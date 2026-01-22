from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import text

from app.db import get_db, DB_URL, engine
from app.deps_auth import get_current_user
from app.models_user import User
from app.schemas_auth import LoginRequest, TokenResponse, UserCreate, UserPublic
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/_debug_users")
def debug_users(db: Session = Depends(get_db)):
    """Dev-only helper to confirm what the auth layer sees."""
    users = db.query(User.id, User.email).order_by(User.id).all()
    try:
        with engine.connect() as conn:
            db_list = conn.execute(text("PRAGMA database_list")).fetchall()
        db_list = [list(r) for r in db_list]
    except Exception as e:
        db_list = {"error": str(e)}

    return {
        "db_url": DB_URL,
        "engine_database_list": db_list,
        "users": [[u[0], u[1]] for u in users],
    }


@router.post("/register", response_model=UserPublic, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    # Pre-check (if this triggers, we'll say so explicitly)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Email already registered (precheck). user_id={existing.id}",
        )

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError:
        db.rollback()
        # If this triggers, it means the unique constraint fired
        raise HTTPException(
            status_code=409,
            detail="Email already registered (unique constraint).",
        )

    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB operational error: {e}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    try:
        user = db.query(User).filter(User.email == email).first()
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=f"DB operational error: {e}")

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user

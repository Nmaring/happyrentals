from __future__ import annotations
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.saas.db import get_db
from app.saas import models
from app.saas.auth import hash_password, verify_password, create_token
from app.saas.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
COOKIE_NAME = "hr_token"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class BootstrapIn(BaseModel):
    org_name: str
    email: EmailStr
    password: str

def _set_cookie(resp: Response, token: str):
    resp.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60*60*24*30,
    )

@router.post("/bootstrap")
def bootstrap(payload: BootstrapIn, resp: Response, db: Session = Depends(get_db)):
    if db.query(models.User).count() > 0:
        raise HTTPException(status_code=409, detail="Already bootstrapped")

    org = models.Organization(name=payload.org_name)
    db.add(org); db.commit(); db.refresh(org)

    user = models.User(
        org_id=org.id,
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
        role="owner",
        is_active=True,
    )
    db.add(user); db.commit(); db.refresh(user)

    sub = models.Subscription(org_id=org.id, plan_type="per_unit", status="trialing", trial_ends_at=datetime.utcnow()+timedelta(days=14))
    db.add(sub); db.commit()

    tok = create_token(user.id, org.id, user.role)
    _set_cookie(resp, tok)
    return {"access_token": tok, "token_type": "bearer"}

@router.post("/login")
def login(payload: LoginIn, resp: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == str(payload.email).lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account not active")

    tok = create_token(user.id, user.org_id, user.role)
    _set_cookie(resp, tok)
    return {"access_token": tok, "token_type": "bearer"}

@router.post("/logout")
def logout(resp: Response):
    resp.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role, "org_id": user.org_id}

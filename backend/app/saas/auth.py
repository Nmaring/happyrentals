from __future__ import annotations
import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-now")
JWT_ALG = "HS256"

def hash_password(pw: str) -> str:
    return pwd.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return pwd.verify(pw, hashed)
    except Exception:
        return False

def create_token(user_id: int, org_id: int, role: str) -> str:
    exp = datetime.utcnow() + timedelta(days=30)
    payload = {"sub": str(user_id), "org_id": org_id, "role": role, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

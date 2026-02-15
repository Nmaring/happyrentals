from __future__ import annotations

from fastapi import Depends, HTTPException
from app.saas.deps import get_current_user

def require_not_tenant(user=Depends(get_current_user)):
    if getattr(user, "role", "") == "tenant":
        raise HTTPException(status_code=403, detail="Tenant role cannot access this resource")
    return user

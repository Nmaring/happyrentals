from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Compatible style for modern FastAPI/pydantic
try:
    from pydantic import ConfigDict  # pydantic v2
    _V2 = True
except Exception:
    ConfigDict = None
    _V2 = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    if _V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

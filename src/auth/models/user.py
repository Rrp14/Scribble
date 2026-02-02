from datetime import datetime
import re
from pydantic import BaseModel, EmailStr, field_validator, SecretStr


class UserCreate(BaseModel):
    email:EmailStr
    password:str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, passwd: str):

        if len(passwd) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", passwd):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", passwd):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", passwd):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[@$!%*?&]", passwd):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")

        return passwd


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id:str
    email:EmailStr
    created_at:datetime


class RefreshTokenRequest(BaseModel):
    refresh_token:str

class LogoutRequest(BaseModel):
    refresh_token:str



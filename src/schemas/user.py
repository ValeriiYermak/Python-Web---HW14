from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

from src.entity.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=18)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str | None
    role: Role

    class Config: frozen = False


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr

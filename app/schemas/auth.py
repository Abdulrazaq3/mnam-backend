from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
    success: bool = True

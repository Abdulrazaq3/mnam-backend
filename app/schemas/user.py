from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """أدوار المستخدمين - يجب أن تتطابق مع models/user.py"""
    SYSTEM_OWNER = "system_owner"
    ADMIN = "admin"
    OWNERS_AGENT = "owners_agent"
    CUSTOMERS_AGENT = "customers_agent"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMERS_AGENT


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_system_owner: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    hashed_password: str


class AssignableRoleResponse(BaseModel):
    """الأدوار المتاحة للتعيين"""
    value: str
    label: str

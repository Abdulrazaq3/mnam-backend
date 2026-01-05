from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OwnerBase(BaseModel):
    owner_name: str
    owner_mobile_phone: str
    paypal_email: Optional[str] = None
    note: Optional[str] = None


class OwnerCreate(OwnerBase):
    pass


class OwnerUpdate(BaseModel):
    owner_name: Optional[str] = None
    owner_mobile_phone: Optional[str] = None
    paypal_email: Optional[str] = None
    note: Optional[str] = None


class OwnerResponse(OwnerBase):
    id: str
    created_at: datetime
    updated_at: datetime
    project_count: int = 0
    unit_count: int = 0
    
    class Config:
        from_attributes = True


class OwnerSimple(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True

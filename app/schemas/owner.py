from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OwnerContractStatus(str, Enum):
    ACTIVE = "ساري"
    EXPIRED = "منتهي"
    PENDING = "قيد التوقيع"


class OwnerBase(BaseModel):
    owner_name: str
    owner_mobile_phone: str
    contract_no: Optional[str] = None
    commission_percent: Decimal = Decimal("0")
    contract_status: OwnerContractStatus = OwnerContractStatus.PENDING
    contract_duration: Optional[str] = None
    paypal_email: Optional[str] = None
    bank_iban: Optional[str] = None
    bank_name: Optional[str] = None
    note: Optional[str] = None


class OwnerCreate(OwnerBase):
    pass


class OwnerUpdate(BaseModel):
    owner_name: Optional[str] = None
    owner_mobile_phone: Optional[str] = None
    contract_no: Optional[str] = None
    commission_percent: Optional[Decimal] = None
    contract_status: Optional[OwnerContractStatus] = None
    contract_duration: Optional[str] = None
    paypal_email: Optional[str] = None
    bank_iban: Optional[str] = None
    bank_name: Optional[str] = None
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

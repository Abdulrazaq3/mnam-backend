from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class UnitType(str, Enum):
    APARTMENT = "شقة"
    STUDIO = "استوديو"
    VILLA = "فيلا"
    CHALET = "شاليه"
    FARMHOUSE = "بيت ريفي"
    REST_HOUSE = "استراحة"
    CARAVAN = "كرفان"
    CAMP = "مخيم"
    DUPLEX = "دوبلكس"
    TOWNHOUSE = "تاون هاوس"


class UnitStatus(str, Enum):
    AVAILABLE = "متاحة"
    BOOKED = "محجوزة"
    CLEANING = "تحتاج تنظيف"
    MAINTENANCE = "صيانة"
    HIDDEN = "مخفية"


class UnitBase(BaseModel):
    project_id: str
    unit_name: str
    unit_type: UnitType = UnitType.APARTMENT
    rooms: int = 1
    floor_number: int = 0
    unit_area: float = 0
    status: UnitStatus = UnitStatus.AVAILABLE
    price_days_of_week: Decimal = Decimal("0")
    price_in_weekends: Decimal = Decimal("0")
    amenities: List[str] = []
    description: Optional[str] = None


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    project_id: Optional[str] = None
    unit_name: Optional[str] = None
    unit_type: Optional[UnitType] = None
    rooms: Optional[int] = None
    floor_number: Optional[int] = None
    unit_area: Optional[float] = None
    status: Optional[UnitStatus] = None
    price_days_of_week: Optional[Decimal] = None
    price_in_weekends: Optional[Decimal] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None


class UnitResponse(UnitBase):
    id: str
    project_name: str = ""
    owner_name: str = ""
    city: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UnitSimple(BaseModel):
    unit_name: str
    unit_type: str
    rooms: int
    price_days_of_week: Decimal
    price_in_weekends: Decimal
    status: str


class UnitForSelect(BaseModel):
    id: str
    unit_name: str
    price_days_of_week: Decimal
    price_in_weekends: Decimal
    
    class Config:
        from_attributes = True

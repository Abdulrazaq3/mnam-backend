from pydantic import BaseModel, EmailStr
from typing import Optional, List, TYPE_CHECKING, Any, Literal
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    """أنواع الجنس"""
    MALE = "male"  # ذكر
    FEMALE = "female"  # أنثى


class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None  # البريد الإلكتروني (اختياري)
    gender: Optional[GenderEnum] = None  # الجنس (اختياري)
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None  # البريد الإلكتروني
    gender: Optional[GenderEnum] = None  # الجنس
    notes: Optional[str] = None
    is_banned: Optional[bool] = None
    ban_reason: Optional[str] = None


class CustomerBanUpdate(BaseModel):
    is_banned: bool
    ban_reason: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: str
    booking_count: int = 0
    completed_booking_count: int = 0  # عدد الحجوزات المكتملة
    total_revenue: float = 0.0  # إجمالي الإيراد
    is_banned: bool = False
    ban_reason: Optional[str] = None
    is_profile_complete: bool = False  # هل البيانات مكتملة
    visitor_type: str = "عادي"  # نوع الزائر: مميز / عادي
    customer_status: str = "new"  # حالة العميل: new / old
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CustomerWithBookings(CustomerResponse):
    """العميل مع قائمة حجوزاته"""
    bookings: List[Any] = []


class CustomerStatsResponse(BaseModel):
    """إحصائيات العملاء"""
    total_customers: int = 0
    new_customers: int = 0  # العملاء الجدد (أقل من أسبوعين)
    old_customers: int = 0  # العملاء القدامى (أكثر من أسبوعين)
    vip_customers: int = 0  # العملاء المميزين (زيارتين أو أكثر)
    regular_customers: int = 0  # العملاء العاديين (زيارة واحدة)
    complete_profiles: int = 0  # البيانات المكتملة
    incomplete_profiles: int = 0  # البيانات الغير مكتملة
    total_revenue: float = 0.0  # إجمالي الإيرادات من جميع العملاء


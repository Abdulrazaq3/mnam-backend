from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "دخل"
    EXPENSE = "صرف"


class TransactionBase(BaseModel):
    project_id: str
    unit_id: Optional[str] = None
    description: str
    date: date
    amount: Decimal
    type: TransactionType
    category: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    project_id: Optional[str] = None
    unit_id: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    amount: Optional[Decimal] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    project_name: str = ""
    unit_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FinancialSummary(BaseModel):
    total_income: Decimal = Decimal("0")
    total_expense: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")


class DailyChallenge(BaseModel):
    """تحدي اليوم"""
    unit_occupancy: int = 0  # إشغال الوحدات
    guest_nights: int = 0  # ليالي الضيوف
    today_income: Decimal = Decimal("0")  # دخل اليوم
    total_cancellations: int = 0  # إجمالي الإلغاءات


class WeeklyPerformance(BaseModel):
    """أداء الأسبوع"""
    total_nights: int = 0  # إجمالي الليالي
    weekly_occupancy_rate: float = 0.0  # نسبة الإشغال الأسبوعي
    revenue_collection: Decimal = Decimal("0")  # تحصيل الإيرادات
    total_cancellations: int = 0  # إجمالي الإلغاءات


class MonthlyHarvest(BaseModel):
    """الحصاد الشهري"""
    monthly_occupancy_rate: float = 0.0  # معدل الإشغال الشهري
    nights_sales: int = 0  # مبيعات الليالي
    project_income: Decimal = Decimal("0")  # دخل المشاريع
    total_cancellations: int = 0  # إجمالي الإلغاء


class TeamAchievement(BaseModel):
    """رحلة إنجاز الفريق"""
    daily_challenge: DailyChallenge = DailyChallenge()
    weekly_performance: WeeklyPerformance = WeeklyPerformance()
    monthly_harvest: MonthlyHarvest = MonthlyHarvest()


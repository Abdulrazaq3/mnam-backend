"""
Schemas لنظام تتبع أداء الموظفين
Employee Performance Tracking Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ======== Enums ========

class ActivityTypeEnum(str, Enum):
    """أنواع الأنشطة"""
    BOOKING_CREATED = "booking_created"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_COMPLETED = "booking_completed"
    BOOKING_CHECKED_IN = "booking_checked_in"
    BOOKING_CHECKED_OUT = "booking_checked_out"
    CUSTOMER_CREATED = "customer_created"
    CUSTOMER_UPDATED = "customer_updated"
    CUSTOMER_BANNED = "customer_banned"
    CUSTOMER_UNBANNED = "customer_unbanned"
    OWNER_CREATED = "owner_created"
    OWNER_UPDATED = "owner_updated"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    UNIT_CREATED = "unit_created"
    UNIT_UPDATED = "unit_updated"
    UNIT_STATUS_CHANGED = "unit_status_changed"
    TRANSACTION_CREATED = "transaction_created"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    TARGET_SET = "target_set"


class TargetPeriodEnum(str, Enum):
    """فترات الأهداف"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ======== Activity Log Schemas ========

class ActivityLogBase(BaseModel):
    activity_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: Optional[str] = None
    amount: float = 0


class ActivityLogCreate(ActivityLogBase):
    employee_id: str
    metadata_json: Optional[str] = None


class ActivityLogResponse(ActivityLogBase):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityLogListResponse(BaseModel):
    """قائمة الأنشطة مع الإحصائيات"""
    activities: List[ActivityLogResponse]
    total_count: int
    page: int
    page_size: int


# ======== Employee Target Schemas ========

class EmployeeTargetBase(BaseModel):
    period: str = TargetPeriodEnum.MONTHLY.value
    start_date: date
    end_date: date
    
    # أهداف وكيل العملاء
    target_bookings: int = 0
    target_booking_revenue: float = 0
    target_new_customers: int = 0
    target_completion_rate: float = 0
    
    # أهداف وكيل الملاك
    target_new_owners: int = 0
    target_new_projects: int = 0
    target_new_units: int = 0
    
    notes: Optional[str] = None


class EmployeeTargetCreate(EmployeeTargetBase):
    employee_id: str


class EmployeeTargetUpdate(BaseModel):
    target_bookings: Optional[int] = None
    target_booking_revenue: Optional[float] = None
    target_new_customers: Optional[int] = None
    target_completion_rate: Optional[float] = None
    target_new_owners: Optional[int] = None
    target_new_projects: Optional[int] = None
    target_new_units: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeTargetResponse(EmployeeTargetBase):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    set_by_id: Optional[str] = None
    set_by_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======== Performance Summary Schemas ========

class PerformanceSummaryBase(BaseModel):
    period_type: str
    period_start: date
    period_end: date
    
    # إحصائيات الحجوزات
    total_bookings_created: int = 0
    total_bookings_completed: int = 0
    total_bookings_cancelled: int = 0
    total_booking_revenue: float = 0
    completion_rate: float = 0
    
    # إحصائيات العملاء
    new_customers_added: int = 0
    customers_banned: int = 0
    
    # إحصائيات الملاك
    new_owners_added: int = 0
    new_projects_created: int = 0
    new_units_added: int = 0
    
    # إحصائيات عامة
    total_activities: int = 0
    target_achievement_rate: float = 0


class PerformanceSummaryResponse(PerformanceSummaryBase):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ======== KPI Schemas ========

class KPIValue(BaseModel):
    """قيمة مؤشر أداء واحد"""
    kpi_key: str
    name_ar: str
    description: str
    current_value: float
    target_value: float
    achievement_rate: float  # نسبة التحقيق (%)
    unit: str
    trend: Optional[str] = None  # up, down, stable


class EmployeeKPIsResponse(BaseModel):
    """مؤشرات أداء موظف"""
    employee_id: str
    employee_name: str
    role: str
    period: str
    period_start: date
    period_end: date
    kpis: List[KPIValue]
    overall_achievement_rate: float


# ======== Employee Dashboard Schemas ========

class EmployeeActivitySummary(BaseModel):
    """ملخص أنشطة موظف"""
    today_activities: int
    week_activities: int
    month_activities: int
    last_activity_at: Optional[datetime] = None


class CustomerAgentStats(BaseModel):
    """إحصائيات وكيل العملاء"""
    # اليوم
    today_bookings: int = 0
    today_revenue: float = 0
    today_customers: int = 0
    
    # الأسبوع
    week_bookings: int = 0
    week_revenue: float = 0
    week_customers: int = 0
    week_completed: int = 0
    week_cancelled: int = 0
    
    # الشهر
    month_bookings: int = 0
    month_revenue: float = 0
    month_customers: int = 0
    month_completion_rate: float = 0


class OwnersAgentStats(BaseModel):
    """إحصائيات وكيل الملاك"""
    # اليوم
    today_owners: int = 0
    today_projects: int = 0
    today_units: int = 0
    
    # الأسبوع
    week_owners: int = 0
    week_projects: int = 0
    week_units: int = 0
    
    # الشهر
    month_owners: int = 0
    month_projects: int = 0
    month_units: int = 0


class EmployeeDashboardResponse(BaseModel):
    """لوحة تحكم الموظف"""
    employee_id: str
    employee_name: str
    role: str
    
    # ملخص الأنشطة
    activity_summary: EmployeeActivitySummary
    
    # الإحصائيات حسب الدور
    customer_agent_stats: Optional[CustomerAgentStats] = None
    owners_agent_stats: Optional[OwnersAgentStats] = None
    
    # الأهداف الحالية
    current_target: Optional[EmployeeTargetResponse] = None
    target_achievement_rate: float = 0
    
    # آخر الأنشطة
    recent_activities: List[ActivityLogResponse] = []


# ======== Admin Dashboard Schemas ========

class EmployeePerformanceCard(BaseModel):
    """بطاقة أداء موظف (للمدير)"""
    employee_id: str
    employee_name: str
    role: str
    role_label: str
    is_active: bool
    
    # إحصائيات سريعة
    today_activities: int = 0
    week_activities: int = 0
    month_activities: int = 0
    
    # نسبة تحقيق الهدف
    target_achievement_rate: float = 0
    
    # أهم الإنجازات (حسب الدور)
    key_metric_label: str = ""
    key_metric_value: float = 0
    key_metric_target: float = 0


class TeamPerformanceOverview(BaseModel):
    """نظرة عامة على أداء الفريق"""
    total_employees: int
    active_employees: int
    
    # إحصائيات الفريق
    team_total_activities_today: int = 0
    team_total_activities_week: int = 0
    team_total_activities_month: int = 0
    
    # متوسط تحقيق الأهداف
    average_target_achievement: float = 0
    
    # أفضل الموظفين
    top_performers: List[EmployeePerformanceCard] = []
    
    # قائمة جميع الموظفين
    all_employees: List[EmployeePerformanceCard] = []


class SetTargetRequest(BaseModel):
    """طلب تحديد هدف لموظف"""
    employee_id: str
    period: str = TargetPeriodEnum.MONTHLY.value
    start_date: date
    end_date: date
    
    # الأهداف (يتم تحديدها حسب الدور)
    target_bookings: Optional[int] = None
    target_booking_revenue: Optional[float] = None
    target_new_customers: Optional[int] = None
    target_completion_rate: Optional[float] = None
    target_new_owners: Optional[int] = None
    target_new_projects: Optional[int] = None
    target_new_units: Optional[int] = None
    
    notes: Optional[str] = None

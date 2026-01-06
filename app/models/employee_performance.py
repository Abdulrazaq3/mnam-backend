"""
نظام تتبع أداء الموظفين
Employee Performance Tracking System
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class ActivityType(str, enum.Enum):
    """أنواع الأنشطة"""
    # أنشطة الحجوزات (Customers Agent)
    BOOKING_CREATED = "booking_created"          # إنشاء حجز
    BOOKING_UPDATED = "booking_updated"          # تعديل حجز
    BOOKING_CANCELLED = "booking_cancelled"      # إلغاء حجز
    BOOKING_COMPLETED = "booking_completed"      # إتمام حجز
    BOOKING_CHECKED_IN = "booking_checked_in"    # تسجيل دخول
    BOOKING_CHECKED_OUT = "booking_checked_out"  # تسجيل خروج
    
    # أنشطة العملاء (Customers Agent)
    CUSTOMER_CREATED = "customer_created"        # إضافة عميل
    CUSTOMER_UPDATED = "customer_updated"        # تعديل عميل
    CUSTOMER_BANNED = "customer_banned"          # حظر عميل
    CUSTOMER_UNBANNED = "customer_unbanned"      # إلغاء حظر عميل
    
    # أنشطة الملاك (Owners Agent)
    OWNER_CREATED = "owner_created"              # إضافة مالك
    OWNER_UPDATED = "owner_updated"              # تعديل مالك
    PROJECT_CREATED = "project_created"          # إنشاء مشروع
    PROJECT_UPDATED = "project_updated"          # تعديل مشروع
    UNIT_CREATED = "unit_created"                # إضافة وحدة
    UNIT_UPDATED = "unit_updated"                # تعديل وحدة
    UNIT_STATUS_CHANGED = "unit_status_changed"  # تغيير حالة وحدة
    
    # أنشطة مالية (General)
    TRANSACTION_CREATED = "transaction_created"  # إضافة معاملة مالية
    
    # أنشطة إدارية (Admin)
    USER_CREATED = "user_created"                # إضافة موظف
    USER_UPDATED = "user_updated"                # تعديل موظف
    USER_DEACTIVATED = "user_deactivated"        # تعطيل موظف
    TARGET_SET = "target_set"                    # تحديد هدف


# تصنيف الأنشطة حسب الدور
ACTIVITY_BY_ROLE = {
    "customers_agent": [
        ActivityType.BOOKING_CREATED, ActivityType.BOOKING_UPDATED, ActivityType.BOOKING_CANCELLED,
        ActivityType.BOOKING_COMPLETED, ActivityType.BOOKING_CHECKED_IN, ActivityType.BOOKING_CHECKED_OUT,
        ActivityType.CUSTOMER_CREATED, ActivityType.CUSTOMER_UPDATED, ActivityType.CUSTOMER_BANNED,
        ActivityType.CUSTOMER_UNBANNED
    ],
    "owners_agent": [
        ActivityType.OWNER_CREATED, ActivityType.OWNER_UPDATED,
        ActivityType.PROJECT_CREATED, ActivityType.PROJECT_UPDATED,
        ActivityType.UNIT_CREATED, ActivityType.UNIT_UPDATED, ActivityType.UNIT_STATUS_CHANGED
    ],
    "admin": [
        ActivityType.USER_CREATED, ActivityType.USER_UPDATED, ActivityType.USER_DEACTIVATED,
        ActivityType.TARGET_SET, ActivityType.TRANSACTION_CREATED
    ]
}


# تسميات الأنشطة بالعربية
ACTIVITY_LABELS = {
    ActivityType.BOOKING_CREATED: "إنشاء حجز",
    ActivityType.BOOKING_UPDATED: "تعديل حجز",
    ActivityType.BOOKING_CANCELLED: "إلغاء حجز",
    ActivityType.BOOKING_COMPLETED: "إتمام حجز",
    ActivityType.BOOKING_CHECKED_IN: "تسجيل دخول",
    ActivityType.BOOKING_CHECKED_OUT: "تسجيل خروج",
    ActivityType.CUSTOMER_CREATED: "إضافة عميل",
    ActivityType.CUSTOMER_UPDATED: "تعديل عميل",
    ActivityType.CUSTOMER_BANNED: "حظر عميل",
    ActivityType.CUSTOMER_UNBANNED: "إلغاء حظر",
    ActivityType.OWNER_CREATED: "إضافة مالك",
    ActivityType.OWNER_UPDATED: "تعديل مالك",
    ActivityType.PROJECT_CREATED: "إنشاء مشروع",
    ActivityType.PROJECT_UPDATED: "تعديل مشروع",
    ActivityType.UNIT_CREATED: "إضافة وحدة",
    ActivityType.UNIT_UPDATED: "تعديل وحدة",
    ActivityType.UNIT_STATUS_CHANGED: "تغيير حالة وحدة",
    ActivityType.TRANSACTION_CREATED: "معاملة مالية",
    ActivityType.USER_CREATED: "إضافة موظف",
    ActivityType.USER_UPDATED: "تعديل موظف",
    ActivityType.USER_DEACTIVATED: "تعطيل موظف",
    ActivityType.TARGET_SET: "تحديد هدف",
}


class EmployeeActivityLog(Base):
    """
    سجل أنشطة الموظفين
    يتتبع كل عملية يقوم بها الموظف في النظام
    """
    __tablename__ = "employee_activity_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # الموظف الذي قام بالعملية
    employee_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # نوع النشاط
    activity_type = Column(String(50), nullable=False, index=True)
    
    # تفاصيل النشاط
    entity_type = Column(String(50), nullable=True)  # نوع الكيان (booking, customer, owner, etc)
    entity_id = Column(String(36), nullable=True)    # معرف الكيان
    description = Column(Text, nullable=True)        # وصف تفصيلي
    
    # القيمة المالية المرتبطة (إن وجدت)
    amount = Column(Float, default=0)
    
    # البيانات الإضافية (JSON string)
    metadata_json = Column(Text, nullable=True)
    
    # التوقيت
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # العلاقات
    employee = relationship("User", foreign_keys=[employee_id])
    
    def __repr__(self):
        return f"<Activity {self.activity_type} by {self.employee_id}>"


class TargetPeriod(str, enum.Enum):
    """فترات الأهداف"""
    DAILY = "daily"        # يومي
    WEEKLY = "weekly"      # أسبوعي
    MONTHLY = "monthly"    # شهري


class EmployeeTarget(Base):
    """
    أهداف الموظفين
    الأهداف التي يحددها المدير لكل موظف
    """
    __tablename__ = "employee_targets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # الموظف المستهدف
    employee_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # فترة الهدف
    period = Column(String(20), default=TargetPeriod.MONTHLY.value)
    
    # تاريخ بداية ونهاية الهدف
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # -------- أهداف وكيل العملاء (Customers Agent) --------
    # عدد الحجوزات المطلوبة
    target_bookings = Column(Integer, default=0)
    # إيرادات الحجوزات المطلوبة
    target_booking_revenue = Column(Float, default=0)
    # عدد العملاء الجدد
    target_new_customers = Column(Integer, default=0)
    # نسبة إتمام الحجوزات (%)
    target_completion_rate = Column(Float, default=0)
    
    # -------- أهداف وكيل الملاك (Owners Agent) --------
    # عدد الملاك الجدد
    target_new_owners = Column(Integer, default=0)
    # عدد المشاريع الجديدة
    target_new_projects = Column(Integer, default=0)
    # عدد الوحدات الجديدة
    target_new_units = Column(Integer, default=0)
    
    # -------- أهداف عامة --------
    # ملاحظات من المدير
    notes = Column(Text, nullable=True)
    
    # من قام بتحديد الهدف
    set_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # الحالة
    is_active = Column(Boolean, default=True)
    
    # التواريخ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    employee = relationship("User", foreign_keys=[employee_id])
    set_by = relationship("User", foreign_keys=[set_by_id])
    
    def __repr__(self):
        return f"<Target for {self.employee_id} - {self.period}>"


class EmployeePerformanceSummary(Base):
    """
    ملخص أداء الموظفين
    يحتوي على الإحصائيات المجمعة لكل فترة
    """
    __tablename__ = "employee_performance_summaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # الموظف
    employee_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # الفترة
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False)
    
    # -------- إحصائيات الحجوزات --------
    total_bookings_created = Column(Integer, default=0)      # إجمالي الحجوزات
    total_bookings_completed = Column(Integer, default=0)    # الحجوزات المكتملة
    total_bookings_cancelled = Column(Integer, default=0)    # الحجوزات الملغية
    total_booking_revenue = Column(Float, default=0)         # إيرادات الحجوزات
    completion_rate = Column(Float, default=0)               # نسبة الإتمام (%)
    
    # -------- إحصائيات العملاء --------
    new_customers_added = Column(Integer, default=0)         # عملاء جدد
    customers_banned = Column(Integer, default=0)            # عملاء محظورين
    
    # -------- إحصائيات الملاك --------
    new_owners_added = Column(Integer, default=0)            # ملاك جدد
    new_projects_created = Column(Integer, default=0)        # مشاريع جديدة
    new_units_added = Column(Integer, default=0)             # وحدات جديدة
    
    # -------- إحصائيات عامة --------
    total_activities = Column(Integer, default=0)            # إجمالي الأنشطة
    average_response_time = Column(Float, default=0)         # متوسط وقت الاستجابة (بالدقائق)
    
    # -------- نسب تحقيق الأهداف --------
    target_achievement_rate = Column(Float, default=0)       # نسبة تحقيق الهدف العام (%)
    
    # التواريخ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    employee = relationship("User", foreign_keys=[employee_id])
    
    def __repr__(self):
        return f"<Performance {self.employee_id} - {self.period_start}>"


# ======== مؤشرات الأداء الرئيسية (KPIs) ========

class KPIDefinition:
    """تعريفات مؤشرات الأداء لكل رتبة"""
    
    CUSTOMERS_AGENT_KPIS = {
        "bookings_created": {
            "name_ar": "عدد الحجوزات",
            "description": "إجمالي الحجوزات التي أنشأها الموظف",
            "unit": "حجز",
            "target_type": "count"
        },
        "booking_revenue": {
            "name_ar": "إيرادات الحجوزات",
            "description": "إجمالي الإيرادات من الحجوزات",
            "unit": "ر.س",
            "target_type": "currency"
        },
        "completion_rate": {
            "name_ar": "نسبة إتمام الحجوزات",
            "description": "نسبة الحجوزات المكتملة من إجمالي الحجوزات",
            "unit": "%",
            "target_type": "percentage"
        },
        "cancellation_rate": {
            "name_ar": "نسبة الإلغاء",
            "description": "نسبة الحجوزات الملغية (يجب أن تكون منخفضة)",
            "unit": "%",
            "target_type": "percentage",
            "lower_is_better": True
        },
        "new_customers": {
            "name_ar": "العملاء الجدد",
            "description": "عدد العملاء الجدد المضافين",
            "unit": "عميل",
            "target_type": "count"
        },
        "average_booking_value": {
            "name_ar": "متوسط قيمة الحجز",
            "description": "متوسط قيمة الحجز الواحد",
            "unit": "ر.س",
            "target_type": "currency"
        }
    }
    
    OWNERS_AGENT_KPIS = {
        "new_owners": {
            "name_ar": "الملاك الجدد",
            "description": "عدد الملاك الجدد المضافين",
            "unit": "مالك",
            "target_type": "count"
        },
        "new_projects": {
            "name_ar": "المشاريع الجديدة",
            "description": "عدد المشاريع الجديدة المنشأة",
            "unit": "مشروع",
            "target_type": "count"
        },
        "new_units": {
            "name_ar": "الوحدات الجديدة",
            "description": "عدد الوحدات الجديدة المضافة",
            "unit": "وحدة",
            "target_type": "count"
        },
        "units_occupancy_rate": {
            "name_ar": "نسبة إشغال الوحدات",
            "description": "نسبة الوحدات المحجوزة من إجمالي الوحدات",
            "unit": "%",
            "target_type": "percentage"
        },
        "owner_retention_rate": {
            "name_ar": "نسبة الاحتفاظ بالملاك",
            "description": "نسبة الملاك النشطين من إجمالي الملاك",
            "unit": "%",
            "target_type": "percentage"
        }
    }
    
    ADMIN_KPIS = {
        "team_productivity": {
            "name_ar": "إنتاجية الفريق",
            "description": "إجمالي أنشطة جميع الموظفين",
            "unit": "نشاط",
            "target_type": "count"
        },
        "target_achievement_rate": {
            "name_ar": "نسبة تحقيق الأهداف",
            "description": "نسبة تحقيق الأهداف لجميع الموظفين",
            "unit": "%",
            "target_type": "percentage"
        },
        "employee_satisfaction": {
            "name_ar": "رضا الموظفين",
            "description": "مؤشر رضا الموظفين (إذا متوفر)",
            "unit": "نقطة",
            "target_type": "score"
        }
    }
    
    @classmethod
    def get_kpis_for_role(cls, role: str) -> dict:
        """الحصول على KPIs حسب الرتبة"""
        if role == "customers_agent":
            return cls.CUSTOMERS_AGENT_KPIS
        elif role == "owners_agent":
            return cls.OWNERS_AGENT_KPIS
        elif role in ["admin", "system_owner"]:
            return {**cls.ADMIN_KPIS, **cls.CUSTOMERS_AGENT_KPIS, **cls.OWNERS_AGENT_KPIS}
        return {}

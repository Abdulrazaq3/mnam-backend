"""
خدمة تتبع أداء الموظفين
Employee Performance Tracking Service
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json

from ..models.employee_performance import (
    EmployeeActivityLog, EmployeeTarget, EmployeePerformanceSummary,
    ActivityType, TargetPeriod, ACTIVITY_LABELS, KPIDefinition
)
from ..models.user import User, UserRole, ROLE_LABELS
from ..models.booking import Booking
from ..models.customer import Customer
from ..models.owner import Owner
from ..models.project import Project
from ..models.unit import Unit


class EmployeePerformanceService:
    """خدمة تتبع أداء الموظفين"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ======== تسجيل الأنشطة ========
    
    def log_activity(
        self,
        employee_id: str,
        activity_type: ActivityType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        description: Optional[str] = None,
        amount: float = 0,
        metadata: Optional[Dict] = None
    ) -> EmployeeActivityLog:
        """تسجيل نشاط جديد للموظف"""
        activity = EmployeeActivityLog(
            employee_id=employee_id,
            activity_type=activity_type.value,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description or ACTIVITY_LABELS.get(activity_type, ""),
            amount=amount,
            metadata_json=json.dumps(metadata) if metadata else None
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    # ======== الحصول على الأنشطة ========
    
    def get_employee_activities(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        activity_types: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """الحصول على أنشطة موظف معين"""
        query = self.db.query(EmployeeActivityLog).filter(
            EmployeeActivityLog.employee_id == employee_id
        )
        
        if start_date:
            query = query.filter(EmployeeActivityLog.created_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(EmployeeActivityLog.created_at <= datetime.combine(end_date, datetime.max.time()))
        if activity_types:
            query = query.filter(EmployeeActivityLog.activity_type.in_(activity_types))
        
        total = query.count()
        activities = query.order_by(EmployeeActivityLog.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return {
            "activities": activities,
            "total_count": total,
            "page": page,
            "page_size": page_size
        }
    
    def get_all_activities(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        role: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict:
        """الحصول على جميع الأنشطة (للمدير)"""
        query = self.db.query(EmployeeActivityLog).join(
            User, EmployeeActivityLog.employee_id == User.id
        )
        
        if start_date:
            query = query.filter(EmployeeActivityLog.created_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(EmployeeActivityLog.created_at <= datetime.combine(end_date, datetime.max.time()))
        if role:
            query = query.filter(User.role == role)
        
        total = query.count()
        activities = query.order_by(EmployeeActivityLog.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return {
            "activities": activities,
            "total_count": total,
            "page": page,
            "page_size": page_size
        }
    
    # ======== إحصائيات الأنشطة ========
    
    def get_activity_count(
        self,
        employee_id: str,
        start_date: date,
        end_date: date,
        activity_types: Optional[List[str]] = None
    ) -> int:
        """عدد الأنشطة في فترة معينة"""
        query = self.db.query(func.count(EmployeeActivityLog.id)).filter(
            EmployeeActivityLog.employee_id == employee_id,
            EmployeeActivityLog.created_at >= datetime.combine(start_date, datetime.min.time()),
            EmployeeActivityLog.created_at <= datetime.combine(end_date, datetime.max.time())
        )
        
        if activity_types:
            query = query.filter(EmployeeActivityLog.activity_type.in_(activity_types))
        
        return query.scalar() or 0
    
    def get_activity_revenue(
        self,
        employee_id: str,
        start_date: date,
        end_date: date,
        activity_types: Optional[List[str]] = None
    ) -> float:
        """إجمالي الإيرادات من الأنشطة"""
        query = self.db.query(func.sum(EmployeeActivityLog.amount)).filter(
            EmployeeActivityLog.employee_id == employee_id,
            EmployeeActivityLog.created_at >= datetime.combine(start_date, datetime.min.time()),
            EmployeeActivityLog.created_at <= datetime.combine(end_date, datetime.max.time())
        )
        
        if activity_types:
            query = query.filter(EmployeeActivityLog.activity_type.in_(activity_types))
        
        return query.scalar() or 0.0
    
    # ======== إحصائيات وكيل العملاء ========
    
    def get_customer_agent_stats(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """إحصائيات وكيل العملاء"""
        # الحجوزات المنشأة
        bookings_created = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.BOOKING_CREATED.value]
        )
        
        # الحجوزات المكتملة
        bookings_completed = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.BOOKING_COMPLETED.value]
        )
        
        # الحجوزات الملغية
        bookings_cancelled = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.BOOKING_CANCELLED.value]
        )
        
        # إيرادات الحجوزات
        booking_revenue = self.get_activity_revenue(
            employee_id, start_date, end_date,
            [ActivityType.BOOKING_CREATED.value]
        )
        
        # العملاء الجدد
        new_customers = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.CUSTOMER_CREATED.value]
        )
        
        # نسبة الإتمام
        total_final = bookings_completed + bookings_cancelled
        completion_rate = (bookings_completed / total_final * 100) if total_final > 0 else 0
        
        return {
            "bookings_created": bookings_created,
            "bookings_completed": bookings_completed,
            "bookings_cancelled": bookings_cancelled,
            "booking_revenue": booking_revenue,
            "new_customers": new_customers,
            "completion_rate": round(completion_rate, 2)
        }
    
    # ======== إحصائيات وكيل الملاك ========
    
    def get_owners_agent_stats(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """إحصائيات وكيل الملاك"""
        # الملاك الجدد
        new_owners = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.OWNER_CREATED.value]
        )
        
        # المشاريع الجديدة
        new_projects = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.PROJECT_CREATED.value]
        )
        
        # الوحدات الجديدة
        new_units = self.get_activity_count(
            employee_id, start_date, end_date,
            [ActivityType.UNIT_CREATED.value]
        )
        
        return {
            "new_owners": new_owners,
            "new_projects": new_projects,
            "new_units": new_units
        }
    
    # ======== إدارة الأهداف ========
    
    def set_target(
        self,
        employee_id: str,
        set_by_id: str,
        period: str,
        start_date: date,
        end_date: date,
        **target_values
    ) -> EmployeeTarget:
        """تحديد هدف لموظف"""
        # إلغاء الأهداف السابقة النشطة في نفس الفترة
        self.db.query(EmployeeTarget).filter(
            EmployeeTarget.employee_id == employee_id,
            EmployeeTarget.is_active == True,
            EmployeeTarget.end_date >= start_date
        ).update({"is_active": False})
        
        target = EmployeeTarget(
            employee_id=employee_id,
            set_by_id=set_by_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            **target_values
        )
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        
        # تسجيل نشاط تحديد الهدف
        self.log_activity(
            employee_id=set_by_id,
            activity_type=ActivityType.TARGET_SET,
            entity_type="employee_target",
            entity_id=target.id,
            description=f"تحديد هدف للموظف",
            metadata={"target_employee_id": employee_id}
        )
        
        return target
    
    def get_current_target(self, employee_id: str) -> Optional[EmployeeTarget]:
        """الحصول على الهدف الحالي للموظف"""
        today = date.today()
        return self.db.query(EmployeeTarget).filter(
            EmployeeTarget.employee_id == employee_id,
            EmployeeTarget.is_active == True,
            EmployeeTarget.start_date <= today,
            EmployeeTarget.end_date >= today
        ).first()
    
    def calculate_target_achievement(
        self,
        employee_id: str,
        target: EmployeeTarget
    ) -> float:
        """حساب نسبة تحقيق الهدف"""
        employee = self.db.query(User).filter(User.id == employee_id).first()
        if not employee:
            return 0.0
        
        achievements = []
        
        if employee.role == UserRole.CUSTOMERS_AGENT.value:
            stats = self.get_customer_agent_stats(
                employee_id, target.start_date, target.end_date
            )
            
            if target.target_bookings > 0:
                achievements.append(min(stats["bookings_created"] / target.target_bookings * 100, 100))
            if target.target_booking_revenue > 0:
                achievements.append(min(stats["booking_revenue"] / target.target_booking_revenue * 100, 100))
            if target.target_new_customers > 0:
                achievements.append(min(stats["new_customers"] / target.target_new_customers * 100, 100))
            if target.target_completion_rate > 0:
                achievements.append(min(stats["completion_rate"] / target.target_completion_rate * 100, 100))
        
        elif employee.role == UserRole.OWNERS_AGENT.value:
            stats = self.get_owners_agent_stats(
                employee_id, target.start_date, target.end_date
            )
            
            if target.target_new_owners > 0:
                achievements.append(min(stats["new_owners"] / target.target_new_owners * 100, 100))
            if target.target_new_projects > 0:
                achievements.append(min(stats["new_projects"] / target.target_new_projects * 100, 100))
            if target.target_new_units > 0:
                achievements.append(min(stats["new_units"] / target.target_new_units * 100, 100))
        
        if achievements:
            return round(sum(achievements) / len(achievements), 2)
        return 0.0
    
    # ======== لوحة تحكم الموظف ========
    
    def get_employee_dashboard(self, employee_id: str) -> Dict:
        """الحصول على لوحة تحكم الموظف"""
        employee = self.db.query(User).filter(User.id == employee_id).first()
        if not employee:
            return {}
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # ملخص الأنشطة
        activity_summary = {
            "today_activities": self.get_activity_count(employee_id, today, today),
            "week_activities": self.get_activity_count(employee_id, week_start, today),
            "month_activities": self.get_activity_count(employee_id, month_start, today),
            "last_activity_at": self._get_last_activity_time(employee_id)
        }
        
        # إحصائيات حسب الدور
        customer_agent_stats = None
        owners_agent_stats = None
        
        if employee.role == UserRole.CUSTOMERS_AGENT.value:
            customer_agent_stats = {
                "today": self.get_customer_agent_stats(employee_id, today, today),
                "week": self.get_customer_agent_stats(employee_id, week_start, today),
                "month": self.get_customer_agent_stats(employee_id, month_start, today),
            }
        elif employee.role == UserRole.OWNERS_AGENT.value:
            owners_agent_stats = {
                "today": self.get_owners_agent_stats(employee_id, today, today),
                "week": self.get_owners_agent_stats(employee_id, week_start, today),
                "month": self.get_owners_agent_stats(employee_id, month_start, today),
            }
        
        # الهدف الحالي
        current_target = self.get_current_target(employee_id)
        target_achievement = 0.0
        if current_target:
            target_achievement = self.calculate_target_achievement(employee_id, current_target)
        
        # آخر الأنشطة
        recent = self.get_employee_activities(employee_id, page_size=10)
        
        return {
            "employee_id": employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "role": employee.role,
            "role_label": ROLE_LABELS.get(UserRole(employee.role), employee.role),
            "activity_summary": activity_summary,
            "customer_agent_stats": customer_agent_stats,
            "owners_agent_stats": owners_agent_stats,
            "current_target": current_target,
            "target_achievement_rate": target_achievement,
            "recent_activities": recent["activities"]
        }
    
    def _get_last_activity_time(self, employee_id: str) -> Optional[datetime]:
        """الحصول على وقت آخر نشاط"""
        activity = self.db.query(EmployeeActivityLog).filter(
            EmployeeActivityLog.employee_id == employee_id
        ).order_by(EmployeeActivityLog.created_at.desc()).first()
        return activity.created_at if activity else None
    
    # ======== لوحة تحكم المدير ========
    
    def get_team_overview(self, exclude_system_owner: bool = True) -> Dict:
        """نظرة عامة على أداء الفريق"""
        query = self.db.query(User).filter(User.is_active == True)
        if exclude_system_owner:
            query = query.filter(User.is_system_owner == False)
        
        employees = query.all()
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        employee_cards = []
        total_achievements = []
        
        for emp in employees:
            # إحصائيات الأنشطة
            today_acts = self.get_activity_count(emp.id, today, today)
            week_acts = self.get_activity_count(emp.id, week_start, today)
            month_acts = self.get_activity_count(emp.id, month_start, today)
            
            # نسبة تحقيق الهدف
            target = self.get_current_target(emp.id)
            achievement = 0.0
            if target:
                achievement = self.calculate_target_achievement(emp.id, target)
                total_achievements.append(achievement)
            
            # المؤشر الرئيسي حسب الدور
            key_metric = self._get_key_metric(emp, month_start, today)
            
            card = {
                "employee_id": emp.id,
                "employee_name": f"{emp.first_name} {emp.last_name}",
                "role": emp.role,
                "role_label": ROLE_LABELS.get(UserRole(emp.role), emp.role),
                "is_active": emp.is_active,
                "today_activities": today_acts,
                "week_activities": week_acts,
                "month_activities": month_acts,
                "target_achievement_rate": achievement,
                **key_metric
            }
            employee_cards.append(card)
        
        # ترتيب حسب الأداء
        employee_cards.sort(key=lambda x: x["target_achievement_rate"], reverse=True)
        
        # إحصائيات الفريق
        team_today = sum(c["today_activities"] for c in employee_cards)
        team_week = sum(c["week_activities"] for c in employee_cards)
        team_month = sum(c["month_activities"] for c in employee_cards)
        avg_achievement = sum(total_achievements) / len(total_achievements) if total_achievements else 0
        
        return {
            "total_employees": len(employees),
            "active_employees": len([e for e in employees if e.is_active]),
            "team_total_activities_today": team_today,
            "team_total_activities_week": team_week,
            "team_total_activities_month": team_month,
            "average_target_achievement": round(avg_achievement, 2),
            "top_performers": employee_cards[:5],
            "all_employees": employee_cards
        }
    
    def _get_key_metric(self, employee: User, start_date: date, end_date: date) -> Dict:
        """الحصول على المؤشر الرئيسي للموظف"""
        if employee.role == UserRole.CUSTOMERS_AGENT.value:
            stats = self.get_customer_agent_stats(employee.id, start_date, end_date)
            target = self.get_current_target(employee.id)
            return {
                "key_metric_label": "الحجوزات",
                "key_metric_value": stats["bookings_created"],
                "key_metric_target": target.target_bookings if target else 0
            }
        elif employee.role == UserRole.OWNERS_AGENT.value:
            stats = self.get_owners_agent_stats(employee.id, start_date, end_date)
            target = self.get_current_target(employee.id)
            return {
                "key_metric_label": "الوحدات",
                "key_metric_value": stats["new_units"],
                "key_metric_target": target.target_new_units if target else 0
            }
        else:
            return {
                "key_metric_label": "الأنشطة",
                "key_metric_value": self.get_activity_count(employee.id, start_date, end_date),
                "key_metric_target": 0
            }


# ======== دوال مساعدة للتسجيل السريع ========

def log_booking_created(db: Session, employee_id: str, booking_id: str, amount: float):
    """تسجيل إنشاء حجز"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.BOOKING_CREATED,
        entity_type="booking",
        entity_id=booking_id,
        amount=amount
    )


def log_booking_completed(db: Session, employee_id: str, booking_id: str, amount: float):
    """تسجيل إتمام حجز"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.BOOKING_COMPLETED,
        entity_type="booking",
        entity_id=booking_id,
        amount=amount
    )


def log_booking_cancelled(db: Session, employee_id: str, booking_id: str):
    """تسجيل إلغاء حجز"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.BOOKING_CANCELLED,
        entity_type="booking",
        entity_id=booking_id
    )


def log_customer_created(db: Session, employee_id: str, customer_id: str):
    """تسجيل إضافة عميل"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.CUSTOMER_CREATED,
        entity_type="customer",
        entity_id=customer_id
    )


def log_owner_created(db: Session, employee_id: str, owner_id: str):
    """تسجيل إضافة مالك"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.OWNER_CREATED,
        entity_type="owner",
        entity_id=owner_id
    )


def log_project_created(db: Session, employee_id: str, project_id: str):
    """تسجيل إنشاء مشروع"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.PROJECT_CREATED,
        entity_type="project",
        entity_id=project_id
    )


def log_unit_created(db: Session, employee_id: str, unit_id: str):
    """تسجيل إضافة وحدة"""
    service = EmployeePerformanceService(db)
    service.log_activity(
        employee_id=employee_id,
        activity_type=ActivityType.UNIT_CREATED,
        entity_type="unit",
        entity_id=unit_id
    )

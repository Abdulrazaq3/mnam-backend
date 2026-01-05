from pydantic import BaseModel
from typing import List
from decimal import Decimal


class DashboardKpis(BaseModel):
    current_month_revenue: Decimal = Decimal("0")
    current_guests: int = 0
    total_units: int = 0
    # جديد: نسبة الإشغال اليومي
    occupancy_rate: float = 0.0
    booked_units: int = 0
    # جديد: الوحدات تحت التنظيف والصيانة
    cleaning_units: int = 0
    maintenance_units: int = 0


class TodayFocusItem(BaseModel):
    booking_id: str
    guest_name: str
    project_name: str
    unit_name: str


class UpcomingBookingSummary(BaseModel):
    booking_id: str
    guest_name: str
    project_name: str
    unit_name: str
    check_in_date: str
    total_price: Decimal


class TodayFocus(BaseModel):
    arrivals: List[TodayFocusItem] = []
    departures: List[TodayFocusItem] = []
    # جديد: الحجوزات التي لم يتم check-in لها اليوم
    pending_checkins: List[TodayFocusItem] = []


class EmployeePerformance(BaseModel):
    """نسبة إنجاز الموظف"""
    daily_bookings: int = 0
    daily_completed: int = 0
    daily_rate: float = 0.0
    weekly_bookings: int = 0
    weekly_completed: int = 0
    weekly_rate: float = 0.0


class DashboardSummary(BaseModel):
    kpis: DashboardKpis
    today_focus: TodayFocus
    upcoming_bookings: List[UpcomingBookingSummary] = []
    employee_performance: EmployeePerformance = EmployeePerformance()

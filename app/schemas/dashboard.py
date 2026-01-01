from pydantic import BaseModel
from typing import List
from decimal import Decimal


class DashboardKpis(BaseModel):
    current_month_revenue: Decimal = Decimal("0")
    current_guests: int = 0
    total_units: int = 0


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


class DashboardSummary(BaseModel):
    kpis: DashboardKpis
    today_focus: TodayFocus
    upcoming_bookings: List[UpcomingBookingSummary] = []

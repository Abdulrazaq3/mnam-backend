from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from decimal import Decimal
from typing import List

from ..database import get_db
from ..models.booking import Booking
from ..models.unit import Unit
from ..schemas.dashboard import (
    DashboardSummary, DashboardKpis, TodayFocus, 
    TodayFocusItem, UpcomingBookingSummary
)
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["لوحة التحكم"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على ملخص لوحة التحكم"""
    today = date.today()
    now = datetime.now()
    
    # Current month start/end
    month_start = date(now.year, now.month, 1)
    if now.month == 12:
        month_end = date(now.year + 1, 1, 1)
    else:
        month_end = date(now.year, now.month + 1, 1)
    
    # KPIs
    current_month_revenue = db.query(
        func.coalesce(func.sum(Booking.total_price), 0)
    ).filter(
        Booking.check_in_date >= month_start,
        Booking.check_in_date < month_end,
        Booking.status.in_(["مؤكد", "مكتمل"])
    ).scalar() or Decimal("0")
    
    current_guests = db.query(Booking).filter(
        Booking.check_in_date <= today,
        Booking.check_out_date > today,
        Booking.status.in_(["مؤكد"])
    ).count()
    
    total_units = db.query(Unit).count()
    
    kpis = DashboardKpis(
        current_month_revenue=current_month_revenue,
        current_guests=current_guests,
        total_units=total_units
    )
    
    # Today's arrivals
    arrivals = db.query(Booking).filter(
        Booking.check_in_date == today,
        Booking.status.in_(["مؤكد", "قيد الانتظار"])
    ).all()
    
    arrival_items = []
    for b in arrivals:
        unit = b.unit
        project = unit.project if unit else None
        arrival_items.append(TodayFocusItem(
            booking_id=b.id,
            guest_name=b.guest_name,
            project_name=project.name if project else "غير معروف",
            unit_name=unit.unit_name if unit else "غير معروف"
        ))
    
    # Today's departures
    departures = db.query(Booking).filter(
        Booking.check_out_date == today,
        Booking.status.in_(["مؤكد"])
    ).all()
    
    departure_items = []
    for b in departures:
        unit = b.unit
        project = unit.project if unit else None
        departure_items.append(TodayFocusItem(
            booking_id=b.id,
            guest_name=b.guest_name,
            project_name=project.name if project else "غير معروف",
            unit_name=unit.unit_name if unit else "غير معروف"
        ))
    
    today_focus = TodayFocus(
        arrivals=arrival_items,
        departures=departure_items
    )
    
    # Upcoming bookings (next 7 days)
    upcoming = db.query(Booking).filter(
        Booking.check_in_date > today,
        Booking.check_in_date <= date(today.year, today.month, today.day + 7) if today.day <= 24 else date(today.year, today.month + 1 if today.month < 12 else 1, today.day - 24),
        Booking.status.in_(["مؤكد", "قيد الانتظار"])
    ).order_by(Booking.check_in_date).limit(10).all()
    
    upcoming_items = []
    for b in upcoming:
        unit = b.unit
        project = unit.project if unit else None
        upcoming_items.append(UpcomingBookingSummary(
            booking_id=b.id,
            guest_name=b.guest_name,
            project_name=project.name if project else "غير معروف",
            unit_name=unit.unit_name if unit else "غير معروف",
            check_in_date=str(b.check_in_date),
            total_price=b.total_price
        ))
    
    return DashboardSummary(
        kpis=kpis,
        today_focus=today_focus,
        upcoming_bookings=upcoming_items
    )

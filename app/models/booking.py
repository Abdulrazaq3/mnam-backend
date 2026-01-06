import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class BookingStatus(str, enum.Enum):
    CONFIRMED = "مؤكد"
    CANCELLED = "ملغي"
    COMPLETED = "مكتمل"
    CHECKED_IN = "دخول"
    CHECKED_OUT = "خروج"


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id = Column(String(36), ForeignKey("units.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(20), nullable=True)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    total_price = Column(Numeric(10, 2), default=0)
    status = Column(String(30), default=BookingStatus.CONFIRMED.value)
    notes = Column(Text, nullable=True)
    
    # تتبع الموظفين
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    unit = relationship("Unit", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    def __repr__(self):
        return f"<Booking {self.guest_name} - {self.check_in_date}>"


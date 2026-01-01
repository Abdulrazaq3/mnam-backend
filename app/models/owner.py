import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class OwnerContractStatus(str, enum.Enum):
    ACTIVE = "ساري"
    EXPIRED = "منتهي"
    PENDING = "قيد التوقيع"


class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_name = Column(String(100), nullable=False)
    owner_mobile_phone = Column(String(20), nullable=False)
    contract_no = Column(String(50), nullable=True)
    commission_percent = Column(Numeric(5, 2), default=0)
    contract_status = Column(String(20), default=OwnerContractStatus.PENDING.value)
    contract_duration = Column(String(50), nullable=True)
    paypal_email = Column(String(100), nullable=True)
    bank_iban = Column(String(50), nullable=True)
    bank_name = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Owner {self.owner_name}>"

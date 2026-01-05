import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ProjectStatus(str, enum.Enum):
    AVAILABLE = "متاح"
    FULLY_BOOKED = "محجوز بالكامل"
    EMPTY = "فارغ"


class ContractStatus(str, enum.Enum):
    ACTIVE = "ساري"
    EXPIRED = "منتهي"
    PENDING = "قيد التوقيع"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(30), default=ProjectStatus.AVAILABLE.value)
    city = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    security_guard_phone = Column(String(20), nullable=True)
    property_manager_phone = Column(String(20), nullable=True)
    map_url = Column(String(500), nullable=True)
    # حقول العقد (منقولة من الملاك)
    contract_no = Column(String(50), nullable=True)
    contract_status = Column(String(20), default=ContractStatus.PENDING.value)
    contract_duration = Column(String(50), nullable=True)
    commission_percent = Column(Numeric(5, 2), default=0)
    bank_name = Column(String(100), nullable=True)
    bank_iban = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("Owner", back_populates="projects")
    units = relationship("Unit", back_populates="project", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.name}>"

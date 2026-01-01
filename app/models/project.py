import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ProjectStatus(str, enum.Enum):
    AVAILABLE = "متاح"
    FULLY_BOOKED = "محجوز بالكامل"
    EMPTY = "فارغ"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(30), default=ProjectStatus.AVAILABLE.value)
    city = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    permit_no = Column(String(50), nullable=True)
    security_guard_phone = Column(String(20), nullable=True)
    property_manager_phone = Column(String(20), nullable=True)
    map_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("Owner", back_populates="projects")
    units = relationship("Unit", back_populates="project", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.name}>"

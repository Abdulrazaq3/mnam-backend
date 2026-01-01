import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class TransactionType(str, enum.Enum):
    INCOME = "دخل"
    EXPENSE = "صرف"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    unit_id = Column(String(36), ForeignKey("units.id", ondelete="SET NULL"), nullable=True)
    description = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(20), nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="transactions")
    unit = relationship("Unit", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.description} - {self.amount}>"

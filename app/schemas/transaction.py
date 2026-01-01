from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "دخل"
    EXPENSE = "صرف"


class TransactionBase(BaseModel):
    project_id: str
    unit_id: Optional[str] = None
    description: str
    date: date
    amount: Decimal
    type: TransactionType
    category: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    project_id: Optional[str] = None
    unit_id: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    amount: Optional[Decimal] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    project_name: str = ""
    unit_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FinancialSummary(BaseModel):
    total_income: Decimal = Decimal("0")
    total_expense: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")

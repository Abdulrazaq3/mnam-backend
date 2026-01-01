from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from decimal import Decimal

from ..database import get_db
from ..models.transaction import Transaction
from ..models.project import Project
from ..models.unit import Unit
from ..schemas.transaction import TransactionResponse, TransactionCreate, TransactionUpdate, FinancialSummary
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/transactions", tags=["المعاملات المالية"])


@router.get("/", response_model=List[TransactionResponse])
async def get_all_transactions(
    project_id: Optional[str] = None,
    type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على قائمة المعاملات المالية مع فلترة اختيارية"""
    query = db.query(Transaction)
    
    if project_id:
        query = query.filter(Transaction.project_id == project_id)
    if type:
        query = query.filter(Transaction.type == type)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    result = []
    for t in transactions:
        project = t.project
        unit = t.unit
        
        result.append(TransactionResponse(
            id=t.id,
            project_id=t.project_id,
            unit_id=t.unit_id,
            description=t.description,
            date=t.date,
            amount=t.amount,
            type=t.type,
            category=t.category,
            project_name=project.name if project else "غير معروف",
            unit_name=unit.unit_name if unit else None,
            created_at=t.created_at
        ))
    
    return result


@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    project_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على ملخص مالي"""
    query = db.query(Transaction)
    
    if project_id:
        query = query.filter(Transaction.project_id == project_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    income = query.filter(Transaction.type == "دخل").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar() or Decimal("0")
    
    expense = query.filter(Transaction.type == "صرف").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar() or Decimal("0")
    
    return FinancialSummary(
        total_income=income,
        total_expense=expense,
        net_profit=income - expense
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """الحصول على معاملة محددة"""
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المعاملة غير موجودة"
        )
    
    project = t.project
    unit = t.unit
    
    return TransactionResponse(
        id=t.id,
        project_id=t.project_id,
        unit_id=t.unit_id,
        description=t.description,
        date=t.date,
        amount=t.amount,
        type=t.type,
        category=t.category,
        project_name=project.name if project else "غير معروف",
        unit_name=unit.unit_name if unit else None,
        created_at=t.created_at
    )


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إضافة معاملة مالية جديدة"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == transaction_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="المشروع غير موجود"
        )
    
    # Verify unit if provided
    unit = None
    if transaction_data.unit_id:
        unit = db.query(Unit).filter(Unit.id == transaction_data.unit_id).first()
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="الوحدة غير موجودة"
            )
    
    new_transaction = Transaction(
        project_id=transaction_data.project_id,
        unit_id=transaction_data.unit_id,
        description=transaction_data.description,
        date=transaction_data.date,
        amount=transaction_data.amount,
        type=transaction_data.type.value,
        category=transaction_data.category
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return TransactionResponse(
        id=new_transaction.id,
        project_id=new_transaction.project_id,
        unit_id=new_transaction.unit_id,
        description=new_transaction.description,
        date=new_transaction.date,
        amount=new_transaction.amount,
        type=new_transaction.type,
        category=new_transaction.category,
        project_name=project.name,
        unit_name=unit.unit_name if unit else None,
        created_at=new_transaction.created_at
    )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تحديث معاملة مالية"""
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المعاملة غير موجودة"
        )
    
    update_data = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "type" and value:
            setattr(t, field, value.value)
        else:
            setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    
    project = t.project
    unit = t.unit
    
    return TransactionResponse(
        id=t.id,
        project_id=t.project_id,
        unit_id=t.unit_id,
        description=t.description,
        date=t.date,
        amount=t.amount,
        type=t.type,
        category=t.category,
        project_name=project.name if project else "غير معروف",
        unit_name=unit.unit_name if unit else None,
        created_at=t.created_at
    )


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف معاملة مالية"""
    t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المعاملة غير موجودة"
        )
    
    db.delete(t)
    db.commit()
    
    return {"message": "تم حذف المعاملة بنجاح"}

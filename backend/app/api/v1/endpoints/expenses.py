"""Expense management endpoints."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.models.expense import ExpenseCategory
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseUpdate,
)
from app.services.business_service import BusinessService
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


async def _get_business(business_id: int, user: User, db):
    svc = BusinessService(db)
    biz = await svc.get_by_id(business_id)
    if not biz or (biz.owner_id != user.id and user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Business not found")
    return biz


@router.post("/{business_id}", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    business_id: int,
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = ExpenseService(db)
    return await svc.create(business_id, payload)


@router.get("/{business_id}", response_model=ExpenseListResponse)
async def list_expenses(
    business_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[ExpenseCategory] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = ExpenseService(db)
    skip = (page - 1) * page_size
    items, total, total_amount = await svc.list_by_business(
        business_id, skip, page_size, start_date, end_date, category
    )
    return ExpenseListResponse(items=items, total=total, page=page, page_size=page_size, total_amount=total_amount)


@router.get("/{business_id}/summary", response_model=ExpenseSummary)
async def expense_summary(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = ExpenseService(db)
    return await svc.get_summary(business_id)


@router.get("/{business_id}/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    business_id: int,
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = ExpenseService(db)
    expense = await svc.get_by_id(expense_id, business_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{business_id}/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    business_id: int,
    expense_id: int,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = ExpenseService(db)
    expense = await svc.get_by_id(expense_id, business_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return await svc.update(expense, payload)


@router.delete("/{business_id}/{expense_id}", status_code=204)
async def delete_expense(
    business_id: int,
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = ExpenseService(db)
    expense = await svc.get_by_id(expense_id, business_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await svc.delete(expense)

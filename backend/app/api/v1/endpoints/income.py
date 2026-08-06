"""Income management endpoints."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.models.income import IncomeCategory
from app.models.user import User
from app.schemas.income import IncomeCreate, IncomeListResponse, IncomeResponse, IncomeSummary, IncomeUpdate
from app.services.business_service import BusinessService
from app.services.income_service import IncomeService

router = APIRouter(prefix="/income", tags=["Income"])


async def _get_business(business_id: int, user: User, db):
    svc = BusinessService(db)
    biz = await svc.get_by_id(business_id)
    if not biz or (biz.owner_id != user.id and user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Business not found")
    return biz


@router.post("/{business_id}", response_model=IncomeResponse, status_code=201)
async def create_income(
    business_id: int,
    payload: IncomeCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = IncomeService(db)
    return await svc.create(business_id, payload)


@router.get("/{business_id}", response_model=IncomeListResponse)
async def list_incomes(
    business_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[IncomeCategory] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = IncomeService(db)
    skip = (page - 1) * page_size
    items, total, total_amount = await svc.list_by_business(
        business_id, skip, page_size, start_date, end_date, category
    )
    return IncomeListResponse(items=items, total=total, page=page, page_size=page_size, total_amount=total_amount)


@router.get("/{business_id}/summary", response_model=IncomeSummary)
async def income_summary(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = IncomeService(db)
    return await svc.get_summary(business_id)


@router.get("/{business_id}/{income_id}", response_model=IncomeResponse)
async def get_income(
    business_id: int,
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = IncomeService(db)
    income = await svc.get_by_id(income_id, business_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return income


@router.put("/{business_id}/{income_id}", response_model=IncomeResponse)
async def update_income(
    business_id: int,
    income_id: int,
    payload: IncomeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = IncomeService(db)
    income = await svc.get_by_id(income_id, business_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    return await svc.update(income, payload)


@router.delete("/{business_id}/{income_id}", status_code=204)
async def delete_income(
    business_id: int,
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = IncomeService(db)
    income = await svc.get_by_id(income_id, business_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    await svc.delete(income)

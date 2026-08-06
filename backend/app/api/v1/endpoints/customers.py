"""Customer management endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.models.customer import CustomerRisk
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerDuesSummary,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.business_service import BusinessService
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


async def _get_business(business_id: int, user: User, db):
    svc = BusinessService(db)
    biz = await svc.get_by_id(business_id)
    if not biz or (biz.owner_id != user.id and user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Business not found")
    return biz


@router.post("/{business_id}", response_model=CustomerResponse, status_code=201)
async def create_customer(
    business_id: int,
    payload: CustomerCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = CustomerService(db)
    return await svc.create(business_id, payload)


@router.get("/{business_id}", response_model=CustomerListResponse)
async def list_customers(
    business_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_filter: Optional[CustomerRisk] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = CustomerService(db)
    skip = (page - 1) * page_size
    items, total, total_outstanding = await svc.list_by_business(business_id, skip, page_size, risk_filter)
    return CustomerListResponse(items=items, total=total, page=page, page_size=page_size, total_outstanding=total_outstanding)


@router.get("/{business_id}/dues-summary", response_model=CustomerDuesSummary)
async def dues_summary(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = CustomerService(db)
    return await svc.get_dues_summary(business_id)


@router.get("/{business_id}/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    business_id: int,
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = CustomerService(db)
    customer = await svc.get_by_id(customer_id, business_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{business_id}/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    business_id: int,
    customer_id: int,
    payload: CustomerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = CustomerService(db)
    customer = await svc.get_by_id(customer_id, business_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return await svc.update(customer, payload)


@router.delete("/{business_id}/{customer_id}", status_code=204)
async def delete_customer(
    business_id: int,
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_business(business_id, current_user, db)
    svc = CustomerService(db)
    customer = await svc.get_by_id(customer_id, business_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await svc.delete(customer)

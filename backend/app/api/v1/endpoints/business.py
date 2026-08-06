"""Business profile CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db, require_owner
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate
from app.services.business_service import BusinessService

router = APIRouter(prefix="/business", tags=["Business"])


@router.post("", response_model=BusinessResponse, status_code=201)
async def create_business(
    payload: BusinessCreate,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BusinessService(db)
    business = await service.create(current_user.id, payload)
    return business


@router.get("", response_model=list[BusinessResponse])
async def list_my_businesses(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = BusinessService(db)
    return await service.get_by_owner(current_user.id)


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return business


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    payload: BusinessUpdate,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Business not found")
    return await service.update(business, payload)


@router.delete("/{business_id}", status_code=204)
async def delete_business(
    business_id: int,
    current_user: User = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Business not found")
    await service.delete(business)

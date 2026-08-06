"""User management endpoints (admin only for listing, self-service for profile)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db, require_admin
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    return await svc.update(current_user, payload)


@router.get("", response_model=UserListResponse, dependencies=[Depends(require_admin)])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    svc = UserService(db)
    skip = (page - 1) * page_size
    users, total = await svc.list_all(skip, page_size)
    return UserListResponse(items=users, total=total, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    svc = UserService(db)
    user = await svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    svc = UserService(db)
    user = await svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False

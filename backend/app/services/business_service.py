"""Business profile CRUD service."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessUpdate


class BusinessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, business_id: int) -> Optional[Business]:
        result = await self.db.execute(
            select(Business).where(Business.id == business_id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: int) -> list[Business]:
        result = await self.db.execute(
            select(Business).where(Business.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def get_first_by_owner(self, owner_id: int) -> Optional[Business]:
        result = await self.db.execute(
            select(Business).where(Business.owner_id == owner_id).limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, owner_id: int, schema: BusinessCreate) -> Business:
        business = Business(owner_id=owner_id, **schema.model_dump())
        self.db.add(business)
        await self.db.flush()
        await self.db.refresh(business)
        return business

    async def update(self, business: Business, schema: BusinessUpdate) -> Business:
        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(business, field, value)
        await self.db.flush()
        await self.db.refresh(business)
        return business

    async def delete(self, business: Business) -> None:
        await self.db.delete(business)
        await self.db.flush()

    async def list_all(self, skip: int = 0, limit: int = 50) -> tuple[list[Business], int]:
        result = await self.db.execute(select(Business).offset(skip).limit(limit))
        businesses = list(result.scalars().all())
        count_result = await self.db.execute(select(Business))
        total = len(count_result.scalars().all())
        return businesses, total

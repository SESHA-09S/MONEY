"""User CRUD service."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, schema: UserCreate) -> User:
        user = User(
            email=schema.email,
            hashed_password=get_password_hash(schema.password),
            full_name=schema.full_name,
            phone=schema.phone,
            role=schema.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, schema: UserUpdate) -> User:
        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def change_password(self, user: User, new_password: str) -> User:
        user.hashed_password = get_password_hash(new_password)
        await self.db.flush()
        return user

    async def set_email_verified(self, user: User) -> User:
        user.is_email_verified = True
        user.email_verification_token = None
        await self.db.flush()
        return user

    async def list_all(self, skip: int = 0, limit: int = 50) -> tuple[list[User], int]:
        count_result = await self.db.execute(select(User))
        all_users = count_result.scalars().all()
        total = len(all_users)
        paginated = all_users[skip: skip + limit]
        return list(paginated), total

"""Income CRUD and analytics service."""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.income import Income, IncomeCategory
from app.schemas.income import IncomeCreate, IncomeUpdate


class IncomeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, income_id: int, business_id: int) -> Optional[Income]:
        result = await self.db.execute(
            select(Income).where(Income.id == income_id, Income.business_id == business_id)
        )
        return result.scalar_one_or_none()

    async def create(self, business_id: int, schema: IncomeCreate) -> Income:
        income = Income(business_id=business_id, **schema.model_dump())
        self.db.add(income)
        await self.db.flush()
        await self.db.refresh(income)
        return income

    async def update(self, income: Income, schema: IncomeUpdate) -> Income:
        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(income, field, value)
        await self.db.flush()
        await self.db.refresh(income)
        return income

    async def delete(self, income: Income) -> None:
        await self.db.delete(income)
        await self.db.flush()

    async def list_by_business(
        self,
        business_id: int,
        skip: int = 0,
        limit: int = 50,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[IncomeCategory] = None,
    ) -> tuple[list[Income], int, float]:
        query = select(Income).where(Income.business_id == business_id)
        if start_date:
            query = query.where(Income.transaction_date >= start_date)
        if end_date:
            query = query.where(Income.transaction_date <= end_date)
        if category:
            query = query.where(Income.category == category)

        count_result = await self.db.execute(query)
        all_items = list(count_result.scalars().all())
        total = len(all_items)
        total_amount = sum(i.amount for i in all_items)
        paginated = all_items[skip: skip + limit]
        return paginated, total, total_amount

    async def get_summary(self, business_id: int) -> dict:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        result = await self.db.execute(
            select(Income).where(Income.business_id == business_id)
        )
        all_incomes = list(result.scalars().all())

        def total_for(items, start: date) -> float:
            return sum(i.amount for i in items if i.transaction_date >= start)

        by_category: dict[str, float] = {}
        by_method: dict[str, float] = {}
        for inc in all_incomes:
            by_category[inc.category.value] = by_category.get(inc.category.value, 0) + inc.amount
            by_method[inc.payment_method.value] = by_method.get(inc.payment_method.value, 0) + inc.amount

        # Daily trend for last 30 days
        trend_map: dict[str, float] = {}
        for inc in all_incomes:
            if inc.transaction_date >= month_start:
                key = inc.transaction_date.isoformat()
                trend_map[key] = trend_map.get(key, 0) + inc.amount
        trend = [{"date": k, "amount": v} for k, v in sorted(trend_map.items())]

        return {
            "today": total_for(all_incomes, today),
            "this_week": total_for(all_incomes, week_start),
            "this_month": total_for(all_incomes, month_start),
            "this_year": total_for(all_incomes, year_start),
            "by_category": by_category,
            "by_payment_method": by_method,
            "trend": trend,
        }

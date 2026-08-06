"""Expense CRUD and analytics service."""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, expense_id: int, business_id: int) -> Optional[Expense]:
        result = await self.db.execute(
            select(Expense).where(Expense.id == expense_id, Expense.business_id == business_id)
        )
        return result.scalar_one_or_none()

    async def create(self, business_id: int, schema: ExpenseCreate) -> Expense:
        expense = Expense(business_id=business_id, **schema.model_dump())
        self.db.add(expense)
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def update(self, expense: Expense, schema: ExpenseUpdate) -> Expense:
        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(expense, field, value)
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def delete(self, expense: Expense) -> None:
        await self.db.delete(expense)
        await self.db.flush()

    async def list_by_business(
        self,
        business_id: int,
        skip: int = 0,
        limit: int = 50,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[ExpenseCategory] = None,
    ) -> tuple[list[Expense], int, float]:
        query = select(Expense).where(Expense.business_id == business_id)
        if start_date:
            query = query.where(Expense.transaction_date >= start_date)
        if end_date:
            query = query.where(Expense.transaction_date <= end_date)
        if category:
            query = query.where(Expense.category == category)
        result = await self.db.execute(query)
        all_items = list(result.scalars().all())
        total = len(all_items)
        total_amount = sum(e.amount for e in all_items)
        return all_items[skip: skip + limit], total, total_amount

    async def get_all_for_business(self, business_id: int) -> list[Expense]:
        result = await self.db.execute(
            select(Expense).where(Expense.business_id == business_id)
        )
        return list(result.scalars().all())

    async def get_summary(self, business_id: int) -> dict:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        all_expenses = await self.get_all_for_business(business_id)

        def total_for(items, start: date) -> float:
            return sum(e.amount for e in items if e.transaction_date >= start)

        by_category: dict[str, float] = {}
        for exp in all_expenses:
            by_category[exp.category.value] = by_category.get(exp.category.value, 0) + exp.amount

        trend_map: dict[str, float] = {}
        for exp in all_expenses:
            if exp.transaction_date >= month_start:
                key = exp.transaction_date.isoformat()
                trend_map[key] = trend_map.get(key, 0) + exp.amount
        trend = [{"date": k, "amount": v} for k, v in sorted(trend_map.items())]
        anomalies_count = sum(1 for e in all_expenses if e.is_anomaly)

        return {
            "today": total_for(all_expenses, today),
            "this_week": total_for(all_expenses, week_start),
            "this_month": total_for(all_expenses, month_start),
            "this_year": total_for(all_expenses, year_start),
            "by_category": by_category,
            "anomalies_count": anomalies_count,
            "trend": trend,
        }

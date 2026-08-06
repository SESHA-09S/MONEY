"""Customer CRUD and analytics service."""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerRisk
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, customer_id: int, business_id: int) -> Optional[Customer]:
        result = await self.db.execute(
            select(Customer).where(
                Customer.id == customer_id, Customer.business_id == business_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, business_id: int, schema: CustomerCreate) -> Customer:
        customer = Customer(business_id=business_id, **schema.model_dump())
        self.db.add(customer)
        await self.db.flush()
        await self.db.refresh(customer)
        return customer

    async def update(self, customer: Customer, schema: CustomerUpdate) -> Customer:
        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)
        # Recalculate risk
        customer.risk_rating = self._calculate_risk(customer)
        await self.db.flush()
        await self.db.refresh(customer)
        return customer

    async def delete(self, customer: Customer) -> None:
        await self.db.delete(customer)
        await self.db.flush()

    async def list_by_business(
        self,
        business_id: int,
        skip: int = 0,
        limit: int = 50,
        risk_filter: Optional[CustomerRisk] = None,
    ) -> tuple[list[Customer], int, float]:
        query = select(Customer).where(Customer.business_id == business_id)
        if risk_filter:
            query = query.where(Customer.risk_rating == risk_filter)
        result = await self.db.execute(query)
        all_items = list(result.scalars().all())
        total = len(all_items)
        total_outstanding = sum(c.outstanding_amount for c in all_items)
        return all_items[skip: skip + limit], total, total_outstanding

    async def get_dues_summary(self, business_id: int) -> dict:
        result = await self.db.execute(
            select(Customer).where(Customer.business_id == business_id, Customer.is_active == True)
        )
        customers = list(result.scalars().all())
        today = date.today()
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)

        total_outstanding = sum(c.outstanding_amount for c in customers)
        overdue = [c for c in customers if c.due_date and c.due_date < today and c.outstanding_amount > 0]
        high_risk = [c for c in customers if c.risk_rating in (CustomerRisk.HIGH, CustomerRisk.CRITICAL)]
        due_week = sum(c.outstanding_amount for c in customers if c.due_date and today <= c.due_date <= week_end)
        due_month = sum(c.outstanding_amount for c in customers if c.due_date and today <= c.due_date <= month_end)

        return {
            "total_outstanding": total_outstanding,
            "overdue_count": len(overdue),
            "high_risk_count": len(high_risk),
            "due_this_week": due_week,
            "due_this_month": due_month,
        }

    @staticmethod
    def _calculate_risk(customer: Customer) -> CustomerRisk:
        score = 0
        if customer.outstanding_amount > customer.credit_limit * 0.8:
            score += 3
        elif customer.outstanding_amount > customer.credit_limit * 0.5:
            score += 2
        if customer.late_payment_count > 5:
            score += 3
        elif customer.late_payment_count > 2:
            score += 2
        elif customer.late_payment_count > 0:
            score += 1
        if customer.due_date and customer.due_date < date.today() and customer.outstanding_amount > 0:
            score += 2
        if score >= 6:
            return CustomerRisk.CRITICAL
        elif score >= 4:
            return CustomerRisk.HIGH
        elif score >= 2:
            return CustomerRisk.MEDIUM
        return CustomerRisk.LOW

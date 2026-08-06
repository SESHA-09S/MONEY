"""Cash Flow engine — calculates key financial metrics."""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business
from app.models.expense import Expense
from app.models.income import Income


class CashFlowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(self, business: Business, period_days: int = 30) -> dict:
        today = date.today()
        start = today - timedelta(days=period_days)

        # Fetch incomes
        inc_result = await self.db.execute(
            select(Income).where(
                Income.business_id == business.id,
                Income.transaction_date >= start,
                Income.transaction_date <= today,
            )
        )
        incomes = inc_result.scalars().all()

        # Fetch expenses
        exp_result = await self.db.execute(
            select(Expense).where(
                Expense.business_id == business.id,
                Expense.transaction_date >= start,
                Expense.transaction_date <= today,
            )
        )
        expenses = exp_result.scalars().all()

        cash_in = sum(i.amount for i in incomes)
        cash_out = sum(e.amount for e in expenses)
        net_cash_flow = cash_in - cash_out

        # Monthly burn rate (average daily expense * 30)
        avg_daily_expense = cash_out / period_days if period_days > 0 else 0
        burn_rate = avg_daily_expense * 30

        # Current cash balance
        all_inc_result = await self.db.execute(
            select(Income).where(Income.business_id == business.id)
        )
        all_exp_result = await self.db.execute(
            select(Expense).where(Expense.business_id == business.id)
        )
        total_income = sum(i.amount for i in all_inc_result.scalars().all())
        total_expense = sum(e.amount for e in all_exp_result.scalars().all())
        cash_balance = business.opening_balance + total_income - total_expense

        # Runway: how many days cash will last at current burn rate
        runway_days = (cash_balance / avg_daily_expense) if avg_daily_expense > 0 else 999

        # Operating cash (last 30 days net)
        operating_cash = net_cash_flow

        # Reserve cash (20% of monthly revenue recommended)
        reserve_cash = cash_in * 0.2

        # Build chart data (daily cash flow for last 30 days)
        daily_chart: dict[str, dict] = {}
        for i in range(period_days + 1):
            day = (start + timedelta(days=i)).isoformat()
            daily_chart[day] = {"date": day, "income": 0.0, "expense": 0.0, "net": 0.0}

        for inc in incomes:
            key = inc.transaction_date.isoformat()
            if key in daily_chart:
                daily_chart[key]["income"] += inc.amount
                daily_chart[key]["net"] += inc.amount

        for exp in expenses:
            key = exp.transaction_date.isoformat()
            if key in daily_chart:
                daily_chart[key]["expense"] += exp.amount
                daily_chart[key]["net"] -= exp.amount

        chart_data = list(daily_chart.values())

        return {
            "cash_in": cash_in,
            "cash_out": cash_out,
            "net_cash_flow": net_cash_flow,
            "burn_rate": burn_rate,
            "runway_days": max(0.0, runway_days),
            "operating_cash": operating_cash,
            "reserve_cash": reserve_cash,
            "opening_balance": business.opening_balance,
            "closing_balance": cash_balance,
            "cash_balance": cash_balance,
            "chart_data": chart_data,
            "period_days": period_days,
        }

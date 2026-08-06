"""Dashboard analytics endpoint — returns everything the UI needs in one call."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db
from app.models.expense import Expense
from app.models.income import Income
from app.models.notification import Notification
from app.models.risk_score import RiskScore
from app.models.user import User
from app.services.business_service import BusinessService
from app.services.cashflow_service import CashFlowService
from app.services.income_service import IncomeService
from app.services.expense_service import ExpenseService
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{business_id}")
async def get_dashboard(
    business_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns complete dashboard data in one request."""
    biz_svc = BusinessService(db)
    business = await biz_svc.get_by_id(business_id)
    if not business or (business.owner_id != current_user.id and current_user.role.value != "admin"):
        raise HTTPException(status_code=404, detail="Business not found")

    today = date.today()
    month_start = today.replace(day=1)

    # ── Cash Flow ─────────────────────────────────────────────────────────────
    cf_svc = CashFlowService(db)
    cf_data = await cf_svc.calculate(business, period_days=30)

    # ── Income summary ────────────────────────────────────────────────────────
    inc_svc = IncomeService(db)
    inc_summary = await inc_svc.get_summary(business_id)

    # ── Expense summary ───────────────────────────────────────────────────────
    exp_svc = ExpenseService(db)
    exp_summary = await exp_svc.get_summary(business_id)

    # ── Customer dues ─────────────────────────────────────────────────────────
    cust_svc = CustomerService(db)
    dues = await cust_svc.get_dues_summary(business_id)
    _, total_customers, _ = await cust_svc.list_by_business(business_id, 0, 1000)

    # ── Latest risk score ─────────────────────────────────────────────────────
    risk_result = await db.execute(
        select(RiskScore)
        .where(RiskScore.business_id == business_id)
        .order_by(RiskScore.created_at.desc())
        .limit(1)
    )
    latest_risk = risk_result.scalar_one_or_none()
    health_score = latest_risk.health_score if latest_risk else 0.0
    risk_score = latest_risk.risk_score if latest_risk else 0.0
    rating = latest_risk.rating if latest_risk else "red"

    # ── Notifications ─────────────────────────────────────────────────────────
    notif_result = await db.execute(
        select(Notification)
        .where(Notification.business_id == business_id, Notification.is_read == False)
        .order_by(Notification.created_at.desc())
        .limit(10)
    )
    notifications = [
        {"id": n.id, "type": n.type.value, "title": n.title, "message": n.message,
         "created_at": n.created_at.isoformat()}
        for n in notif_result.scalars().all()
    ]

    # ── Recent transactions (last 10) ─────────────────────────────────────────
    inc_recent = await db.execute(
        select(Income).where(Income.business_id == business_id)
        .order_by(Income.transaction_date.desc()).limit(5)
    )
    exp_recent = await db.execute(
        select(Expense).where(Expense.business_id == business_id)
        .order_by(Expense.transaction_date.desc()).limit(5)
    )
    recent_transactions = []
    for inc in inc_recent.scalars().all():
        recent_transactions.append({
            "id": inc.id, "type": "income", "amount": inc.amount,
            "category": inc.category.value, "date": inc.transaction_date.isoformat(),
            "description": inc.description or inc.category.value,
        })
    for exp in exp_recent.scalars().all():
        recent_transactions.append({
            "id": exp.id, "type": "expense", "amount": exp.amount,
            "category": exp.category.value, "date": exp.transaction_date.isoformat(),
            "description": exp.description or exp.category.value,
        })
    recent_transactions.sort(key=lambda x: x["date"], reverse=True)
    recent_transactions = recent_transactions[:10]

    # ── Expense by category (pie chart) ──────────────────────────────────────
    expense_by_category = [
        {"name": k, "value": v}
        for k, v in exp_summary["by_category"].items()
    ]

    # ── Key metrics ───────────────────────────────────────────────────────────
    today_income = inc_summary["today"]
    today_expense = exp_summary["today"]
    net_profit = today_income - today_expense

    return {
        "metrics": {
            "today_income": today_income,
            "today_expense": today_expense,
            "net_profit": net_profit,
            "cash_balance": cf_data["cash_balance"],
            "cash_runway_days": cf_data["runway_days"],
            "pending_payments": dues["total_outstanding"],
            "health_score": health_score,
            "risk_score": risk_score,
            "burn_rate": cf_data["burn_rate"],
            "total_customers": total_customers,
            "overdue_invoices": dues["overdue_count"],
        },
        "cash_flow": {
            "cash_in": cf_data["cash_in"],
            "cash_out": cf_data["cash_out"],
            "net_cash_flow": cf_data["net_cash_flow"],
            "burn_rate": cf_data["burn_rate"],
            "runway_days": cf_data["runway_days"],
            "operating_cash": cf_data["operating_cash"],
            "reserve_cash": cf_data["reserve_cash"],
            "opening_balance": cf_data["opening_balance"],
            "closing_balance": cf_data["closing_balance"],
        },
        "income_trend": inc_summary["trend"],
        "expense_trend": exp_summary["trend"],
        "cash_flow_chart": cf_data["chart_data"],
        "expense_by_category": expense_by_category,
        "recent_transactions": recent_transactions,
        "forecast_chart": [],  # Populated by /predictions endpoint
        "health_score": health_score,
        "risk_score": risk_score,
        "rating": rating,
        "notifications": notifications,
    }

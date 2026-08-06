"""Dashboard summary schemas."""
from typing import Optional
from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    today_income: float
    today_expense: float
    net_profit: float
    cash_balance: float
    cash_runway_days: float
    pending_payments: float
    health_score: float
    risk_score: float
    burn_rate: float
    total_customers: int
    overdue_invoices: int


class CashFlowData(BaseModel):
    cash_in: float
    cash_out: float
    net_cash_flow: float
    burn_rate: float
    runway_days: float
    operating_cash: float
    reserve_cash: float
    opening_balance: float
    closing_balance: float


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    cash_flow: CashFlowData
    income_trend: list[dict]
    expense_trend: list[dict]
    cash_flow_chart: list[dict]
    expense_by_category: list[dict]
    recent_transactions: list[dict]
    upcoming_bills: list[dict]
    forecast_chart: list[dict]
    health_score: float
    risk_score: float
    rating: str
    notifications: list[dict]

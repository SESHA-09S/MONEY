"""Expense schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    amount: float
    category: ExpenseCategory = ExpenseCategory.MISCELLANEOUS
    description: Optional[str] = None
    vendor_name: Optional[str] = None
    reference_number: Optional[str] = None
    transaction_date: date
    is_recurring: bool = False

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    vendor_name: Optional[str] = None
    reference_number: Optional[str] = None
    transaction_date: Optional[date] = None
    is_recurring: Optional[bool] = None


class ExpenseResponse(BaseModel):
    id: int
    business_id: int
    amount: float
    category: ExpenseCategory
    description: Optional[str]
    vendor_name: Optional[str]
    reference_number: Optional[str]
    transaction_date: date
    receipt_url: Optional[str]
    is_recurring: bool
    is_anomaly: bool
    anomaly_score: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
    total_amount: float


class ExpenseSummary(BaseModel):
    today: float
    this_week: float
    this_month: float
    this_year: float
    by_category: dict[str, float]
    anomalies_count: int
    trend: list[dict]

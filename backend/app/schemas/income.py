"""Income schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.income import IncomeCategory, PaymentMethod


class IncomeCreate(BaseModel):
    amount: float
    category: IncomeCategory = IncomeCategory.SALES
    payment_method: PaymentMethod = PaymentMethod.CASH
    description: Optional[str] = None
    reference_number: Optional[str] = None
    transaction_date: date
    customer_id: Optional[int] = None
    is_recurring: bool = False

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[IncomeCategory] = None
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None
    reference_number: Optional[str] = None
    transaction_date: Optional[date] = None
    customer_id: Optional[int] = None
    is_recurring: Optional[bool] = None


class IncomeResponse(BaseModel):
    id: int
    business_id: int
    customer_id: Optional[int]
    amount: float
    category: IncomeCategory
    payment_method: PaymentMethod
    description: Optional[str]
    reference_number: Optional[str]
    transaction_date: date
    is_recurring: bool
    receipt_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class IncomeListResponse(BaseModel):
    items: list[IncomeResponse]
    total: int
    page: int
    page_size: int
    total_amount: float


class IncomeSummary(BaseModel):
    today: float
    this_week: float
    this_month: float
    this_year: float
    by_category: dict[str, float]
    by_payment_method: dict[str, float]
    trend: list[dict]  # [{"date": "2024-01-01", "amount": 5000}]

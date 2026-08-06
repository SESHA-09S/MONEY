"""Customer schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.customer import CustomerRisk


class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    outstanding_amount: float = 0.0
    credit_limit: float = 50000.0
    due_date: Optional[date] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    outstanding_amount: Optional[float] = None
    credit_limit: Optional[float] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    id: int
    business_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    outstanding_amount: float
    credit_limit: float
    due_date: Optional[date]
    risk_rating: CustomerRisk
    late_payment_count: int
    total_paid: float
    total_invoiced: float
    reminder_sent: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_outstanding: float


class CustomerDuesSummary(BaseModel):
    total_outstanding: float
    overdue_count: int
    high_risk_count: int
    due_this_week: float
    due_this_month: float

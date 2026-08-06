"""Business profile schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.business import FinancialYearMonth, IndustryType


class BusinessCreate(BaseModel):
    name: str
    gst_number: Optional[str] = None
    industry: IndustryType = IndustryType.RETAIL
    description: Optional[str] = None
    currency: str = "INR"
    opening_balance: float = 0.0
    financial_year_start: FinancialYearMonth = FinancialYearMonth.APRIL
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    gst_number: Optional[str] = None
    industry: Optional[IndustryType] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    opening_balance: Optional[float] = None
    financial_year_start: Optional[FinancialYearMonth] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None


class BusinessResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    gst_number: Optional[str]
    industry: IndustryType
    description: Optional[str]
    currency: str
    opening_balance: float
    financial_year_start: FinancialYearMonth
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    logo_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

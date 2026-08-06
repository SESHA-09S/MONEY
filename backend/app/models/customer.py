"""
Customer model — business customers with payment tracking and risk rating.
"""
import enum
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CustomerRisk(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    outstanding_amount: Mapped[float] = mapped_column(Float, default=0.0)
    credit_limit: Mapped[float] = mapped_column(Float, default=50000.0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    risk_rating: Mapped[CustomerRisk] = mapped_column(Enum(CustomerRisk), default=CustomerRisk.LOW)
    late_payment_count: Mapped[int] = mapped_column(Integer, default=0)
    total_paid: Mapped[float] = mapped_column(Float, default=0.0)
    total_invoiced: Mapped[float] = mapped_column(Float, default=0.0)

    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    last_reminder_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    business: Mapped["Business"] = relationship("Business", back_populates="customers")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="customer")
    payments: Mapped[list["Income"]] = relationship("Income", back_populates="customer")


from app.models.business import Business  # noqa: E402
from app.models.invoice import Invoice  # noqa: E402
from app.models.income import Income  # noqa: E402

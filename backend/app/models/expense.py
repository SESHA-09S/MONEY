"""
Expense model — tracks all money going out of the business.
"""
import enum
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ExpenseCategory(str, enum.Enum):
    RENT = "rent"
    SALARY = "salary"
    FUEL = "fuel"
    ELECTRICITY = "electricity"
    MARKETING = "marketing"
    INVENTORY = "inventory"
    MAINTENANCE = "maintenance"
    TAXES = "taxes"
    MISCELLANEOUS = "miscellaneous"
    LOAN_REPAYMENT = "loan_repayment"
    INSURANCE = "insurance"
    EQUIPMENT = "equipment"
    SUBSCRIPTION = "subscription"
    TRANSPORT = "transport"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[ExpenseCategory] = mapped_column(Enum(ExpenseCategory), default=ExpenseCategory.MISCELLANEOUS)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)

    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    business: Mapped["Business"] = relationship("Business", back_populates="expenses")


from app.models.business import Business  # noqa: E402

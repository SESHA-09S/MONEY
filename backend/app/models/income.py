"""
Income model — tracks all money coming into the business.
"""
import enum
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class IncomeCategory(str, enum.Enum):
    SALES = "sales"
    BANK = "bank"
    CASH = "cash"
    ONLINE = "online"
    CUSTOMER_PAYMENT = "customer_payment"
    INVESTMENT = "investment"
    LOAN = "loan"
    OTHER = "other"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    CARD = "card"
    CHEQUE = "cheque"
    OTHER = "other"


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[IncomeCategory] = mapped_column(Enum(IncomeCategory), default=IncomeCategory.SALES)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.CASH)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)

    is_recurring: Mapped[bool] = mapped_column(default=False)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    business: Mapped["Business"] = relationship("Business", back_populates="incomes")
    customer: Mapped["Customer | None"] = relationship("Customer", back_populates="payments")


from app.models.business import Business  # noqa: E402
from app.models.customer import Customer  # noqa: E402

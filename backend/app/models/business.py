"""
Business profile model.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class IndustryType(str, enum.Enum):
    GROCERY = "grocery"
    MEDICAL = "medical"
    RESTAURANT = "restaurant"
    SALON = "salon"
    TUITION = "tuition"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    HOME_BUSINESS = "home_business"
    FREELANCER = "freelancer"
    STARTUP = "startup"
    OTHER = "other"


class FinancialYearMonth(str, enum.Enum):
    APRIL = "april"
    JANUARY = "january"


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gst_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    industry: Mapped[IndustryType] = mapped_column(Enum(IndustryType), default=IndustryType.RETAIL)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    currency: Mapped[str] = mapped_column(String(10), default="INR")
    opening_balance: Mapped[float] = mapped_column(Float, default=0.0)
    financial_year_start: Mapped[FinancialYearMonth] = mapped_column(
        Enum(FinancialYearMonth), default=FinancialYearMonth.APRIL
    )

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="businesses")
    incomes: Mapped[list["Income"]] = relationship("Income", back_populates="business")
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="business")
    customers: Mapped[list["Customer"]] = relationship("Customer", back_populates="business")
    predictions: Mapped[list["Prediction"]] = relationship("Prediction", back_populates="business")
    risk_scores: Mapped[list["RiskScore"]] = relationship("RiskScore", back_populates="business")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="business")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="business")


from app.models.user import User  # noqa: E402
from app.models.income import Income  # noqa: E402
from app.models.expense import Expense  # noqa: E402
from app.models.customer import Customer  # noqa: E402
from app.models.prediction import Prediction  # noqa: E402
from app.models.risk_score import RiskScore  # noqa: E402
from app.models.recommendation import Recommendation  # noqa: E402
from app.models.notification import Notification  # noqa: E402

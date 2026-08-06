"""
Recommendation model — AI-generated actionable financial advice.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RecommendationCategory(str, enum.Enum):
    CASH_FLOW = "cash_flow"
    EXPENSES = "expenses"
    REVENUE = "revenue"
    CUSTOMER = "customer"
    INVENTORY = "inventory"
    SAVINGS = "savings"
    RISK = "risk"
    GROWTH = "growth"


class RecommendationPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_items: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list

    category: Mapped[RecommendationCategory] = mapped_column(
        Enum(RecommendationCategory), default=RecommendationCategory.CASH_FLOW
    )
    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM
    )

    estimated_impact: Mapped[float | None] = mapped_column(Float, nullable=True)  # INR amount
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_implemented: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    business: Mapped["Business"] = relationship("Business", back_populates="recommendations")


from app.models.business import Business  # noqa: E402

"""
Risk Score model — business health and risk assessment results.
"""
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Composite health score 0-100
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100, higher = more risk

    # Component scores
    cash_flow_score: Mapped[float] = mapped_column(Float, default=0.0)
    expense_score: Mapped[float] = mapped_column(Float, default=0.0)
    sales_score: Mapped[float] = mapped_column(Float, default=0.0)
    savings_score: Mapped[float] = mapped_column(Float, default=0.0)
    customer_dues_score: Mapped[float] = mapped_column(Float, default=0.0)
    profit_margin_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Calculated metrics
    burn_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    runway_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Rating: green / yellow / red
    rating: Mapped[str] = mapped_column(String(10), default="green")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    business: Mapped["Business"] = relationship("Business", back_populates="risk_scores")


from app.models.business import Business  # noqa: E402

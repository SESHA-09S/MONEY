"""
AI Prediction model — stores ML model outputs for cash flow forecasting.
"""
import enum
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PredictionType(str, enum.Enum):
    CASH_FLOW_7D = "cash_flow_7d"
    CASH_FLOW_15D = "cash_flow_15d"
    CASH_FLOW_30D = "cash_flow_30d"
    CASH_FLOW_90D = "cash_flow_90d"
    SALES_FORECAST = "sales_forecast"
    EXPENSE_FORECAST = "expense_forecast"
    CASH_SHORTAGE = "cash_shortage"
    BUSINESS_FAILURE_RISK = "business_failure_risk"
    CUSTOMER_LATE_PAYMENT = "customer_late_payment"


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    prediction_type: Mapped[PredictionType] = mapped_column(Enum(PredictionType), nullable=False)
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    lower_bound: Mapped[float | None] = mapped_column(Float, nullable=True)
    upper_bound: Mapped[float | None] = mapped_column(Float, nullable=True)

    prediction_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    features_used: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    forecast_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON time-series

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    business: Mapped["Business"] = relationship("Business", back_populates="predictions")


from app.models.business import Business  # noqa: E402

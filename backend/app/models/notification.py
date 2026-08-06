"""
Notification model — system alerts and reminders.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class NotificationType(str, enum.Enum):
    LOW_CASH = "low_cash"
    EXPENSE_SPIKE = "expense_spike"
    CUSTOMER_DUE = "customer_due"
    UPCOMING_BILL = "upcoming_bill"
    INVENTORY_RISK = "inventory_risk"
    ANOMALY_DETECTED = "anomaly_detected"
    CASH_SHORTAGE_PREDICTED = "cash_shortage_predicted"
    HEALTH_SCORE_DROP = "health_score_drop"
    INVOICE_OVERDUE = "invoice_overdue"
    GENERAL = "general"


class NotificationChannel(str, enum.Enum):
    DASHBOARD = "dashboard"
    EMAIL = "email"
    PUSH = "push"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel), default=NotificationChannel.DASHBOARD
    )

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    business: Mapped["Business"] = relationship("Business", back_populates="notifications")


from app.models.business import Business  # noqa: E402

"""Import all models so Alembic can detect them."""
from app.models.user import User, UserRole
from app.models.business import Business, IndustryType
from app.models.income import Income, IncomeCategory, PaymentMethod
from app.models.expense import Expense, ExpenseCategory
from app.models.customer import Customer, CustomerRisk
from app.models.invoice import Invoice, InvoiceStatus
from app.models.prediction import Prediction, PredictionType
from app.models.risk_score import RiskScore
from app.models.recommendation import Recommendation, RecommendationCategory, RecommendationPriority
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog

__all__ = [
    "User", "UserRole",
    "Business", "IndustryType",
    "Income", "IncomeCategory", "PaymentMethod",
    "Expense", "ExpenseCategory",
    "Customer", "CustomerRisk",
    "Invoice", "InvoiceStatus",
    "Prediction", "PredictionType",
    "RiskScore",
    "Recommendation", "RecommendationCategory", "RecommendationPriority",
    "Notification", "NotificationType",
    "AuditLog",
]

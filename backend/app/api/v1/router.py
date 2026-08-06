"""API v1 router — registers all endpoint modules."""
from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.business import router as business_router
from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.expenses import router as expenses_router
from app.api.v1.endpoints.income import router as income_router
from app.api.v1.endpoints.predictions import router as predictions_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(business_router)
api_router.include_router(income_router)
api_router.include_router(expenses_router)
api_router.include_router(customers_router)
api_router.include_router(dashboard_router)
api_router.include_router(predictions_router)
api_router.include_router(reports_router)

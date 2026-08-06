"""
AI Service — orchestrates all AI/ML models and persists results to the database.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.models import (
    AnomalyDetector,
    BusinessHealthScorer,
    CashFlowForecaster,
    CashShortagePredictor,
    RecommendationEngine,
)
from app.models.business import Business
from app.models.expense import Expense
from app.models.income import Income
from app.models.prediction import Prediction, PredictionType
from app.models.recommendation import Recommendation, RecommendationCategory, RecommendationPriority
from app.models.risk_score import RiskScore

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.forecaster = CashFlowForecaster()
        self.anomaly_detector = AnomalyDetector()
        self.health_scorer = BusinessHealthScorer()
        self.recommender = RecommendationEngine()
        self.shortage_predictor = CashShortagePredictor()

    # ── Data Fetchers ─────────────────────────────────────────────────────────

    async def _get_incomes(self, business_id: int) -> list[Income]:
        result = await self.db.execute(
            select(Income).where(Income.business_id == business_id)
        )
        return list(result.scalars().all())

    async def _get_expenses(self, business_id: int) -> list[Expense]:
        result = await self.db.execute(
            select(Expense).where(Expense.business_id == business_id)
        )
        return list(result.scalars().all())

    def _monthly_totals(self, records: list, months: int = 3) -> list[float]:
        """Aggregate amounts into monthly buckets for the last N months."""
        today = date.today()
        buckets: dict[str, float] = {}
        for i in range(months):
            m = (today.replace(day=1) - timedelta(days=30 * i)).strftime("%Y-%m")
            buckets[m] = 0.0
        for r in records:
            m = r.transaction_date.strftime("%Y-%m")
            if m in buckets:
                buckets[m] += r.amount
        return [buckets[k] for k in sorted(buckets.keys())]

    # ── Cash Flow Forecast ────────────────────────────────────────────────────

    async def run_cash_flow_forecast(
        self, business: Business, horizon_days: int = 30
    ) -> dict[str, Any]:
        incomes = await self._get_incomes(business.id)

        # Aggregate to daily
        daily: dict[date, float] = defaultdict(float)
        for inc in incomes:
            daily[inc.transaction_date] += inc.amount

        dates = sorted(daily.keys())
        amounts = [daily[d] for d in dates]

        forecast = self.forecaster.forecast(dates, amounts, horizon_days)

        # Map horizon to enum
        type_map = {7: PredictionType.CASH_FLOW_7D, 15: PredictionType.CASH_FLOW_15D,
                    30: PredictionType.CASH_FLOW_30D, 90: PredictionType.CASH_FLOW_90D}
        pred_type = type_map.get(horizon_days, PredictionType.CASH_FLOW_30D)

        total_forecast = sum(p["predicted"] for p in forecast)
        import numpy as np
        cv = float(np.std(amounts) / np.mean(amounts)) if amounts and np.mean(amounts) > 0 else 1.0
        confidence = self.forecaster.calculate_confidence(cv, len(amounts))

        prediction = Prediction(
            business_id=business.id,
            prediction_type=pred_type,
            predicted_value=total_forecast,
            confidence_score=confidence,
            prediction_date=date.today(),
            forecast_data=json.dumps(forecast),
            model_name="Prophet+LinearFallback",
            model_version="1.0",
        )
        self.db.add(prediction)
        await self.db.flush()

        return {"forecast": forecast, "total": total_forecast, "confidence": confidence, "id": prediction.id}

    # ── Anomaly Detection ─────────────────────────────────────────────────────

    async def run_anomaly_detection(self, business_id: int) -> dict[str, Any]:
        expenses = await self._get_expenses(business_id)
        if not expenses:
            return {"anomalies": [], "count": 0}

        expense_dicts = [
            {
                "id": e.id,
                "amount": e.amount,
                "category": e.category.value,
                "transaction_date": e.transaction_date.isoformat(),
                "vendor_name": e.vendor_name,
            }
            for e in expenses
        ]

        results = self.anomaly_detector.detect(expense_dicts)
        duplicates = self.anomaly_detector.check_duplicates(expense_dicts)

        # Persist anomaly flags
        result_map = {r["id"]: r for r in results}
        for expense in expenses:
            r = result_map.get(expense.id)
            if r:
                expense.is_anomaly = r["is_anomaly"] or expense.id in duplicates
                expense.anomaly_score = r["anomaly_score"]
        await self.db.flush()

        anomalies = [r for r in results if r["is_anomaly"] or r["id"] in duplicates]
        return {"anomalies": anomalies, "count": len(anomalies), "duplicates": duplicates}

    # ── Health Score ──────────────────────────────────────────────────────────

    async def run_health_score(self, business: Business) -> dict[str, Any]:
        incomes = await self._get_incomes(business.id)
        expenses = await self._get_expenses(business.id)

        today = date.today()
        month_start = today.replace(day=1)

        monthly_income = sum(i.amount for i in incomes if i.transaction_date >= month_start)
        monthly_expense = sum(e.amount for e in expenses if e.transaction_date >= month_start)
        total_income = sum(i.amount for i in incomes)
        total_expense = sum(e.amount for e in expenses)
        cash_balance = business.opening_balance + total_income - total_expense
        burn_rate = monthly_expense
        profit_margin = (monthly_income - monthly_expense) / monthly_income if monthly_income > 0 else 0.0

        monthly_sales_trend = self._monthly_totals(incomes, 3)

        from app.models.customer import Customer
        cust_result = await self.db.execute(
            select(Customer).where(Customer.business_id == business.id)
        )
        customers = cust_result.scalars().all()
        total_outstanding = sum(c.outstanding_amount for c in customers)

        result = self.health_scorer.calculate(
            cash_in=monthly_income,
            cash_out=monthly_expense,
            total_outstanding=total_outstanding,
            burn_rate=burn_rate,
            cash_balance=cash_balance,
            profit_margin=profit_margin,
            monthly_sales_trend=monthly_sales_trend,
            total_income=total_income,
        )

        risk_score = RiskScore(
            business_id=business.id,
            health_score=result["health_score"],
            risk_score=result["risk_score"],
            rating=result["rating"],
            summary=result["summary"],
            cash_flow_score=result["components"]["cash_flow_score"],
            expense_score=result["components"]["expense_score"],
            sales_score=result["components"]["sales_score"],
            savings_score=result["components"]["savings_score"],
            customer_dues_score=result["components"]["customer_dues_score"],
            profit_margin_score=result["components"]["profit_margin_score"],
            burn_rate=result["burn_rate"],
            runway_days=result["runway_days"],
            profit_margin=result["profit_margin"],
            score_date=today,
        )
        self.db.add(risk_score)
        await self.db.flush()

        return result

    # ── Recommendations ───────────────────────────────────────────────────────

    async def run_recommendations(self, business: Business) -> list[dict[str, Any]]:
        health_data = await self.run_health_score(business)
        incomes = await self._get_incomes(business.id)
        expenses = await self._get_expenses(business.id)

        today = date.today()
        month_start = today.replace(day=1)

        monthly_income = sum(i.amount for i in incomes if i.transaction_date >= month_start)
        monthly_expense = sum(e.amount for e in expenses if e.transaction_date >= month_start)
        total_income = sum(i.amount for i in incomes)
        total_expense = sum(e.amount for e in expenses)
        cash_balance = business.opening_balance + total_income - total_expense

        expense_by_category: dict[str, float] = {}
        for e in expenses:
            expense_by_category[e.category.value] = expense_by_category.get(e.category.value, 0) + e.amount

        anomaly_result = await self.run_anomaly_detection(business.id)
        from app.models.invoice import Invoice, InvoiceStatus
        inv_result = await self.db.execute(
            select(Invoice).where(
                Invoice.business_id == business.id,
                Invoice.status == InvoiceStatus.OVERDUE,
            )
        )
        overdue_invoices = len(inv_result.scalars().all())

        from app.models.customer import Customer
        cust_result = await self.db.execute(
            select(Customer).where(Customer.business_id == business.id)
        )
        customers = cust_result.scalars().all()
        total_outstanding = sum(c.outstanding_amount for c in customers)
        profit_margin = (monthly_income - monthly_expense) / monthly_income if monthly_income > 0 else 0.0

        recs = self.recommender.generate(
            health_score=health_data["health_score"],
            cash_balance=cash_balance,
            burn_rate=health_data["burn_rate"],
            runway_days=health_data["runway_days"],
            total_outstanding=total_outstanding,
            expense_by_category=expense_by_category,
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            anomalies_count=anomaly_result["count"],
            overdue_invoices=overdue_invoices,
            profit_margin=profit_margin,
        )

        # Persist recommendations
        priority_map = {"critical": RecommendationPriority.CRITICAL, "high": RecommendationPriority.HIGH,
                        "medium": RecommendationPriority.MEDIUM, "low": RecommendationPriority.LOW}
        cat_map = {c.value: c for c in RecommendationCategory}

        for rec in recs:
            r = Recommendation(
                business_id=business.id,
                title=rec["title"],
                description=rec["description"],
                category=cat_map.get(rec["category"], RecommendationCategory.CASH_FLOW),
                priority=priority_map.get(rec["priority"], RecommendationPriority.MEDIUM),
                estimated_impact=rec["estimated_impact"],
                confidence=rec["confidence"],
                action_items=json.dumps(rec["action_items"]),
            )
            self.db.add(r)
        await self.db.flush()

        return recs

    # ── Shortage Prediction ───────────────────────────────────────────────────

    async def run_shortage_prediction(self, business: Business) -> dict[str, Any]:
        incomes = await self._get_incomes(business.id)
        expenses = await self._get_expenses(business.id)

        total_income = sum(i.amount for i in incomes)
        total_expense = sum(e.amount for e in expenses)
        cash_balance = business.opening_balance + total_income - total_expense

        income_trend = self._monthly_totals(incomes, 3)
        expense_trend = self._monthly_totals(expenses, 3)

        monthly_income = income_trend[-1] if income_trend else 0.0
        monthly_expense = expense_trend[-1] if expense_trend else 0.0
        burn_rate = monthly_expense

        from app.models.customer import Customer
        cust_result = await self.db.execute(
            select(Customer).where(Customer.business_id == business.id)
        )
        customers = cust_result.scalars().all()
        overdue_amount = sum(c.outstanding_amount for c in customers)

        avg_daily_expense = monthly_expense / 30 if monthly_expense > 0 else 1
        runway_days = cash_balance / avg_daily_expense if avg_daily_expense > 0 else 999

        result = self.shortage_predictor.predict(
            cash_balance=cash_balance,
            burn_rate=burn_rate,
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            overdue_amount=overdue_amount,
            runway_days=runway_days,
            income_trend=income_trend,
            expense_trend=expense_trend,
        )

        # Persist
        prediction = Prediction(
            business_id=business.id,
            prediction_type=PredictionType.CASH_SHORTAGE,
            predicted_value=result["shortage_probability"],
            confidence_score=result["confidence"],
            prediction_date=date.today(),
            forecast_data=json.dumps(result),
            model_name="RuleBasedShortagePredictor",
            model_version="1.0",
        )
        self.db.add(prediction)
        await self.db.flush()

        return result

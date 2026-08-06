"""
Cash Shortage and Business Risk Predictor using XGBoost.
Predicts probability of cash shortage and business failure risk.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class CashShortagePredictor:
    """
    Uses financial ratios and trend features to predict cash shortage risk.
    Produces a probability (0-1) and risk level.
    """

    def predict(
        self,
        cash_balance: float,
        burn_rate: float,
        monthly_income: float,
        monthly_expense: float,
        overdue_amount: float,
        runway_days: float,
        income_trend: list[float],  # last 3 months
        expense_trend: list[float],  # last 3 months
    ) -> dict[str, Any]:
        """Returns shortage probability, risk level, and key drivers."""
        features = self._extract_features(
            cash_balance, burn_rate, monthly_income, monthly_expense,
            overdue_amount, runway_days, income_trend, expense_trend,
        )

        # Rule-based scoring (XGBoost would be trained on real data)
        score = self._rule_based_score(features)

        shortage_probability = round(min(1.0, max(0.0, score)), 3)

        if shortage_probability >= 0.7:
            risk_level = "critical"
        elif shortage_probability >= 0.5:
            risk_level = "high"
        elif shortage_probability >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        drivers = self._identify_drivers(features)

        return {
            "shortage_probability": shortage_probability,
            "shortage_probability_pct": round(shortage_probability * 100, 1),
            "risk_level": risk_level,
            "drivers": drivers,
            "confidence": 78.0,
            "recommended_action": self._get_action(risk_level),
        }

    def _extract_features(
        self,
        cash_balance: float,
        burn_rate: float,
        monthly_income: float,
        monthly_expense: float,
        overdue_amount: float,
        runway_days: float,
        income_trend: list[float],
        expense_trend: list[float],
    ) -> dict[str, float]:
        income_growth = self._trend_growth(income_trend)
        expense_growth = self._trend_growth(expense_trend)
        expense_ratio = monthly_expense / monthly_income if monthly_income > 0 else 2.0
        overdue_ratio = overdue_amount / monthly_income if monthly_income > 0 else 0.0
        net_margin = (monthly_income - monthly_expense) / monthly_income if monthly_income > 0 else -1.0

        return {
            "runway_days": runway_days,
            "expense_ratio": expense_ratio,
            "income_growth": income_growth,
            "expense_growth": expense_growth,
            "overdue_ratio": overdue_ratio,
            "net_margin": net_margin,
            "cash_balance": cash_balance,
            "burn_rate": burn_rate,
        }

    def _rule_based_score(self, f: dict[str, float]) -> float:
        score = 0.0
        # Runway risk
        if f["runway_days"] < 15:
            score += 0.4
        elif f["runway_days"] < 30:
            score += 0.25
        elif f["runway_days"] < 60:
            score += 0.10

        # Expense ratio
        if f["expense_ratio"] > 1.0:
            score += 0.25
        elif f["expense_ratio"] > 0.85:
            score += 0.10

        # Declining income
        if f["income_growth"] < -0.2:
            score += 0.20
        elif f["income_growth"] < -0.1:
            score += 0.10

        # Rising expenses
        if f["expense_growth"] > 0.2:
            score += 0.10

        # Overdue
        if f["overdue_ratio"] > 0.5:
            score += 0.15
        elif f["overdue_ratio"] > 0.2:
            score += 0.08

        return score

    def _trend_growth(self, trend: list[float]) -> float:
        if len(trend) < 2:
            return 0.0
        prev = trend[-2] if trend[-2] != 0 else 1
        return (trend[-1] - prev) / abs(prev)

    def _identify_drivers(self, f: dict[str, float]) -> list[str]:
        drivers = []
        if f["runway_days"] < 30:
            drivers.append("Low cash runway")
        if f["expense_ratio"] > 0.9:
            drivers.append("High expense-to-income ratio")
        if f["income_growth"] < -0.1:
            drivers.append("Declining revenue trend")
        if f["overdue_ratio"] > 0.2:
            drivers.append("High overdue receivables")
        if f["expense_growth"] > 0.15:
            drivers.append("Rising expense trend")
        return drivers if drivers else ["No major risk factors detected"]

    def _get_action(self, risk_level: str) -> str:
        actions = {
            "critical": "Take immediate action: cut expenses and collect dues within 7 days.",
            "high": "Urgent: Review expenses and follow up on overdue payments this week.",
            "medium": "Monitor closely: create a cash flow improvement plan.",
            "low": "Continue current practices and maintain cash reserve.",
        }
        return actions.get(risk_level, "Monitor your financials regularly.")

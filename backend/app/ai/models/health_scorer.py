"""
Business Health Score Calculator.
Produces a 0-100 score with component breakdown and Green/Yellow/Red rating.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HealthComponents:
    cash_flow_score: float = 0.0
    expense_score: float = 0.0
    sales_score: float = 0.0
    savings_score: float = 0.0
    customer_dues_score: float = 0.0
    profit_margin_score: float = 0.0


class BusinessHealthScorer:
    """
    Weights:
      Cash Flow     20%
      Expenses      20%
      Sales         20%
      Savings       15%
      Customer Dues 15%
      Profit Margin 10%
    """

    WEIGHTS = {
        "cash_flow": 0.20,
        "expense": 0.20,
        "sales": 0.20,
        "savings": 0.15,
        "customer_dues": 0.15,
        "profit_margin": 0.10,
    }

    def calculate(
        self,
        cash_in: float,
        cash_out: float,
        total_outstanding: float,
        burn_rate: float,
        cash_balance: float,
        profit_margin: float,  # 0-1
        monthly_sales_trend: list[float],
        total_income: float,
    ) -> dict[str, Any]:
        components = HealthComponents()

        # 1. Cash Flow Score — net flow relative to cash_in
        if cash_in > 0:
            net_ratio = (cash_in - cash_out) / cash_in
            components.cash_flow_score = min(100.0, max(0.0, net_ratio * 100 + 50))
        else:
            components.cash_flow_score = 10.0

        # 2. Expense Score — lower expense ratio = better
        if cash_in > 0:
            expense_ratio = cash_out / cash_in
            components.expense_score = max(0.0, min(100.0, (1 - expense_ratio) * 100))
        else:
            components.expense_score = 20.0

        # 3. Sales Score — based on trend (growing = better)
        if len(monthly_sales_trend) >= 2:
            recent = monthly_sales_trend[-1]
            prev = monthly_sales_trend[-2]
            if prev > 0:
                growth = (recent - prev) / prev
                components.sales_score = min(100.0, max(0.0, 50 + growth * 200))
            else:
                components.sales_score = 50.0
        elif monthly_sales_trend:
            components.sales_score = 50.0
        else:
            components.sales_score = 20.0

        # 4. Savings Score — runway in months
        monthly_burn = burn_rate if burn_rate > 0 else 1
        runway_months = cash_balance / monthly_burn if monthly_burn > 0 else 0
        components.savings_score = min(100.0, runway_months * 20)

        # 5. Customer Dues Score — outstanding vs total income
        if total_income > 0:
            dues_ratio = total_outstanding / total_income
            components.customer_dues_score = max(0.0, min(100.0, (1 - dues_ratio) * 100))
        else:
            components.customer_dues_score = 50.0 if total_outstanding == 0 else 30.0

        # 6. Profit Margin Score
        components.profit_margin_score = min(100.0, max(0.0, profit_margin * 100))

        # Weighted health score
        health_score = (
            components.cash_flow_score * self.WEIGHTS["cash_flow"]
            + components.expense_score * self.WEIGHTS["expense"]
            + components.sales_score * self.WEIGHTS["sales"]
            + components.savings_score * self.WEIGHTS["savings"]
            + components.customer_dues_score * self.WEIGHTS["customer_dues"]
            + components.profit_margin_score * self.WEIGHTS["profit_margin"]
        )
        health_score = round(health_score, 1)

        # Risk score is inverse of health
        risk_score = round(100.0 - health_score, 1)

        # Rating
        if health_score >= 70:
            rating = "green"
        elif health_score >= 45:
            rating = "yellow"
        else:
            rating = "red"

        # Summary
        summary = self._generate_summary(health_score, rating, components)

        return {
            "health_score": health_score,
            "risk_score": risk_score,
            "rating": rating,
            "summary": summary,
            "components": {
                "cash_flow_score": round(components.cash_flow_score, 1),
                "expense_score": round(components.expense_score, 1),
                "sales_score": round(components.sales_score, 1),
                "savings_score": round(components.savings_score, 1),
                "customer_dues_score": round(components.customer_dues_score, 1),
                "profit_margin_score": round(components.profit_margin_score, 1),
            },
            "burn_rate": round(burn_rate, 2),
            "runway_days": round((cash_balance / (burn_rate / 30)) if burn_rate > 0 else 999, 0),
            "profit_margin": round(profit_margin * 100, 1),
        }

    def _generate_summary(self, score: float, rating: str, c: HealthComponents) -> str:
        if rating == "green":
            return f"Business is financially healthy (score: {score}/100). Cash flow is stable."
        elif rating == "yellow":
            weakest = min(
                [("cash flow", c.cash_flow_score), ("expenses", c.expense_score),
                 ("savings", c.savings_score), ("customer dues", c.customer_dues_score)],
                key=lambda x: x[1]
            )
            return (
                f"Business needs attention (score: {score}/100). "
                f"Focus on improving {weakest[0]} management."
            )
        else:
            return (
                f"Business is at high risk (score: {score}/100). "
                "Immediate action required to stabilize cash flow."
            )

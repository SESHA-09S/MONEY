"""
AI Recommendation Engine.
Generates prioritized, actionable financial recommendations
based on the business's current financial state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RecommendationItem:
    title: str
    description: str
    category: str
    priority: str  # critical / high / medium / low
    estimated_impact: float  # INR
    action_items: list[str]
    confidence: float  # 0-100


class RecommendationEngine:
    """
    Rule-based + threshold-driven recommendation engine.
    Produces recommendations sorted by priority and impact.
    """

    def generate(
        self,
        health_score: float,
        cash_balance: float,
        burn_rate: float,
        runway_days: float,
        total_outstanding: float,
        expense_by_category: dict[str, float],
        monthly_income: float,
        monthly_expense: float,
        anomalies_count: int,
        overdue_invoices: int,
        profit_margin: float,
    ) -> list[dict[str, Any]]:
        recommendations: list[RecommendationItem] = []

        # 1. Critical: Low cash runway
        if runway_days < 30:
            recommendations.append(RecommendationItem(
                title="Critical: Cash Runway Below 30 Days",
                description=f"Your cash will last only {int(runway_days)} days at current burn rate. Immediate action is needed.",
                category="cash_flow",
                priority="critical",
                estimated_impact=burn_rate * 2,
                action_items=[
                    "Collect all outstanding payments immediately",
                    "Pause non-essential expenses for 30 days",
                    "Negotiate extended payment terms with suppliers",
                    "Consider a short-term line of credit",
                ],
                confidence=95.0,
            ))
        elif runway_days < 60:
            recommendations.append(RecommendationItem(
                title="Warning: Cash Runway Below 60 Days",
                description=f"Cash runway is {int(runway_days)} days. Start cash conservation measures.",
                category="cash_flow",
                priority="high",
                estimated_impact=burn_rate,
                action_items=[
                    "Accelerate collection of overdue invoices",
                    "Review and cut 20% of variable expenses",
                    "Build a 3-month cash reserve",
                ],
                confidence=88.0,
            ))

        # 2. High: Overdue invoices
        if overdue_invoices > 0:
            impact = total_outstanding * 0.5
            recommendations.append(RecommendationItem(
                title=f"Collect {overdue_invoices} Overdue Invoice(s)",
                description=f"You have {overdue_invoices} overdue invoice(s). Collecting them can improve cash flow significantly.",
                category="customer",
                priority="high" if overdue_invoices < 5 else "critical",
                estimated_impact=impact,
                action_items=[
                    "Send payment reminders via WhatsApp/email today",
                    "Offer a 2% discount for immediate payment",
                    "Set up automatic payment reminders",
                    "Consider partial payment arrangements",
                ],
                confidence=90.0,
            ))

        # 3. Reduce high expense categories
        total_expense = sum(expense_by_category.values()) or 1
        for category, amount in sorted(expense_by_category.items(), key=lambda x: -x[1]):
            ratio = amount / total_expense
            if ratio > 0.35 and category not in ("salary", "inventory"):
                recommendations.append(RecommendationItem(
                    title=f"Reduce {category.replace('_', ' ').title()} Expenses",
                    description=f"{category.replace('_', ' ').title()} accounts for {ratio*100:.0f}% of total expenses.",
                    category="expenses",
                    priority="medium",
                    estimated_impact=amount * 0.15,
                    action_items=[
                        f"Audit all {category} transactions",
                        "Get 3 competitive quotes from vendors",
                        f"Target 15% reduction in {category} spending",
                    ],
                    confidence=75.0,
                ))
                break  # One at a time

        # 4. Anomaly detection alert
        if anomalies_count > 0:
            recommendations.append(RecommendationItem(
                title=f"Review {anomalies_count} Suspicious Expense(s)",
                description="Our AI detected unusual spending patterns. Review these transactions for errors or fraud.",
                category="risk",
                priority="high",
                estimated_impact=monthly_expense * 0.05,
                action_items=[
                    "Review all flagged transactions in the Expense module",
                    "Verify receipts for anomalous entries",
                    "Check for duplicate payments",
                    "Enable two-factor approval for large expenses",
                ],
                confidence=82.0,
            ))

        # 5. Low profit margin
        if profit_margin < 0.10:
            recommendations.append(RecommendationItem(
                title="Improve Profit Margin (Currently Low)",
                description=f"Your profit margin is {profit_margin*100:.1f}%. Target at least 15-20% for sustainability.",
                category="revenue",
                priority="medium",
                estimated_impact=monthly_income * 0.05,
                action_items=[
                    "Review pricing strategy — consider 5-10% price increase",
                    "Identify and cut low-margin products/services",
                    "Focus marketing on high-margin offerings",
                    "Reduce cost of goods through bulk purchasing",
                ],
                confidence=70.0,
            ))

        # 6. Build cash reserve
        if cash_balance < burn_rate * 3:
            recommendations.append(RecommendationItem(
                title="Build 3-Month Cash Reserve",
                description="A healthy business should maintain at least 3 months of operating expenses as a reserve.",
                category="savings",
                priority="medium",
                estimated_impact=burn_rate * 3 - cash_balance,
                action_items=[
                    "Set aside 10% of monthly revenue to savings",
                    "Open a separate business savings account",
                    "Automate monthly transfer to reserve fund",
                ],
                confidence=85.0,
            ))

        # 7. Growth recommendation if healthy
        if health_score > 70 and profit_margin > 0.15:
            recommendations.append(RecommendationItem(
                title="Invest in Growth — Business is Healthy",
                description="Your financials are strong. Consider investing in marketing or expansion.",
                category="growth",
                priority="low",
                estimated_impact=monthly_income * 0.2,
                action_items=[
                    "Increase marketing budget by 15-20%",
                    "Explore new customer segments",
                    "Consider hiring additional staff for growth",
                ],
                confidence=65.0,
            ))

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda r: (priority_order.get(r.priority, 4), -r.estimated_impact))

        return [
            {
                "title": r.title,
                "description": r.description,
                "category": r.category,
                "priority": r.priority,
                "estimated_impact": round(r.estimated_impact, 2),
                "action_items": r.action_items,
                "confidence": r.confidence,
            }
            for r in recommendations
        ]

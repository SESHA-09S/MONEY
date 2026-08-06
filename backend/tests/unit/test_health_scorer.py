"""Unit tests for BusinessHealthScorer."""
import pytest
from app.ai.models.health_scorer import BusinessHealthScorer


@pytest.fixture
def scorer():
    return BusinessHealthScorer()


def test_healthy_business(scorer):
    result = scorer.calculate(
        cash_in=100_000,
        cash_out=60_000,
        total_outstanding=5_000,
        burn_rate=60_000,
        cash_balance=200_000,
        profit_margin=0.40,
        monthly_sales_trend=[80_000, 90_000, 100_000],
        total_income=500_000,
    )
    assert result["health_score"] >= 60
    assert result["rating"] in ("green", "yellow")
    assert 0 <= result["risk_score"] <= 100


def test_unhealthy_business(scorer):
    result = scorer.calculate(
        cash_in=10_000,
        cash_out=50_000,
        total_outstanding=80_000,
        burn_rate=50_000,
        cash_balance=5_000,
        profit_margin=-0.5,
        monthly_sales_trend=[30_000, 20_000, 10_000],
        total_income=60_000,
    )
    assert result["health_score"] < 50
    assert result["rating"] == "red"


def test_score_is_bounded(scorer):
    result = scorer.calculate(
        cash_in=0, cash_out=0, total_outstanding=0,
        burn_rate=0, cash_balance=0, profit_margin=0,
        monthly_sales_trend=[], total_income=0,
    )
    assert 0 <= result["health_score"] <= 100
    assert 0 <= result["risk_score"] <= 100


def test_components_present(scorer):
    result = scorer.calculate(
        cash_in=50_000, cash_out=30_000, total_outstanding=10_000,
        burn_rate=30_000, cash_balance=50_000, profit_margin=0.2,
        monthly_sales_trend=[40_000, 45_000, 50_000], total_income=200_000,
    )
    assert "components" in result
    assert all(k in result["components"] for k in [
        "cash_flow_score", "expense_score", "sales_score",
        "savings_score", "customer_dues_score", "profit_margin_score",
    ])

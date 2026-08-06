"""Unit tests for AnomalyDetector."""
import pytest
from app.ai.models.anomaly_detector import AnomalyDetector


@pytest.fixture
def detector():
    return AnomalyDetector()


@pytest.fixture
def normal_expenses():
    return [
        {"id": i, "amount": 1000 + i * 10, "category": "rent",
         "transaction_date": f"2024-0{(i % 9) + 1}-{(i % 28) + 1:02d}",
         "vendor_name": f"Vendor{i % 5}"}
        for i in range(1, 20)
    ]


def test_detect_returns_flags(detector, normal_expenses):
    results = detector.detect(normal_expenses)
    assert len(results) == len(normal_expenses)
    for r in results:
        assert "is_anomaly" in r
        assert "anomaly_score" in r
        assert 0.0 <= r["anomaly_score"] <= 1.0


def test_spike_detected(detector, normal_expenses):
    # Add a massive spike
    normal_expenses.append({
        "id": 999, "amount": 999_999, "category": "rent",
        "transaction_date": "2024-06-15", "vendor_name": "Unknown",
    })
    results = detector.detect(normal_expenses)
    spike = next(r for r in results if r["id"] == 999)
    assert spike["anomaly_score"] > 0.5


def test_small_dataset_no_crash(detector):
    tiny = [{"id": 1, "amount": 500, "category": "fuel",
             "transaction_date": "2024-01-01", "vendor_name": None}]
    results = detector.detect(tiny)
    assert results[0]["is_anomaly"] == False


def test_duplicate_detection(detector):
    expenses = [
        {"id": 1, "amount": 5000, "category": "rent", "transaction_date": "2024-01-01", "vendor_name": "LandLord"},
        {"id": 2, "amount": 5000, "category": "rent", "transaction_date": "2024-01-02", "vendor_name": "LandLord"},
        {"id": 3, "amount": 200, "category": "fuel", "transaction_date": "2024-01-05", "vendor_name": "PetrolStation"},
    ]
    duplicates = detector.check_duplicates(expenses)
    assert 2 in duplicates

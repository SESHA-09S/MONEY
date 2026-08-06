"""
Expense Anomaly Detector using Isolation Forest.
Detects sudden spikes, duplicates, and unusual spending patterns.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Uses Isolation Forest to flag anomalous expenses.
    Returns anomaly scores and a boolean flag per record.
    """

    CONTAMINATION = 0.05  # Expect ~5% anomalies

    def detect(self, expenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Args:
            expenses: List of dicts with keys: id, amount, category, transaction_date
        Returns:
            Same list with added keys: is_anomaly (bool), anomaly_score (float 0-1)
        """
        if len(expenses) < 5:
            for e in expenses:
                e["is_anomaly"] = False
                e["anomaly_score"] = 0.0
            return expenses

        df = pd.DataFrame(expenses)

        # Feature engineering
        df["day_of_week"] = pd.to_datetime(df["transaction_date"]).dt.dayofweek
        df["day_of_month"] = pd.to_datetime(df["transaction_date"]).dt.day
        df["month"] = pd.to_datetime(df["transaction_date"]).dt.month

        # Category encoding (ordinal for simplicity)
        categories = df["category"].unique().tolist()
        cat_map = {c: i for i, c in enumerate(categories)}
        df["category_encoded"] = df["category"].map(cat_map)

        # Category-level z-score (amount relative to category average)
        df["cat_mean"] = df.groupby("category")["amount"].transform("mean")
        df["cat_std"] = df.groupby("category")["amount"].transform("std").fillna(1)
        df["amount_z"] = (df["amount"] - df["cat_mean"]) / df["cat_std"].clip(lower=0.01)

        features = ["amount", "day_of_week", "day_of_month", "month", "amount_z", "category_encoded"]
        X = df[features].fillna(0).values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = IsolationForest(
            contamination=self.CONTAMINATION,
            random_state=42,
            n_estimators=100,
        )
        predictions = model.fit_predict(X_scaled)
        scores = model.score_samples(X_scaled)  # More negative = more anomalous

        # Normalize scores to 0-1 (1 = most anomalous)
        min_score, max_score = scores.min(), scores.max()
        score_range = max_score - min_score
        if score_range > 0:
            normalized = (max_score - scores) / score_range
        else:
            normalized = np.zeros_like(scores)

        for i, expense in enumerate(expenses):
            expense["is_anomaly"] = bool(predictions[i] == -1)
            expense["anomaly_score"] = round(float(normalized[i]), 4)

        return expenses

    def check_duplicates(self, expenses: list[dict[str, Any]]) -> list[int]:
        """Returns IDs of likely duplicate payments (same amount + vendor within 3 days)."""
        duplicates = []
        df = pd.DataFrame(expenses)
        if len(df) < 2:
            return []
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
        df = df.sort_values("transaction_date")

        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                row_i = df.iloc[i]
                row_j = df.iloc[j]
                days_diff = abs((row_j["transaction_date"] - row_i["transaction_date"]).days)
                if days_diff > 3:
                    break
                if (
                    row_i["amount"] == row_j["amount"]
                    and row_i.get("vendor_name") == row_j.get("vendor_name")
                    and row_i.get("vendor_name") is not None
                ):
                    duplicates.append(int(row_j["id"]))
        return list(set(duplicates))

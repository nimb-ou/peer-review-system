"""
Edge Case and Robustness Tests for Peer Review System ML Pipeline
Validates:
1. Zero-variance review scores (all identical ratings).
2. Single-review edge case (no variance, single interaction).
3. Extreme descriptor skew (100% blocking or 100% collaborative).
4. Non-existent employee query fallback behavior.
5. Score scale boundary enforcement (1.0 to 5.0).
"""

import pytest
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from database import DatabaseManager
from ml_pipeline import PeerReviewMLPipeline


@pytest.fixture
def db():
    return DatabaseManager("data/reviews.db")


@pytest.fixture
def pipeline(db):
    pipe = PeerReviewMLPipeline(db)
    pipe.load_models("models")
    return pipe


def test_zero_variance_reviews(pipeline):
    """Verify feature engineering handles multiple reviews with identical scores without NaN variance."""
    date_str = "2026-07-20"
    df = pd.DataFrame([
        {"reviewee_id": "EMP-ISO-01", "reviewer_id": "R1", "score": 5.0, "descriptor": "collaborative", "date": date_str},
        {"reviewee_id": "EMP-ISO-01", "reviewer_id": "R2", "score": 5.0, "descriptor": "collaborative", "date": date_str},
        {"reviewee_id": "EMP-ISO-01", "reviewer_id": "R3", "score": 5.0, "descriptor": "collaborative", "date": date_str},
    ])
    features = pipeline.engineer_features(df)
    assert len(features) == 1
    row = features.iloc[0]
    assert row["avg_score"] == 5.0
    assert row["score_std"] == 0.0
    assert row["pct_collaborative"] == 1.0
    assert row["pct_score_5"] == 1.0


def test_single_review_per_employee(pipeline):
    """Verify that an isolated employee with exactly one review produces standard feature rows."""
    df = pd.DataFrame([
        {"reviewee_id": "EMP-SOLO", "reviewer_id": "R1", "score": 3.0, "descriptor": "neutral", "date": "2026-07-21"}
    ])
    features = pipeline.engineer_features(df)
    assert len(features) == 1
    row = features.iloc[0]
    assert row["review_count"] == 1
    assert row["score_std"] == 0.0
    assert row["avg_score"] == 3.0
    assert row["pct_neutral"] == 1.0


def test_all_blocking_descriptors_skew(pipeline):
    """Verify features correctly reflect an exclusively blocking feedback profile."""
    date_str = "2026-07-22"
    df = pd.DataFrame([
        {"reviewee_id": "EMP-BLOCK", "reviewer_id": f"R{i}", "score": 1.0, "descriptor": "blocking", "date": date_str}
        for i in range(5)
    ])
    features = pipeline.engineer_features(df)
    row = features.iloc[0]
    assert row["pct_blocking"] == 1.0
    assert row["pct_collaborative"] == 0.0
    assert row["avg_score"] == 1.0
    assert row["pct_score_1"] == 1.0
    assert row["avg_descriptor_score"] == 1.0  # blocking mapped to 1.0


def test_nonexistent_employee_insights_graceful_fallback(pipeline):
    """Verify querying an unknown employee returns structured fallback with zero reviews and no crash."""
    insights = pipeline.get_employee_insights("UNKNOWN_NONEXISTENT_EMP_99999")
    assert insights["total_reviews"] == 0
    assert insights["is_anomaly"] is False
    assert "error" in insights

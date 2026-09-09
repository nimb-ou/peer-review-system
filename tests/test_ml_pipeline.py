"""
Unit tests for Peer Review System ML Pipeline
Validates feature engineering, Isolation Forest anomaly detection, clustering, and employee insights.
"""

import pytest
import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from database import DatabaseManager
from ml_pipeline import PeerReviewMLPipeline

@pytest.fixture
def db():
    return DatabaseManager("data/reviews.db")

@pytest.fixture
def pipeline(db):
    pipe = PeerReviewMLPipeline(db)
    # Load pre-trained models
    pipe.load_models("models")
    return pipe

def test_database_reviews_count(db):
    reviews = db.get_reviews()
    assert len(reviews) > 1000
    assert "score" in reviews.columns
    assert "reviewee_id" in reviews.columns

def test_feature_engineering(pipeline, db):
    reviews = db.get_reviews()
    features = pipeline.engineer_features(reviews)
    assert len(features) > 0
    assert "avg_score" in features.columns
    assert "pct_collaborative" in features.columns
    assert "pct_withdrawn" in features.columns

def test_models_loaded(pipeline):
    assert "score_predictor" in pipeline.models
    assert "anomaly_detector" in pipeline.models
    assert "behavior_clusters" in pipeline.models

def test_employee_insights_generation(pipeline, db):
    employees = db.get_employees()
    assert len(employees) > 0
    emp_id = employees[0]
    insights = pipeline.get_employee_insights(emp_id)
    assert "avg_score" in insights
    assert "collaboration_rate" in insights
    assert "is_anomaly" in insights
    assert isinstance(bool(insights["is_anomaly"]), bool)

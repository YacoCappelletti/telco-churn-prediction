"""API tests for the Telco churn prediction service (Phase 5)."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api.main import app  # noqa: E402


VALID_PAYLOAD = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 4,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 89.5,
    "TotalCharges": 350.5,
}


def test_health_ok():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] in {"ok", "degraded"}
        assert body["model_loaded"] is True
        assert body["model_name"] == "telco_churn_classifier"


def test_predict_valid_customer():
    with TestClient(app) as client:
        response = client.post("/v1/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200
        body = response.json()
        prob = body["customer_risk"]["churn_probability"]
        assert 0.0 <= prob <= 1.0
        assert body["customer_risk"]["prediction"] in {"Yes", "No"}
        assert body["customer_risk"]["risk_level"] in {"high", "medium", "low"}
        assert len(body["contributing_factors"]) >= 1
        assert all(
            f["direction"] in {"increases_risk", "decreases_risk"}
            for f in body["contributing_factors"]
        )
        assert "business_recommendation" in body
        assert body["model_version"] == "1.0.0"


def test_predict_high_risk_profile():
    """New month-to-month fiber customer with manual payment must be high risk."""
    with TestClient(app) as client:
        payload = dict(VALID_PAYLOAD)
        payload.update({"tenure": 2, "TotalCharges": 180.0})
        response = client.post("/v1/predict", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["customer_risk"]["risk_level"] in {"high", "medium"}
        assert body["business_recommendation"]


def test_predict_invalid_categorical():
    with TestClient(app) as client:
        payload = dict(VALID_PAYLOAD)
        payload["Contract"] = "Three year"  # not in the data dictionary domain
        response = client.post("/v1/predict", json=payload)
        assert response.status_code == 422


def test_predict_out_of_range_numeric():
    with TestClient(app) as client:
        payload = dict(VALID_PAYLOAD)
        payload["tenure"] = 500  # exceeds 72 months
        response = client.post("/v1/predict", json=payload)
        assert response.status_code == 422


def test_predict_missing_field():
    with TestClient(app) as client:
        payload = dict(VALID_PAYLOAD)
        payload.pop("MonthlyCharges")
        response = client.post("/v1/predict", json=payload)
        assert response.status_code == 422


def test_model_card():
    with TestClient(app) as client:
        response = client.get("/v1/model-card")
        assert response.status_code == 200
        body = response.json()
        assert body["model_name"] == "telco_churn_classifier"
        assert body["approved_target"] == "Churn"
        assert body["problem_type"] == "classification"
        assert "test_metrics" in body

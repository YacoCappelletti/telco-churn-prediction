"""Prediction logic for the Telco churn API (model loading + explanation)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.model.pipeline import (
    CATEGORICAL_FEATURES,
    FEATURES,
    NUMERIC_FEATURES,
    ROOT,
    load_config,
    risk_band,
)

logger = logging.getLogger("telco_api")

MODEL_PATH = ROOT / "models" / "final_model.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"

FRIENDLY_NAMES = {
    "tenure": "Tenure",
    "MonthlyCharges": "Monthly bill",
    "TotalCharges": "Lifetime charges",
    "SeniorCitizen": "Senior status",
    "gender": "Gender",
    "Partner": "Partner",
    "Dependents": "Dependents",
    "PhoneService": "Phone service",
    "MultipleLines": "Multiple lines",
    "InternetService": "Internet service",
    "OnlineSecurity": "Online security",
    "OnlineBackup": "Online backup",
    "DeviceProtection": "Device protection",
    "TechSupport": "Tech support",
    "StreamingTV": "Streaming TV",
    "StreamingMovies": "Streaming movies",
    "Contract": "Contract type",
    "PaperlessBilling": "Paperless billing",
    "PaymentMethod": "Payment method",
}

RECOMMENDATIONS = {
    "high": (
        "Contact this customer within 48 hours. Lead with a contract-migration "
        "offer (1-2 year term with discount) plus a protection bundle "
        "(OnlineSecurity / TechSupport); if paying by electronic check, also "
        "propose automatic payments."
    ),
    "medium": (
        "Include this customer in the next retention wave. Offer a protection "
        "bundle at a promotional first-year price and migration to automatic "
        "payments; monitor at the next billing cycle."
    ),
    "low": (
        "No immediate retention action required. Keep standard lifecycle "
        "messaging and re-score after the next billing cycle."
    ),
}


def load_model() -> object | None:
    if not MODEL_PATH.exists():
        logger.warning("Model artifact not found at %s", MODEL_PATH)
        return None
    logger.info("Loading model from %s", MODEL_PATH)
    return joblib.load(MODEL_PATH)


def load_metadata() -> dict:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text())
    return {"model_name": "telco_churn_classifier", "model_version": "unknown"}


def _contribution_labels(names: list[str]) -> dict[str, str]:
    """Map encoded feature names back to friendly, human-readable labels."""
    labels: dict[str, str] = {}
    for name in names:
        if name in FRIENDLY_NAMES:  # numeric feature
            labels[name] = FRIENDLY_NAMES[name]
        else:  # one-hot column: "FeatureValue" or "Feature_Value"
            for feature in CATEGORICAL_FEATURES:
                if name.startswith(feature):
                    value = name[len(feature) :].lstrip("_")
                    labels[name] = f"{FRIENDLY_NAMES[feature]} = {value}"
                    break
    return labels


def predict_one(
    model,
    payload: dict,
    config: dict | None = None,
    metadata: dict | None = None,
) -> dict:
    """Score one customer and build the prediction response body.

    `config` and `metadata` are injected by the API from app.state (loaded
    once at startup); when omitted they fall back to a disk read so direct
    calls keep working.
    """
    config = config or load_config()
    metadata = metadata or load_metadata()
    df = pd.DataFrame([payload])[FEATURES]

    prob = float(model.predict_proba(df)[0, 1])
    band = risk_band(prob, config)

    # Per-feature logit contributions (linear model: coef * scaled_value),
    # aggregated back to the original feature groups.
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    x_enc = preprocessor.transform(df)[0]
    onehot = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    encoded_names = list(NUMERIC_FEATURES) + list(
        onehot.get_feature_names_out(CATEGORICAL_FEATURES)
    )
    contributions = classifier.coef_[0] * x_enc

    per_feature: dict[str, float] = {}
    for name, value in zip(encoded_names, contributions):
        if name in NUMERIC_FEATURES:
            per_feature[name] = per_feature.get(name, 0.0) + float(value)
        else:
            for feature in CATEGORICAL_FEATURES:
                if name.startswith(feature):
                    # Inactive one-hot columns contribute 0 by construction, so
                    # accumulate unconditionally: this keeps protective
                    # categories (negative logit contribution) in the ranking.
                    per_feature[feature] = per_feature.get(feature, 0.0) + float(value)
                    break

    labels = _contribution_labels(encoded_names)
    ranked = sorted(per_feature.items(), key=lambda kv: kv[1], reverse=True)
    positives = [
        {
            "feature": f,
            "direction": "increases_risk",
            "description": f"{labels.get(f, f)} pushes churn risk up",
        }
        for f, v in ranked[:3]
        if v > 0
    ]
    negatives = [
        {
            "feature": f,
            "direction": "decreases_risk",
            "description": f"{labels.get(f, f)} pulls churn risk down",
        }
        for f, v in reversed(ranked[-3:])
        if v < 0
    ]

    prediction = "Yes" if prob >= 0.5 else "No"
    drivers = ", ".join(f.replace("_", " ") for f, _ in ranked[:2]) or "n/a"
    recommendation = RECOMMENDATIONS[band]

    return {
        "customer_risk": {
            "churn_probability": round(prob, 4),
            "prediction": prediction,
            "risk_level": band,
        },
        "contributing_factors": positives + negatives,
        "business_recommendation": recommendation,
        "model_version": metadata.get("model_version", "unknown"),
        "model_name": metadata.get("model_name", "telco_churn_classifier"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

"""Model artifact tests (Phase 4 outputs, kept executable)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.model.pipeline import (  # noqa: E402
    ROOT,
    build_preprocessor,
    get_splits,
    load_config,
)

MODELS = ROOT / "models"


def test_model_artifact_exists_and_loads():
    model = joblib.load(MODELS / "final_model.joblib")
    assert model is not None


def test_metadata_fields():
    metadata = json.loads((MODELS / "model_metadata.json").read_text())
    required = [
        "model_name",
        "model_version",
        "approved_target",
        "problem_type",
        "target_approval_reference",
        "training_timestamp",
        "feature_list",
        "preprocessing_summary",
        "validation_metrics",
        "test_metrics",
        "library_versions",
        "notes_and_limitations",
    ]
    for field in required:
        assert field in metadata, f"Missing metadata field: {field}"
    assert metadata["approved_target"] == "Churn"


def test_target_approval_is_recorded():
    approval = json.loads((ROOT / "docs" / "json" / "target_approval.json").read_text())
    assert approval["approval_status"] == "approved"
    assert approval["approved_target"] == "Churn"


def test_preprocessor_transforms_one_row():
    config = load_config()
    X_train, _X_val, _X_test, _y_train, _y_val, _y_test = get_splits(config)
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)
    transformed = preprocessor.transform(X_train.iloc[:1])
    assert transformed.shape[1] > len(X_train.columns)  # one-hot expanded


def test_model_predicts_valid_probabilities():
    config = load_config()
    _X_train, _X_val, X_test, _y_train, _y_val, y_test = get_splits(config)
    model = joblib.load(MODELS / "final_model.joblib")
    prob = model.predict_proba(X_test)[:, 1]
    assert prob.shape == (len(X_test),)
    assert ((prob >= 0) & (prob <= 1)).all()
    # Metrics recorded during training are in valid ranges
    perf = json.loads((ROOT / "docs" / "json" / "model_performance.json").read_text())
    tm = perf["final_test_metrics"]
    assert 0 <= tm["average_precision"] <= 1
    assert 0 <= tm["roc_auc"] <= 1
    assert perf["final_test_metrics"]["average_precision"] > 0.5

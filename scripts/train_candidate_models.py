"""Phase 4 - Candidate models for the approved target (Churn, classification).

Trains three candidates per the plan (Logistic Regression, Decision Tree,
Random Forest) inside full preprocessing pipelines, evaluated with 5-fold
stratified cross-validation on the training set, then validated once on the
validation set. Selects the best model by the business-aligned metric
(average precision / PR-AUC, given the moderate class imbalance).

Outputs:
- models/preprocessor.joblib (fit on the training set)
- docs/json/candidate_models.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from src.model.pipeline import build_preprocessor, get_splits, load_config

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "json" / "candidate_models.json"
PREPROCESSOR_PATH = ROOT / "models" / "preprocessor.joblib"

SCORING = ["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"]


def make_candidates(config: dict) -> dict[str, Pipeline]:
    p = config["candidates"]
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=p["logistic_regression"]["max_iter"],
                        C=p["logistic_regression"]["C"],
                        random_state=config["random_state"],
                    ),
                ),
            ]
        ),
        "decision_tree": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                (
                    "classifier",
                    DecisionTreeClassifier(
                        max_depth=p["decision_tree"]["max_depth"],
                        min_samples_leaf=p["decision_tree"]["min_samples_leaf"],
                        random_state=config["random_state"],
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=p["random_forest"]["n_estimators"],
                        min_samples_leaf=p["random_forest"]["min_samples_leaf"],
                        random_state=config["random_state"],
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def classification_metrics(y_true, prob) -> dict:
    pred = (prob >= 0.5).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_true, pred)), 4),
        "precision": round(float(precision_score(y_true, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, prob)), 4),
        "average_precision": round(float(average_precision_score(y_true, prob)), 4),
    }


def main() -> None:
    config = load_config()
    X_train, X_val, _X_test, y_train, y_val, _y_test = get_splits(config)

    cv = StratifiedKFold(
        n_splits=config["cv_folds"], shuffle=True, random_state=config["random_state"]
    )
    results = {}
    candidates = make_candidates(config)
    for name, pipe in candidates.items():
        cv_res = cross_validate(
            pipe, X_train, y_train, cv=cv, scoring=SCORING, n_jobs=-1
        )
        cv_summary = {
            m: {
                "mean": round(float(cv_res[f"test_{m}"].mean()), 4),
                "std": round(float(cv_res[f"test_{m}"].std()), 4),
            }
            for m in SCORING
        }
        pipe.fit(X_train, y_train)
        val_metrics = classification_metrics(y_val, pipe.predict_proba(X_val)[:, 1])
        results[name] = {"cv_train": cv_summary, "validation": val_metrics}
        print(
            f"{name:20s} CV AP={cv_summary['average_precision']['mean']:.4f} "
            f"(+/-{cv_summary['average_precision']['std']:.4f}) "
            f"| Val AP={val_metrics['average_precision']:.4f}"
        )

    best = max(
        results,
        key=lambda n: results[n]["validation"]["average_precision"],
    )
    # Persist the fitted preprocessor (fit on train) for inspection/reuse
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train, y_train)
    PREPROCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": config["approved_target"],
        "target_approval_reference": config["target_approval_reference"],
        "primary_metric": config["primary_metric"],
        "candidates": results,
        "selected_candidate": best,
        "selection_rule": "highest validation average_precision (PR-AUC), business-aligned per docs/data_quality_report.md imbalance note",
        "baseline_reference": "docs/json/baseline_metrics.json",
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Selected: {best}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {PREPROCESSOR_PATH}")


if __name__ == "__main__":
    main()

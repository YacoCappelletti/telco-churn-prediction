"""Phase 4 - Baseline model for the approved target (Churn, classification).

Baseline: DummyClassifier with the 'prior' strategy (predicts the class
frequency, i.e. always No-like behavior at the base rate). Evaluated with
5-fold stratified cross-validation on the training set plus one validation
pass. No feature learning: this is the floor every candidate must beat.

Outputs:
- docs/json/baseline_metrics.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate

from src.model.pipeline import get_splits, load_config

OUT_JSON = (
    Path(__file__).resolve().parents[1] / "docs" / "json" / "baseline_metrics.json"
)


def main() -> None:
    config = load_config()
    X_train, X_val, _X_test, y_train, y_val, _y_test = get_splits(config)

    dummy = DummyClassifier(strategy="prior", random_state=config["random_state"])

    cv = StratifiedKFold(
        n_splits=config["cv_folds"], shuffle=True, random_state=config["random_state"]
    )
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"]
    cv_res = cross_validate(dummy, X_train, y_train, cv=cv, scoring=scoring)
    cv_metrics = {
        m: {
            "mean": round(float(cv_res[f"test_{m}"].mean()), 4),
            "std": round(float(cv_res[f"test_{m}"].std()), 4),
        }
        for m in scoring
    }

    dummy.fit(X_train, y_train)
    prob_val = dummy.predict_proba(X_val)[:, 1]
    pred_val = (prob_val >= 0.5).astype(int)
    val_metrics = {
        "accuracy": accuracy_score(y_val, pred_val),
        "precision": precision_score(y_val, pred_val, zero_division=0),
        "recall": recall_score(y_val, pred_val, zero_division=0),
        "f1": f1_score(y_val, pred_val, zero_division=0),
        "roc_auc": roc_auc_score(y_val, prob_val),
        "average_precision": average_precision_score(y_val, prob_val),
    }
    val_metrics = {k: round(float(v), 4) for k, v in val_metrics.items()}

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "DummyClassifier(strategy='prior')",
        "target": config["approved_target"],
        "positive_class": config["positive_class"],
        "cv_train": cv_metrics,
        "validation": val_metrics,
        "note": "Floor metric: any candidate model must beat these on the primary metric (average_precision).",
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {OUT_JSON}")
    print(
        f"Baseline CV AP={cv_metrics['average_precision']['mean']:.4f} "
        f"| Val AP={val_metrics['average_precision']:.4f} "
        f"(expected ~ base rate 0.265)"
    )


if __name__ == "__main__":
    main()

"""Phase 4 - Final model evaluation (single pass on the held-out test set).

Hard gate: refuses to run unless docs/json/target_approval.json has
approval_status == "approved" (Phase 3 gate).

Refits the selected candidate on train + validation, evaluates ONCE on the
test set, computes permutation importance, and writes all Phase 4 artifacts:
- models/final_model.joblib
- models/preprocessor.joblib (refit on train+val)
- models/model_metadata.json
- docs/json/model_performance.json
- docs/json/feature_importance.json
- docs/images/model_performance_charts.png
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline

from src.model.pipeline import get_splits, load_config
from train_candidate_models import make_candidates

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MODELS = ROOT / "models"
IMAGES = DOCS / "images"
JSON_DIR = DOCS / "json"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#CBD5E1",
        "axes.grid": True,
        "grid.color": "#E2E8F0",
        "axes.axisbelow": True,
        "font.size": 10,
        "axes.titlesize": 11.5,
        "axes.titleweight": "bold",
    }
)


def main() -> None:
    approval = json.loads((JSON_DIR / "target_approval.json").read_text())
    if approval["approval_status"] != "approved":
        raise SystemExit(
            "Phase 4 blocked: target variable is not approved "
            "(docs/json/target_approval.json). Phase 3 approval is required."
        )

    config = load_config()
    candidates_summary = json.loads((JSON_DIR / "candidate_models.json").read_text())
    baseline = json.loads((JSON_DIR / "baseline_metrics.json").read_text())
    best_name = candidates_summary["selected_candidate"]

    X_train, X_val, X_test, y_train, y_val, y_test = get_splits(config)
    X_trainval = pd.concat([X_train, X_val], axis=0)
    y_trainval = pd.concat([y_train, y_val], axis=0)

    final_model: Pipeline = make_candidates(config)[best_name]
    final_model.fit(X_trainval, y_trainval)

    # ---- Single evaluation on the test set ---------------------------------
    prob_test = final_model.predict_proba(X_test)[:, 1]
    pred_test = (prob_test >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred_test).ravel()
    test_metrics = {
        "accuracy": round(float((tp + tn) / len(y_test)), 4),
        "precision": round(float(tp / max(tp + fp, 1)), 4),
        "recall": round(float(tp / max(tp + fn, 1)), 4),
        "f1": round(float(2 * tp / max(2 * tp + fp + fn, 1)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, prob_test)), 4),
        "average_precision": round(
            float(average_precision_score(y_test, prob_test)), 4
        ),
    }
    brier = round(float(brier_score_loss(y_test, prob_test)), 4)

    # Business view: top-decile capture (rank customers by risk)
    order = prob_test.argsort()[::-1]
    top_decile = order[: max(1, len(order) // 10)]
    top_decile_capture = round(float(y_test.iloc[top_decile].sum() / y_test.sum()), 4)
    lift = round(top_decile_capture / 0.10, 2)

    # ---- Permutation importance (robust method) ----------------------------
    perm = permutation_importance(
        final_model,
        X_test,
        y_test,
        n_repeats=config["permutation_importance"]["n_repeats"],
        scoring=config["permutation_importance"]["scoring"],
        random_state=config["random_state"],
        n_jobs=-1,
    )
    importance = sorted(
        zip(X_test.columns, perm.importances_mean, perm.importances_std),
        key=lambda t: t[1],
        reverse=True,
    )
    feature_importance = {
        "method": "permutation_importance",
        "scoring": config["permutation_importance"]["scoring"],
        "n_repeats": config["permutation_importance"]["n_repeats"],
        "computed_on": "test set (single pass)",
        "importances": [
            {"feature": f, "mean": round(float(m), 4), "std": round(float(s), 4)}
            for f, m, s in importance
        ],
    }

    # ---- Persist artifacts -------------------------------------------------
    MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODELS / "final_model.joblib")
    preprocessor = final_model.named_steps["preprocessor"]
    joblib.dump(preprocessor, MODELS / "preprocessor.joblib")

    lib_versions = {}
    import sklearn

    lib_versions.update(
        {
            "pandas": pd.__version__,
            "scikit-learn": sklearn.__version__,
            "joblib": joblib.__version__,
        }
    )

    metrics_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "approved_target": config["approved_target"],
        "positive_class": config["positive_class"],
        "selected_model": best_name,
        "split": {"train": len(X_train), "validation": len(X_val), "test": len(X_test)},
        "baseline": {
            "model": baseline["model"],
            "validation_average_precision": baseline["validation"]["average_precision"],
        },
        "candidates_validation": {
            name: r["validation"]
            for name, r in candidates_summary["candidates"].items()
        },
        "final_test_metrics": test_metrics,
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "calibration": {"brier_score": brier},
        "business_view": {
            "top_decile_churn_capture": top_decile_capture,
            "top_decile_lift": lift,
            "interpretation": (
                f"Targeting the riskiest 10% of customers catches "
                f"{top_decile_capture:.0%} of all churners (lift {lift}x vs random)."
            ),
        },
        "curves": {
            "precision_recall": {
                "precision": [
                    round(float(v), 4)
                    for v in precision_recall_curve(y_test, prob_test)[0]
                ],
                "recall": [
                    round(float(v), 4)
                    for v in precision_recall_curve(y_test, prob_test)[1]
                ],
            },
            "roc": {
                "fpr": [round(float(v), 4) for v in roc_curve(y_test, prob_test)[0]],
                "tpr": [round(float(v), 4) for v in roc_curve(y_test, prob_test)[1]],
            },
        },
    }
    (JSON_DIR / "model_performance.json").write_text(
        json.dumps(metrics_payload, indent=2) + "\n"
    )
    (JSON_DIR / "feature_importance.json").write_text(
        json.dumps(feature_importance, indent=2) + "\n"
    )

    metadata = {
        "model_name": config["model_name"],
        "model_version": config["model_version"],
        "approved_target": config["approved_target"],
        "problem_type": config["problem_type"],
        "target_approval_reference": config["target_approval_reference"],
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "selected_model": best_name,
        "feature_list": list(X_train.columns),
        "preprocessing_summary": {
            "numeric": "median imputation + standard scaling (tenure, MonthlyCharges, TotalCharges, SeniorCitizen)",
            "categorical": "one-hot encoding, unknown categories ignored (15 service/contract/payment columns)",
            "total_features_after_encoding": int(
                preprocessor.transform(X_test.iloc[:1]).shape[1]
            ),
        },
        "validation_metrics": candidates_summary["candidates"][best_name]["validation"],
        "cv_metrics": candidates_summary["candidates"][best_name]["cv_train"],
        "test_metrics": test_metrics,
        "library_versions": lib_versions,
        "notes_and_limitations": [
            "Single-snapshot data: no temporal validation possible.",
            "Moderate class imbalance (26.5% positive): PR-AUC used as primary metric.",
            "Probabilities used for ranking with risk bands (high >= 0.60, medium >= 0.35).",
            "TotalCharges kept as feature with documented collinearity vs tenure.",
        ],
    }
    (MODELS / "model_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    # ---- Charts ------------------------------------------------------------
    pr_p, pr_r, _ = precision_recall_curve(y_test, prob_test)
    fpr, tpr, _ = roc_curve(y_test, prob_test)
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 9.5))

    axes[0, 0].plot(pr_r, pr_p, color="#0F6E84", lw=2)
    axes[0, 0].axhline(float(y_test.mean()), color="#E4572E", ls="--", lw=1.2)
    axes[0, 0].text(
        0.98,
        float(y_test.mean()) + 0.03,
        f"Base rate {float(y_test.mean()):.2f}",
        ha="right",
        transform=axes[0, 0].transAxes,
        color="#E4572E",
        fontsize=9,
    )
    axes[0, 0].set_xlabel("Recall")
    axes[0, 0].set_ylabel("Precision")
    axes[0, 0].set_title(
        f"Precision-Recall (test AP = {test_metrics['average_precision']:.3f})"
    )

    axes[0, 1].plot(fpr, tpr, color="#0F6E84", lw=2)
    axes[0, 1].plot([0, 1], [0, 1], color="#94A3B1", ls="--", lw=1)
    axes[0, 1].set_xlabel("False positive rate")
    axes[0, 1].set_ylabel("True positive rate")
    axes[0, 1].set_title(f"ROC (test AUC = {test_metrics['roc_auc']:.3f})")

    cm = [[tn, fp], [fn, tp]]
    colors = [["#E8F1F4", "#FBEAE3"], ["#FBEAE3", "#E8F1F4"]]
    for i in range(2):
        for j in range(2):
            axes[1, 0].text(
                j,
                i,
                f"{cm[i][j]:,}",
                ha="center",
                va="center",
                fontsize=14,
                color="#1F2937",
            )
    axes[1, 0].set_xticks([0, 1], labels=["Pred No", "Pred Yes"])
    axes[1, 0].set_yticks([0, 1], labels=["True No", "True Yes"])
    axes[1, 0].set_title(
        f"Confusion matrix (threshold 0.5) - accuracy {test_metrics['accuracy']:.3f}"
    )
    for i in range(2):
        for j in range(2):
            axes[1, 0].add_patch(
                Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=colors[i][j], zorder=0)
            )
    axes[1, 0].set_xlim(-0.5, 1.5)
    axes[1, 0].set_ylim(1.5, -0.5)
    axes[1, 0].grid(False)

    top = feature_importance["importances"][:12][::-1]
    names = [d["feature"] for d in top]
    means = [d["mean"] for d in top]
    axes[1, 1].barh(names, means, color="#0F6E84", height=0.6)
    axes[1, 1].set_xlabel("Mean AP drop when permuted")
    axes[1, 1].set_title("Permutation importance (top 12)")

    fig.suptitle(
        f"Final model: {best_name} - approved target: Churn (Yes) - single test evaluation",
        fontsize=13,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(IMAGES / "model_performance_charts.png", bbox_inches="tight")
    plt.close(fig)

    print(
        f"Selected: {best_name} | Test AP={test_metrics['average_precision']} "
        f"ROC-AUC={test_metrics['roc_auc']} Recall={test_metrics['recall']} "
        f"Precision={test_metrics['precision']}"
    )
    print(
        f"Confusion: TN={tn} FP={fp} FN={fn} TP={tp} | Brier={brier} "
        f"| Top-decile capture={top_decile_capture} (lift {lift}x)"
    )
    print("Wrote models/final_model.joblib, preprocessor.joblib, model_metadata.json")
    print("Wrote docs/json/model_performance.json, feature_importance.json")
    print("Wrote docs/images/model_performance_charts.png")


if __name__ == "__main__":
    main()

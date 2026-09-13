"""Phase 1 - Create the data dictionary for the Telco Customer Churn dataset.

Profiles every column of the raw dataset and writes:
- docs/data_dictionary.md
- docs/json/data_dictionary.json

Per column the dictionary records: description, business meaning, inferred type,
possible values / ranges, missing and unique counts, example values, whether it
can be used as a feature, whether it could be a candidate target in Phase 3,
and potential data-leakage risk.

This phase does not select or propose a target variable.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
DOCS_DIR = ROOT / "docs"
JSON_DIR = DOCS_DIR / "json"

DATA_SOURCE_REF = (
    "IBM Telco Customer Churn sample dataset (public sample data distributed by "
    "IBM for Cognos Analytics / commonly mirrored on Kaggle as "
    "'telco-customer-churn')."
)

# Human-curated column metadata, grounded in the profiling report values.
COLUMN_META = {
    "customerID": {
        "role": "Identifier",
        "description": (
            "Unique customer identifier with format 'NNNN-XXXX' (digits + 5 "
            "alphanumeric characters). One per customer."
        ),
        "feature": False,
        "feature_reason": (
            "100% unique per row: zero predictive value. Exclude from features; "
            "use only as a join key / traceability ID."
        ),
        "target": False,
        "leakage": "None. Randomly assigned identifier.",
    },
    "gender": {
        "role": "Dimension",
        "description": "Customer gender (Male / Female).",
        "feature": True,
        "feature_reason": "Standard demographic segmentation variable.",
        "target": False,
        "leakage": "None. Known at signup.",
    },
    "SeniorCitizen": {
        "role": "Status flag",
        "description": (
            "Binary flag marking customers aged 65+ (1 = senior, 0 = not). "
            "Numeric encoding of a boolean."
        ),
        "feature": True,
        "feature_reason": (
            "Age segment proxy; useful for demographic targeting of retention offers."
        ),
        "target": False,
        "leakage": "None.",
    },
    "Partner": {
        "role": "Status flag",
        "description": "Whether the customer has a spouse/partner (Yes/No).",
        "feature": True,
        "feature_reason": "Household-size proxy; multi-person households churn less in telecom.",
        "target": False,
        "leakage": "None.",
    },
    "Dependents": {
        "role": "Status flag",
        "description": "Whether the customer has dependents in the household (Yes/No).",
        "feature": True,
        "feature_reason": "Family bundle indicator; correlates with plan choice and stickiness.",
        "target": False,
        "leakage": "None.",
    },
    "tenure": {
        "role": "Metric",
        "description": (
            "Customer tenure with the company in completed months (0 = brand new, "
            "max 72). Integer."
        ),
        "feature": True,
        "feature_reason": (
            "Strong behavioural variable: contract age at the snapshot date."
        ),
        "target": True,
        "target_note": (
            "Conceivable as a retention-duration outcome (regression / survival "
            "analysis), but weaker direct business actionability; to be evaluated "
            "in Phase 3."
        ),
        "leakage": (
            "None for churn-style prediction: tenure at scoring time is known. "
            "Perfectly collinear with TotalCharges accumulation."
        ),
    },
    "PhoneService": {
        "role": "Status flag",
        "description": "Whether the customer subscribes to home phone service (Yes/No).",
        "feature": True,
        "feature_reason": "Product-mix variable.",
        "target": False,
        "leakage": "None.",
    },
    "MultipleLines": {
        "role": "Dimension",
        "description": (
            "Phone add-on: multiple lines (Yes / No / No phone service). The "
            "'No phone service' value encodes the structural dependency on PhoneService."
        ),
        "feature": True,
        "feature_reason": "Product-mix variable with explicit structural category.",
        "target": False,
        "leakage": "None.",
    },
    "InternetService": {
        "role": "Dimension",
        "description": "Internet technology: DSL, Fiber optic, or No internet service.",
        "feature": True,
        "feature_reason": (
            "Core product line; largest monthly-charge differentiator (median "
            "$91.68 fiber vs $56.15 DSL)."
        ),
        "target": False,
        "leakage": "None.",
    },
    "OnlineSecurity": {
        "role": "Dimension",
        "description": (
            "Internet add-on: online security (Yes / No / No internet service)."
        ),
        "feature": True,
        "feature_reason": "Value-added service; retention-relevant add-on.",
        "target": False,
        "leakage": "None.",
    },
    "OnlineBackup": {
        "role": "Dimension",
        "description": "Internet add-on: cloud backup (Yes / No / No internet service).",
        "feature": True,
        "feature_reason": "Value-added service; retention-relevant add-on.",
        "target": False,
        "leakage": "None.",
    },
    "DeviceProtection": {
        "role": "Dimension",
        "description": "Internet add-on: device protection plan (Yes / No / No internet service).",
        "feature": True,
        "feature_reason": "Value-added service; retention-relevant add-on.",
        "target": False,
        "leakage": "None.",
    },
    "TechSupport": {
        "role": "Dimension",
        "description": "Internet add-on: tech support plan (Yes / No / No internet service).",
        "feature": True,
        "feature_reason": "Service-quality proxy; retention-relevant add-on.",
        "target": False,
        "leakage": "None.",
    },
    "StreamingTV": {
        "role": "Dimension",
        "description": "Entertainment add-on: streaming TV (Yes / No / No internet service).",
        "feature": True,
        "feature_reason": "Engagement/entertainment bundle variable.",
        "target": False,
        "leakage": "None.",
    },
    "StreamingMovies": {
        "role": "Dimension",
        "description": "Entertainment add-on: streaming movies (Yes / No / No internet service).",
        "feature": True,
        "feature_reason": "Engagement/entertainment bundle variable.",
        "target": False,
        "leakage": "None.",
    },
    "Contract": {
        "role": "Dimension",
        "description": (
            "Contract type: Month-to-month, One year, or Two year. Defines the "
            "customer's commitment period and exit cost."
        ),
        "feature": True,
        "feature_reason": (
            "Strongest commitment/switching-cost variable in the dataset; 55% of "
            "the base is month-to-month."
        ),
        "target": False,
        "leakage": "None. Contract type is known at any scoring time.",
    },
    "PaperlessBilling": {
        "role": "Status flag",
        "description": "Whether the customer receives paperless billing (Yes/No).",
        "feature": True,
        "feature_reason": "Billing-behaviour variable; interacts with payment method.",
        "target": False,
        "leakage": "None.",
    },
    "PaymentMethod": {
        "role": "Dimension",
        "description": (
            "Payment method: Electronic check, Mailed check, Bank transfer "
            "(automatic), or Credit card (automatic)."
        ),
        "feature": True,
        "feature_reason": (
            "Distinguishes manual vs automatic payments - a known friction/retention lever."
        ),
        "target": False,
        "leakage": "None.",
    },
    "MonthlyCharges": {
        "role": "Metric",
        "description": (
            "Recurring monthly charge for the customer's current bundle, in USD. "
            "Range $18.25-$118.75."
        ),
        "feature": True,
        "feature_reason": "Core price variable; price-sensitivity analyses.",
        "target": True,
        "target_note": (
            "Could serve as a price/ARPU regression outcome, but weak business "
            "actionability as a target; to be evaluated in Phase 3."
        ),
        "leakage": "None. Known for any active customer at scoring time.",
    },
    "TotalCharges": {
        "role": "Metric",
        "description": (
            "Cumulative amount billed to the customer to date, in USD. Stored as "
            "text with 11 blank strings (all tenure = 0 customers). "
            "Range $18.80-$8,684.80, right-skewed."
        ),
        "feature": True,
        "feature_reason": (
            "Lifetime revenue proxy. Requires cleaning (numeric coercion + "
            "imputation of 11 blanks, e.g. tenure x MonthlyCharges)."
        ),
        "target": True,
        "target_note": (
            "Candidate for a customer-value / revenue regression, but weak "
            "actionability as a direct target; to be evaluated in Phase 3."
        ),
        "leakage": (
            "Temporal-proxy risk: TotalCharges accumulates over tenure and is "
            "approximately tenure x MonthlyCharges, so it partially encodes tenure. "
            "It is available at scoring time for existing customers, but a model "
            "relying on it would not generalise to brand-new customers. Check "
            "collinearity before use."
        ),
    },
    "Churn": {
        "role": "Status flag",
        "description": (
            "Outcome flag: whether the customer left the company within the "
            "observation window (Yes = churned, 26.54%; No = retained, 73.46%)."
        ),
        "feature": False,
        "feature_reason": (
            "It is the only outcome-like flag in the dataset. If it were used as "
            "a feature for any model, it would leak the very outcome being "
            "predicted. Must be excluded from feature matrices."
        ),
        "target": True,
        "target_note": (
            "Only outcome-like flag in the dataset; natural candidate-target for "
            "retention problems. Selection/ranking belongs to Phase 3 - no "
            "decision is made here."
        ),
        "leakage": (
            "It IS the outcome. Using it as a feature would be target leakage; "
            "predicting it is the legitimate use, pending Phase 3 approval."
        ),
    },
}


def infer_kind(name: str, series: pd.Series) -> tuple[str, str | None]:
    """Infer the column kind, mirroring standard data-profiling semantics."""
    uniques = series.dropna().unique()
    if name == "customerID":
        return "identifier", "alphanumeric code (likely unique key)"
    if pd.api.types.is_bool_dtype(series):
        return "boolean", None
    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() == 2:
            return "boolean", "0/1"
        return "numeric", None
    if series.nunique() == 2 and set(map(str, uniques)) <= {"Yes", "No"}:
        return "boolean", "yes/no"
    if len(uniques) <= 10:
        return "categorical", None
    return "string", None


def profile_column(df: pd.DataFrame, col: str) -> dict:
    s = df[col]
    kind, kind_note = infer_kind(col, s)
    missing = int(s.isna().sum())
    blanks = int(s.astype(str).str.strip().eq("").sum())
    out: dict = {
        "name": col,
        "role": COLUMN_META[col]["role"],
        "dtype_storage": str(s.dtype),
        "inferred_kind": kind,
        "kind_note": kind_note,
        "missing": missing,
        "missing_pct": round(missing / len(df) * 100, 2),
        "implicit_blanks": blanks,
        "unique": int(s.nunique()),
        "unique_pct": round(s.nunique() / len(df) * 100, 2),
        "examples": [str(x) for x in s.dropna().unique()[:3]],
    }
    if kind in {"numeric"} or col == "TotalCharges":
        num = pd.to_numeric(s, errors="coerce")
        q1, q3 = num.quantile([0.25, 0.75])
        out["stats"] = {
            "min": float(num.min()),
            "max": float(num.max()),
            "mean": round(float(num.mean()), 2),
            "median": float(num.median()),
            "std": round(float(num.std()), 2),
            "q1": float(q1),
            "q3": float(q3),
            "iqr_outliers": int(
                ((num < q1 - 1.5 * (q3 - q1)) | (num > q3 + 1.5 * (q3 - q1))).sum()
            ),
        }
    elif kind in {"categorical", "boolean"} or s.nunique() <= 6:
        vc = s.value_counts()
        out["values"] = [
            {"value": str(k), "count": int(v), "pct": round(v / len(df) * 100, 2)}
            for k, v in vc.items()
        ]
    meta = COLUMN_META[col]
    out["description"] = meta["description"]
    out["feature_candidate"] = meta["feature"]
    out["feature_reason"] = meta["feature_reason"]
    out["target_candidate_phase3"] = bool(meta.get("target", False))
    if meta.get("target_note"):
        out["target_note"] = meta["target_note"]
    out["leakage_risk"] = meta["leakage"]
    return out


def main() -> None:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RAW_PATH)
    n_rows, n_cols = df.shape

    columns = [profile_column(df, c) for c in df.columns]
    dup_rows = int(df.duplicated().sum())

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(RAW_PATH.relative_to(ROOT)),
        "data_source_reference": DATA_SOURCE_REF,
        "rows": n_rows,
        "columns": n_cols,
        "grain": "one row = one customer snapshot (demographics, services, contract, billing, churn outcome flag)",
        "duplicate_rows": dup_rows,
        "primary_key": "customerID",
        "columns": columns,
    }
    (JSON_DIR / "data_dictionary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )

    # --- Markdown ------------------------------------------------------------
    md: list[str] = []
    md.append("# Data Dictionary - Telco Customer Churn\n")
    md.append(
        f"> Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"Source: `data/raw/Telco-Customer-Churn.csv` · Rows: {n_rows:,} · Columns: {n_cols}\n"
    )
    md.append("## Overview\n")
    md.append("| Property | Value |")
    md.append("| -------- | ----- |")
    md.append(
        f"| Source file | `{RAW_PATH.relative_to(ROOT)}` (CSV, comma-separated, UTF-8) |"
    )
    md.append(f"| Rows / Columns | {n_rows:,} / {n_cols} |")
    md.append(
        "| Grain | One row = one customer snapshot (demographics, services, contract, billing, churn outcome flag) |"
    )
    md.append(f"| Duplicate rows | {dup_rows} |")
    md.append("| Primary key | `customerID` (100% unique, 0% null) |")
    md.append(f"| Data source reference | {DATA_SOURCE_REF} |")
    md.append(
        "| Inferred purpose | Telecom customer-base snapshot designed for retention analysis: each record bundles who the customer is, what they subscribed to, what they pay, and whether they churned |"
    )
    md.append("")
    md.append("## Column Summary\n")
    md.append("| # | Column | Role | Type | Unique | Missing % | Description |")
    md.append("| - | ------ | ---- | ---- | ------ | --------- | ----------- |")
    for i, c in enumerate(columns, start=1):
        t = c["inferred_kind"] + (f" ({c['kind_note']})" if c["kind_note"] else "")
        md.append(
            f"| {i} | `{c['name']}` | {c['role']} | {t} | {c['unique']:,} | "
            f"{c['missing_pct']:.2f}% | {c['description']} |"
        )
    md.append("")
    md.append(
        "Roles: Identifier · Metric · Dimension · Status flag · Target · Timestamp · Free text.\n"
    )

    md.append("## Column Details\n")
    for c in columns:
        md.append(f"### `{c['name']}`\n")
        kind_txt = c["inferred_kind"] + (
            f" ({c['kind_note']})" if c["kind_note"] else ""
        )
        md.append(
            f"- **Role:** {c['role']} · **Type:** {kind_txt} · "
            f"**Storage dtype:** `{c['dtype_storage']}` · "
            f"**Missing:** {c['missing']} ({c['missing_pct']:.2f}%)"
        )
        md.append(f"- **Unique values:** {c['unique']:,} ({c['unique_pct']:.2f}%)")
        md.append(f"- **Description:** {c['description']}")
        if "stats" in c:
            st = c["stats"]
            md.append(
                f"- **Range:** {st['min']:g} … {st['max']:g} · mean {st['mean']:g} · "
                f"median {st['median']:g} · std {st['std']:g} · IQR outliers: {st['iqr_outliers']}"
            )
        if "values" in c:
            md.append("- **Allowed values:**\n")
            md.append("  | Value | Count | % |")
            md.append("  | ----- | -----: | -: |")
            for v in c["values"]:
                md.append(f"  | `{v['value']}` | {v['count']:,} | {v['pct']}% |")
            md.append("")
        md.append(f"- **Examples:** {', '.join(f'`{e}`' for e in c['examples'][:3])}")
        md.append(
            f"- **Feature candidate:** {'Yes' if c['feature_candidate'] else 'No'} - {c['feature_reason']}"
        )
        tgt = "Yes" if c["target_candidate_phase3"] else "No"
        note = f" {c['target_note']}" if c.get("target_note") else ""
        md.append(f"- **Candidate target (Phase 3):** {tgt}.{note}")
        md.append(f"- **Leakage risk:** {c['leakage_risk']}")
        md.append("")

    md.append("## Key & Relationships\n")
    md.append("| Column | Evidence | Assessment |")
    md.append("| ------ | -------- | ---------- |")
    md.append(
        "| `customerID` | 7,043 unique values = row count, 0 null | Primary key |"
    )
    md.append(
        "| `MultipleLines` | `No phone service` count (682) equals `PhoneService = No` count | Dependent on `PhoneService` |"
    )
    md.append(
        "| `OnlineSecurity` … `StreamingMovies` | `No internet service` count (1,526) equals `InternetService = No` count | Dependent on `InternetService` |"
    )
    md.append(
        "| `TotalCharges` | 11 blanks align exactly with `tenure = 0` rows | Dependent on `tenure` accumulation |"
    )
    md.append("")
    md.append("Single-table dataset: no foreign keys to external tables.\n")

    md.append("## Data Quality Notes\n")
    md.append("| # | Column | Issue | Evidence | Recommendation |")
    md.append("| - | ------ | ----- | -------- | -------------- |")
    md.append(
        '| 1 | `TotalCharges` | Implicit nulls / wrong storage type | 11 blank strings `" "` stored in an otherwise numeric column (0.16%); all belong to `tenure = 0` customers | Coerce to numeric; impute as `tenure × MonthlyCharges` (first invoice) or drop the 11 rows |'
    )
    md.append(
        "| 2 | `SeniorCitizen` | Numeric encoding of a boolean | Stored as 0/1 int | Treat as categorical boolean in analysis and UI |"
    )
    md.append(
        "| 3 | `Churn` | Moderate class imbalance | Yes = 26.54% vs No = 73.46% (ratio 2.77 : 1) | If modeled, use stratified splits and imbalance-aware metrics (no target decision in this phase) |"
    )
    md.append(
        "| 4 | `TotalCharges` | Right skew (accumulation) | Max $8,684.80 vs median $1,397.48 | Not an error: reflects long-tenure customers; consider log transform or capping in modeling |"
    )
    md.append(
        "| 5 | Add-on columns | Redundant structural level | `No internet service` / `No phone service` duplicate information already in `InternetService` / `PhoneService` | Keep as-is (informative) or normalise to Yes/No + separate flag |"
    )
    md.append("")
    md.append("## Glossary\n")
    md.append("| Term | Definition |")
    md.append("| ---- | ---------- |")
    md.append(
        "| Churn | Customer leaving the company within the observation window (`Churn = Yes`) |"
    )
    md.append("| Tenure | Completed months of customer relationship (0 = brand new) |")
    md.append(
        "| Month-to-month | Contract with no commitment period; customer can leave any month |"
    )
    md.append(
        "| DSL / Fiber optic | Internet technologies offered; fiber is the premium tier (median monthly charge $91.68 vs $56.15) |"
    )
    md.append(
        "| Electronic check | Manual, non-recurring payment method; contrast with automatic bank transfer / credit card |"
    )
    md.append(
        "| ARPU | Average revenue per user, approximated here by `MonthlyCharges` |"
    )
    md.append("")

    (DOCS_DIR / "data_dictionary.md").write_text("\n".join(md))
    print("Wrote docs/data_dictionary.md")
    print("Wrote docs/json/data_dictionary.json")
    target_candidates = [c["name"] for c in columns if c["target_candidate_phase3"]]
    print(
        f"Columns={len(columns)} | target_candidate flags (unranked)={target_candidates}"
    )


if __name__ == "__main__":
    main()

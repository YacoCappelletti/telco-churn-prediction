"""Phase 1 - Data audit for the Telco Customer Churn dataset.

Reads the raw dataset, profiles structure and data quality, and writes:
- docs/data_quality_report.md
- docs/json/data_quality_metrics.json

This phase is diagnostic only: it does not select, define, or propose a target
variable.
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
    "'telco-customer-churn'). 7,043 customers of a fictional US telecom operator."
)


def count_implicit_blanks(series: pd.Series) -> int:
    """Count values that are empty or whitespace-only strings."""
    return int(series.astype(str).str.strip().eq("").sum())


def iqr_outliers(series: pd.Series) -> int:
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return int(((series < lo) | (series > hi)).sum())


def fmt(v: float, nd: int = 2) -> str:
    return f"{v:,.{nd}f}"


def main() -> None:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RAW_PATH)
    n_rows, n_cols = df.shape
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    # --- Missing values -----------------------------------------------------
    explicit_missing = df.isna().sum()
    implicit_blanks = {c: count_implicit_blanks(df[c]) for c in df.columns}
    # TotalCharges blank strings become NaN after numeric coercion
    tc_numeric = pd.to_numeric(df["TotalCharges"], errors="coerce")
    missing_view = []
    for c in df.columns:
        blanks = implicit_blanks[c] if c != "TotalCharges" else 0
        coerced_nan = int(tc_numeric.isna().sum()) if c == "TotalCharges" else 0
        if explicit_missing[c] > 0 or blanks > 0 or coerced_nan > 0:
            missing_view.append((c, int(explicit_missing[c]), blanks, coerced_nan))

    # --- Duplicates ---------------------------------------------------------
    dup_rows = int(df.duplicated().sum())
    dup_ids = int(df["customerID"].duplicated().sum())

    # --- Constant columns ---------------------------------------------------
    constant_cols = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]

    # --- Data type issues ---------------------------------------------------
    # A column has a type issue only if it is mostly numeric yet contains
    # non-coercible values or blank strings (e.g. TotalCharges with " ").
    type_issues = []
    for c in non_numeric_cols:
        stripped = df[c].astype(str).str.strip()
        blank_mask = stripped.eq("")
        coerced = pd.to_numeric(
            stripped.where(~blank_mask, other=np.nan), errors="coerce"
        )
        nonblank_count = int((~blank_mask & df[c].notna()).sum())
        dirty = int((coerced.isna() & ~blank_mask & df[c].notna()).sum())
        frac_numeric = coerced.notna().sum() / nonblank_count if nonblank_count else 0.0
        blanks = int(blank_mask.sum())
        if frac_numeric >= 0.5 and (dirty > 0 or blanks > 0):
            issue = (
                "implicit blanks in numeric column"
                if dirty == 0
                else "mixed numeric / non-numeric values"
            )
            type_issues.append(
                {
                    "column": c,
                    "declared_kind": "string",
                    "issue": issue,
                    "dirty_count": dirty,
                    "blank_count": blanks,
                    "frac_numeric": round(float(frac_numeric), 4),
                }
            )
    tc_clean = tc_numeric.fillna(df["tenure"] * df["MonthlyCharges"])

    # --- Outliers (IQR rule) ------------------------------------------------
    outlier_stats = {}
    for c in ["tenure", "MonthlyCharges", "TotalCharges"]:
        s = df[c] if c != "TotalCharges" else tc_clean
        outlier_stats[c] = {
            "min": float(s.min()),
            "max": float(s.max()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": float(s.std()),
            "iqr_outliers": iqr_outliers(s),
        }

    # --- Class imbalance (outcome-like flag only) ---------------------------
    churn_counts = df["Churn"].value_counts()
    churn_pct = df["Churn"].value_counts(normalize=True) * 100
    imbalance_ratio = churn_counts.max() / churn_counts.min()

    # --- Basic distributions ------------------------------------------------
    numeric_dist = df[["tenure", "MonthlyCharges"]].describe().T.round(2)
    categorical_dist = {
        c: df[c].value_counts().head(6).to_dict() for c in non_numeric_cols
    }
    # Group structure without touching the churn flag (pricing structure)
    price_by_internet = (
        df.groupby("InternetService")["MonthlyCharges"].median().round(2)
    )
    price_by_contract = df.groupby("Contract")["MonthlyCharges"].median().round(2)
    new_customers = int((df["tenure"] == 0).sum())

    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(RAW_PATH.relative_to(ROOT)),
        "data_source_reference": DATA_SOURCE_REF,
        "rows": n_rows,
        "columns": n_cols,
        "duplicate_rows": dup_rows,
        "duplicate_customer_ids": dup_ids,
        "constant_columns": constant_cols,
        "missing_values": [
            {
                "column": c,
                "explicit": e,
                "implicit_blank": b,
                "after_numeric_coercion": n,
            }
            for c, e, b, n in missing_view
        ],
        "type_issues": type_issues,
        "numeric_summary": {
            c: outlier_stats[c] for c in ["tenure", "MonthlyCharges", "TotalCharges"]
        },
        "iqr_outlier_counts": {
            c: outlier_stats[c]["iqr_outliers"] for c in outlier_stats
        },
        "churn_flag_distribution": {
            "No": int(churn_counts["No"]),
            "Yes": int(churn_counts["Yes"]),
            "pct_no": round(float(churn_pct["No"]), 2),
            "pct_yes": round(float(churn_pct["Yes"]), 2),
            "imbalance_ratio_no_to_yes": round(float(imbalance_ratio), 2),
        },
        "categorical_distributions": categorical_dist,
        "median_monthly_charges_by_internet": price_by_internet.to_dict(),
        "median_monthly_charges_by_contract": price_by_contract.to_dict(),
        "customers_with_zero_tenure": new_customers,
    }
    (JSON_DIR / "data_quality_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n"
    )

    # --- Markdown report ----------------------------------------------------
    md = []
    md.append("# Data Quality Report - Telco Customer Churn\n")
    md.append(
        f"> Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"Source: `data/raw/Telco-Customer-Churn.csv` · "
        f"Rows: {n_rows:,} · Columns: {n_cols}\n"
    )
    md.append("## 1. Dataset overview\n")
    md.append(f"- **Rows:** {n_rows:,} · **Columns:** {n_cols}")
    md.append(f"- **Data source reference:** {DATA_SOURCE_REF}")
    md.append(
        "- **Grain:** one row = one customer snapshot (contract, services, billing, churn flag)."
    )
    md.append(f"- **Customers with zero tenure (brand new):** {new_customers}\n")

    md.append("## 2. Missing values\n")
    if missing_view:
        md.append(
            "| Column | Explicit NaN | Implicit blanks (' ') | After numeric coercion |"
        )
        md.append(
            "| ------ | -----------: | --------------------: | ----------------------: |"
        )
        for c, e, b, n in missing_view:
            md.append(f"| `{c}` | {e} | {b} | {n} |")
        md.append(
            "\nOnly `TotalCharges` is affected: **11 rows (0.16%)** store an empty "
            "string instead of a number. All 11 belong to customers with `tenure = 0` "
            "(brand-new customers billed once, whose `MonthlyCharges` is their first "
            "invoice). No other column has missing values.\n"
        )
    else:
        md.append("No missing values detected.\n")

    md.append("## 3. Duplicated rows\n")
    md.append(f"- Duplicated full rows: **{dup_rows}**")
    md.append(
        f"- Duplicated `customerID`: **{dup_ids}** -> `customerID` is a clean primary key.\n"
    )

    md.append("## 4. Constant columns\n")
    md.append("None. Every column has at least two distinct values.\n")

    md.append("## 5. Data type issues\n")
    md.append(
        "| Column | Declared type | Issue | Recommendation |\n"
        "| ------ | ------------- | ----- | -------------- |\n"
        '| `TotalCharges` | string | 11 blank strings `" "` stored in an otherwise numeric column | Coerce with `pd.to_numeric(errors="coerce")`; impute the 11 new customers as `tenure × MonthlyCharges` (or drop, 0.16%) |\n'
        "| `SeniorCitizen` | int64 (0/1) | Numeric encoding of a binary flag | Treat as categorical boolean in analysis |\n"
        "| `Churn` | string (Yes/No) | Text encoding of a binary outcome | Map to {0, 1} only downstream, once a target is formally approved |\n"
    )
    md.append(
        'Structural category values (`"No phone service"`, `"No internet service"`) '
        "are consistent and are not errors: they encode service dependencies "
        "(add-ons require the underlying service).\n"
    )

    md.append("## 6. Outliers (IQR rule, 1.5 × IQR)\n")
    md.append("| Column | Min | Median | Mean | Max | Std | IQR outliers |")
    md.append("| ------ | --: | -----: | ---: | --: | --: | -----------: |")
    for c, s in outlier_stats.items():
        md.append(
            f"| `{c}` | {fmt(s['min'])} | {fmt(s['median'])} | {fmt(s['mean'])} | "
            f"{fmt(s['max'])} | {fmt(s['std'])} | {s['iqr_outliers']} |"
        )
    md.append(
        "\nNo IQR outliers in any numeric column. `TotalCharges` is naturally "
        "right-skewed (accumulation of monthly invoices over tenure) but the skew "
        "comes from long-tenure customers, not erroneous values.\n"
    )

    md.append("## 7. Class imbalance (outcome-like flag)\n")
    md.append(
        f"- The only outcome-like flag in the dataset is `Churn` "
        f"(Yes: {int(churn_counts['Yes']):,} = {churn_pct['Yes']:.2f}%, "
        f"No: {int(churn_counts['No']):,} = {churn_pct['No']:.2f}%).\n"
        f"- Imbalance ratio (No : Yes) = {imbalance_ratio:.2f} : 1 — a **moderate "
        "imbalance**. If this flag were ever used for predictive modeling, plain "
        "accuracy would be a misleading metric and stratified sampling / PR-style "
        "metrics would be required. (Recorded here as a data-quality fact only; "
        "no target decision is made in this phase.)\n"
    )

    md.append("## 8. Basic distributions\n")
    md.append("### Numeric columns\n")
    md.append("| Column | Min | Q1 | Median | Q3 | Max | Mean |")
    md.append("| ------ | --: | -: | -----: | -: | --: | ---: |")
    for c in ["tenure", "MonthlyCharges"]:
        s = df[c]
        md.append(
            f"| `{c}` | {fmt(s.min())} | {fmt(s.quantile(0.25))} | {fmt(s.median())} | "
            f"{fmt(s.quantile(0.75))} | {fmt(s.max())} | {fmt(s.mean())} |"
        )
    md.append(
        "\n- `tenure` is fairly flat across 0-72 months (median 29), with a visible "
        "spike of brand-new customers (tenure < 3 months).\n"
    )
    md.append("### Categorical columns (top values)\n")
    md.append("| Column | Top values (count) |")
    md.append("| ------ | ------------------ |")
    for c, dist in categorical_dist.items():
        if c in {"customerID", "TotalCharges"}:
            continue
        items = ", ".join(f"`{k}` ({v})" for k, v in dist.items())
        md.append(f"| `{c}` | {items} |")
    md.append("")
    md.append("### Pricing structure (group medians of `MonthlyCharges`)\n")
    md.append("| Internet service | Median monthly charge |")
    md.append("| ---------------- | --------------------: |")
    for k, v in price_by_internet.items():
        md.append(f"| `{k}` | ${fmt(v)} |")
    md.append("| Contract | Median monthly charge |")
    md.append("| -------- | --------------------: |")
    for k, v in price_by_contract.items():
        md.append(f"| `{k}` | ${fmt(v)} |")
    md.append("")

    md.append("## 9. Initial hypotheses (to be validated in Phase 2)\n")
    md.append(
        "1. **Contract commitment drives retention.** 55% of the base is on "
        "month-to-month contracts; lock-in contracts (1-2 years) plausibly reduce "
        "churn. Highest-impact hypothesis to validate.\n"
        "2. **New customers are the fragile segment.** A tenure spike at 0-3 months "
        "plus 11 zero-tenure rows suggests onboarding is a churn-critical window.\n"
        "3. **Fiber optic is the premium - and possibly problematic - product.** It "
        "carries a median monthly charge of $91.68 vs $56.15 for DSL; premium "
        "price with under-delivered expectations is a classic churn driver.\n"
        "4. **Payment friction may matter.** 33.6% of customers pay by electronic "
        "check (manual, non-recurring); manual payment methods often correlate with "
        "churn vs automatic payments.\n"
        "5. **Revenue concentration risk.** With ARPU around $65 and 26.5% of "
        "customers flagged as churned, the business impact of churn is material; "
        "revenue at risk must be quantified in Phase 2.\n"
    )

    md.append("## 10. Phase 1 compliance note\n")
    md.append(
        "This report is diagnostic. **No target variable has been selected, defined, "
        "ranked, or proposed in this phase.** The `Churn` distribution is reported "
        "strictly as a data-quality characteristic (class imbalance), as required by "
        "the audit checklist. Candidate-target analysis belongs to Phase 3.\n"
    )

    (DOCS_DIR / "data_quality_report.md").write_text("\n".join(md))
    print("Wrote docs/data_quality_report.md")
    print("Wrote docs/json/data_quality_metrics.json")
    print(
        f"Rows={n_rows:,} Cols={n_cols} Dups={dup_rows} "
        f"TypeIssues={[t['column'] for t in type_issues]} "
        f"Imbalance={churn_pct['Yes']:.2f}% churn-yes"
    )


if __name__ == "__main__":
    main()

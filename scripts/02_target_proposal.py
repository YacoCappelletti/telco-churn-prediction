"""Phase 3 - Target variable proposal for the Telco Customer Churn dataset.

Reads the Phase 1/2 evidence (problem statement, business analysis, data
dictionary, data quality report, insights), evaluates candidate target
variables against 14 criteria, and writes:
- docs/json/target_proposal.json
- docs/json/target_approval.json  (approval_status = "pending")
- docs/target_proposal.md

No model is trained in this phase. Execution stops until the user approves
the target variable (docs/json/target_approval.json -> "approved").
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
DOCS_DIR = ROOT / "docs"
JSON_DIR = DOCS_DIR / "json"


def main() -> None:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RAW_PATH)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # --- Computed evidence for candidate variables ---------------------------
    n = len(df)
    churn_yes = int((df["Churn"] == "Yes").sum())
    churn_pct = churn_yes / n

    tenure_missing = int(df["tenure"].isna().sum())
    monthly_missing = int(df["MonthlyCharges"].isna().sum())
    total_missing = int(df["TotalCharges"].isna().sum())

    correlation_total_monthly = round(
        float(df["TotalCharges"].corr(df["tenure"] * df["MonthlyCharges"])), 4
    )

    computed = {
        "n_rows": n,
        "churn_yes_count": churn_yes,
        "churn_yes_rate": round(churn_pct, 4),
        "churn_imbalance_ratio": round((n - churn_yes) / churn_yes, 2),
        "missing_values_by_candidate": {
            "tenure": tenure_missing,
            "MonthlyCharges": monthly_missing,
            "TotalCharges": total_missing,
            "Churn": int(df["Churn"].isna().sum()),
        },
        "totalcharges_tenure_monthly_correlation": correlation_total_monthly,
        "zero_tenure_rows": int((df["tenure"] == 0).sum()),
    }

    # --- Candidate evaluation (14 criteria) ----------------------------------
    criteria = [
        "alignment_with_business_problem",
        "business_relevance",
        "actionability",
        "availability_at_prediction_time",
        "data_quality",
        "missing_values",
        "data_type_consistency",
        "definition_reliability",
        "outliers_inconsistent_values",
        "class_balance",
        "data_leakage",
        "temporal_consistency",
        "ethical_legal_restrictions",
        "ml_feasibility",
    ]

    candidates = [
        {
            "name": "Churn",
            "type": "binary flag (Yes/No)",
            "alignment": "Directly matches the primary problem (P1): customer attrition and recurring-revenue protection.",
            "relevance": "Highest: 26.5% of the base churns and takes 30.5% of MRR ($139K/mo) with it.",
            "actionability": "High: probability scores map directly to retention offers, call prioritization and budget weighting by revenue at risk.",
            "availability": "All candidate features (contract, services, payment, charges, tenure) are customer attributes known while the account is active.",
            "data_quality": "No missing values, consistent Yes/No domain, no outliers (flag).",
            "class_balance": f"Moderate imbalance: {churn_pct:.1%} positive - manageable with stratified splits and imbalance-aware metrics (PR-AUC).",
            "leakage": "It is the outcome itself; as long as it is used as the target (never as a feature), leakage is by construction absent. No post-outcome fields exist in the dataset.",
            "temporal_consistency": "Single-snapshot flag; definition ('customer left within observation window') is uniform across rows.",
            "ethics": "No sensitive attributes involved in the outcome; gender exists but is not needed for the target definition.",
            "feasibility": "Binary classification is standard, well supported, and deliverable as an API (probability) + app + dashboard.",
        },
        {
            "name": "tenure",
            "type": "integer months (0-72)",
            "alignment": "Indirect: retention duration, but not the primary revenue-leak problem.",
            "relevance": "Medium: duration matters, but the business question is who leaves and what revenue leaves with them.",
            "actionability": "Medium: a predicted tenure band is less directly usable for retention offers than a churn probability.",
            "availability": "Known at prediction time.",
            "data_quality": "Complete, integer, well-formed (11 zero-tenure new customers).",
            "class_balance": "Not applicable (regression); distribution is flat with a month-1 spike.",
            "leakage": "None.",
            "temporal_consistency": "Uniform definition.",
            "ethics": "None.",
            "feasibility": "Feasible regression / survival task, but weaker business fit than churn classification.",
        },
        {
            "name": "MonthlyCharges",
            "type": "float USD (18.25-118.75)",
            "alignment": "Weak: price is a lever, not an outcome the business needs to predict.",
            "relevance": "Low: predicting what a customer would pay is a pricing problem, not the identified churn problem.",
            "actionability": "Low: prediction does not change decisions.",
            "availability": "Known at prediction time.",
            "data_quality": "Clean, no missing.",
            "class_balance": "Not applicable.",
            "leakage": "None.",
            "temporal_consistency": "Uniform.",
            "ethics": "None.",
            "feasibility": "Feasible regression but low business value as a target.",
        },
        {
            "name": "TotalCharges",
            "type": "float USD (accumulated billing)",
            "alignment": "Weak: accumulated value is a consequence of tenure, not an actionable outcome.",
            "relevance": "Low-medium: interesting for value estimation, not for the churn problem.",
            "actionability": "Low.",
            "availability": "Only meaningful for existing customers; ~0 for brand-new customers.",
            "data_quality": "11 implicit blanks (0.16%), right-skewed, requires cleaning.",
            "class_balance": "Not applicable.",
            "leakage": "Strong proxy risk: correlates with tenure x MonthlyCharges; encodes past history rather than future behavior.",
            "temporal_consistency": "Cumulative measure - depends on when the snapshot is taken.",
            "ethics": "None.",
            "feasibility": "Feasible regression but weak alignment and leakage concerns.",
        },
    ]

    proposal = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommended_target": "Churn",
        "alternative_targets": ["tenure", "MonthlyCharges", "TotalCharges"],
        "problem_type": "classification",
        "positive_class": "Yes",
        "evaluation_criteria": criteria,
        "candidate_evaluation": candidates,
        "business_justification": (
            "The problem statement identifies customer churn as the primary problem "
            "(P1), and the business analysis quantified its impact: 26.5% of customers "
            "churn, taking 30.5% of monthly recurring revenue ($139K/mo, ~$1.67M "
            "annualized) with them. A churn probability directly powers the four "
            "recommended levers (contract migration, onboarding prioritization, fiber "
            "protection bundling, payment migration) by ranking accounts by expected "
            "risk x revenue at risk."
        ),
        "technical_justification": (
            "Binary classification with all-tabular features; moderate class imbalance "
            "(~26.5% positive) is manageable with stratified splits and PR-AUC-style "
            "metrics; probability outputs support threshold tuning to business trade-offs "
            "(retention capacity vs catch rate). Feature availability at scoring time is "
            "guaranteed because every feature is a current-customer attribute."
        ),
        "data_quality_justification": (
            "Churn has zero missing values and a consistent Yes/No domain. The only "
            "quality issue in the dataset (11 blank TotalCharges strings) affects a "
            "feature, not the target, and has a documented cleaning rule "
            "(impute tenure x MonthlyCharges). No outliers or inconsistent values exist "
            "in the flag."
        ),
        "data_dictionary_evidence": (
            "data_dictionary.md marks Churn as the only outcome-like Status flag "
            "(Yes: 1,869 / No: 5,174), flags it feature_candidate=False (leakage if used "
            "as a feature) and lists it as a Phase 3 target candidate."
        ),
        "data_quality_evidence": (
            "data_quality_report.md records the 26.54% / 73.46% split with imbalance "
            "ratio 2.77:1 (moderate), and confirms no missing values in Churn, no "
            "duplicated rows and no constant columns."
        ),
        "business_analysis_evidence": (
            "business_analysis_report.md quantifies the churn exposure: $139,131/mo "
            "revenue churned (30.5% of MRR), month-to-month contracts at 42.7% churn, "
            "first-year customers generating 55.5% of churn, fiber at 41.9% and "
            "e-check x paperless at 49.8% - all evidencing churn as the primary "
            "business problem and the segments a churn model must score."
        ),
        "assumptions": [
            "The Churn flag is defined uniformly for all customers (left within the observation window).",
            "The snapshot is representative of the current customer population.",
            "Retention actions will use predicted probabilities for ranking, with thresholds tuned to campaign capacity.",
        ],
        "risks": [
            "Moderate class imbalance: naive accuracy would overstate performance; use stratified splits and PR-AUC/recall-focused evaluation.",
            "Cross-sectional snapshot: no temporal validation set; performance on future cohorts is unverified.",
            "TotalCharges partially encodes tenure (correlation with tenure x MonthlyCharges) - collinearity must be handled in preprocessing.",
            "Possible proxy discrimination through demographic features (age proxy, gender); monitor fairness if used for customer-facing decisions.",
        ],
        "limitations": [
            "No timestamps: temporal validation (train-past, test-future) is impossible; single holdout only.",
            "No post-outcome fields exist, so classic target leakage is structurally absent, but future deployments must preserve this guarantee.",
            "The dataset is a curated sample; real-world drift may differ.",
        ],
        "data_leakage_checks": [
            "Churn is the outcome itself: excluded from any feature matrix (by construction).",
            "No post-outcome columns exist in the dataset (verified column-by-column in the data dictionary).",
            "TotalCharges accumulates over tenure - retained as a feature only with documented collinearity treatment, since it is available for existing customers at scoring time.",
            "customerID is excluded from features (unique identifier, zero predictive value).",
        ],
        "open_questions": [
            "Should demographic attributes (gender, SeniorCitizen) be allowed as model features, or excluded for fairness policy reasons?",
            "Is there a business-defined retention capacity (number of customers that can be contacted per month) to calibrate the probability threshold?",
            "Should the model prioritize recall (catch more churners) or precision (cheaper campaigns) - i.e., what is the cost of a retention offer vs a lost customer?",
        ],
        "approval_status": "pending_user_approval",
    }
    (JSON_DIR / "target_proposal.json").write_text(
        json.dumps(proposal, indent=2, ensure_ascii=False) + "\n"
    )

    approval = {
        "approved_target": None,
        "approved_problem_type": None,
        "approval_status": "pending",
        "user_comments": "",
        "approval_timestamp": None,
    }
    (JSON_DIR / "target_approval.json").write_text(
        json.dumps(approval, indent=2, ensure_ascii=False) + "\n"
    )

    # --- Markdown ------------------------------------------------------------
    cand_rows = "\n".join(
        f"| `{c['name']}` | {c['type']} | {c['alignment'].split(':')[0]} | "
        f"{'Clean' if c['name'] == 'Churn' else c['data_quality'].split(',')[0]} |"
        for c in candidates
    )
    md = f"""# Target Variable Proposal - Telco Customer Churn

> Phase 3 deliverable · Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · Status: **PENDING USER APPROVAL**
> Inputs: `problem_statement.md`, `business_analysis_report.md`, `data_dictionary.md`, `data_quality_report.md`, `json/insights.json`

## 1. Recommended target variable

**`Churn`** (Yes/No customer-attrition flag) - **problem type: binary classification** (positive class: `Yes`).

## 2. Candidate variables evaluated

| Candidate | Type | Business alignment | Verdict |
| --------- | ---- | ------------------ | ------- |
| `Churn` | binary flag | Directly matches the primary problem (P1, churn/retention) | **Recommended** |
| `tenure` | integer months | Indirect (duration view) | Alternative - weaker actionability |
| `MonthlyCharges` | float USD | Weak (price, not outcome) | Alternative - low value as target |
| `TotalCharges` | float USD | Weak (accumulated consequence) | Alternative - leakage/proxy risk |

All four were evaluated against 14 criteria: business alignment, relevance,
actionability, availability at prediction time, data quality, missing values,
type consistency, definition reliability, outliers, class balance, data
leakage, temporal consistency, ethical/legal restrictions, and ML feasibility
(full detail: `docs/json/target_proposal.json`).

## 3. Justification

### Business

The primary problem (Phase 1) is customer churn; the business analysis
(Phase 2) quantified it: 26.5% churn rate, $139,131/month churned revenue
(30.5% of MRR, ~$1.67M annualized), concentrated in month-to-month contracts
(42.7% churn), first-year customers (55.5% of churn), unprotected fiber users
and electronic-check payers. A churn probability is the single most useful
score for all four recommended levers: it ranks accounts for contract
migration, onboarding care, bundling offers, and payment migration, and it
supports revenue-weighted prioritization.

### Technical

Binary classification on all-tabular data is the best-supported setup:
stratified train/validation/test splits, imbalance-aware metrics
(PR-AUC, recall at fixed precision), calibrated probabilities for threshold
tuning to the retention campaign's capacity. Candidate models (Logistic
Regression, Decision Tree, Random Forest) are all appropriate for this size
(7,043 rows, 20 usable features).

### Data quality

`Churn` has zero missing values, a consistent two-level domain, and no
outliers. The dataset's single quality issue (11 blank `TotalCharges`)
affects a feature, not the target, and has a documented fix. Class imbalance
(2.77:1) is moderate and manageable.

## 4. Evidence trail

- **Data dictionary** (`data_dictionary.md`): Churn is the only outcome-like
  flag; flagged `feature_candidate = No` (leakage if used as a feature) and as
  a Phase 3 target candidate.
- **Data quality report** (`data_quality_report.md`): 26.54%/73.46% split,
  imbalance ratio 2.77:1, no missing values in Churn, clean primary key.
- **Business analysis** (`business_analysis_report.md`): revenue at risk,
  segment concentrations and the four recommended levers listed above.
- **Computed evidence** (this script): {computed["n_rows"]:,} rows;
  {churn_yes:,} churn-Yes ({churn_pct:.2%}); imbalance ratio
  {computed["churn_imbalance_ratio"]}; missing values per candidate:
  {computed["missing_values_by_candidate"]}; TotalCharges vs
  (tenure x MonthlyCharges) correlation:
  {computed["totalcharges_tenure_monthly_correlation"]}.

## 5. Assumptions, risks, limitations

- **Assumptions:** uniform Churn definition; representative snapshot;
  probabilities will be used for ranking with capacity-tuned thresholds.
- **Risks:** class imbalance (mitigated by stratified sampling + PR-AUC);
  no temporal validation possible (single snapshot); TotalCharges collinearity;
  demographic features may act as fairness-sensitive proxies.
- **Limitations:** no timestamps, no service-quality or competitor context;
  results are specific to this snapshot.

## 6. Data-leakage checks

1. Churn is the outcome itself - it will never enter the feature matrix.
2. No post-outcome columns exist in the dataset (verified column by column).
3. `TotalCharges` is an accumulated measure - kept only with documented
   collinearity treatment; available at scoring time for existing customers.
4. `customerID` excluded (unique ID, zero predictive value).

## 7. Open questions for the user

1. Are demographic attributes (gender, SeniorCitizen) acceptable as model
   features, or should they be excluded by fairness policy?
2. Is there a monthly retention-contact capacity to calibrate the decision
   threshold?
3. Should the model optimize recall (catch more churners) or precision
   (cheaper campaign)?

## 8. Alternatives considered

`tenure` (duration/survival view), `MonthlyCharges` (price regression),
`TotalCharges` (value regression) - each rated lower on business alignment
and/or actionability; details in `docs/json/target_proposal.json`.

## 9. Approval status

**`pending_user_approval`** - no model training will start until the user
explicitly approves (see `docs/json/target_approval.json`).
"""
    (DOCS_DIR / "target_proposal.md").write_text(md)

    print("Wrote docs/target_proposal.md")
    print("Wrote docs/json/target_proposal.json")
    print("Wrote docs/json/target_approval.json (status=pending)")
    print(json.dumps(computed, indent=1))


if __name__ == "__main__":
    main()

# Target Variable Proposal - Telco Customer Churn

> Phase 3 deliverable · Generated 2026-09-13 17:24 UTC · Status: **PENDING USER APPROVAL**
> Inputs: `problem_statement.md`, `business_analysis_report.md`, `data_dictionary.md`, `data_quality_report.md`, `json/insights.json`
> **Update:** approved by the user on 2026-09-13 — see `docs/json/target_approval.json` (status `approved`, target `Churn`, classification). The "pending" status below is kept as the historical record of this phase's deliverable.

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
- **Computed evidence** (this script): 7,043 rows;
  1,869 churn-Yes (26.54%); imbalance ratio
  2.77; missing values per candidate:
  {'tenure': 0, 'MonthlyCharges': 0, 'TotalCharges': 11, 'Churn': 0}; TotalCharges vs
  (tenure x MonthlyCharges) correlation:
  0.9996.

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

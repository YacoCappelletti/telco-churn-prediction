# Model Report - Telco Churn Classifier

> Generated 2026-09-13 · Target: `Churn` (validated, `docs/json/target_approval.json`) · problem type = classification

## 1. Problem definition

Predict, for each customer of the telecom operator, the probability that they
will churn (leave the company), so that retention actions (contract migration,
onboarding care, bundle offers, payment migration - see
`docs/business_analysis_report.md`) can be prioritized by expected risk
weighted by monthly revenue at risk.

## 2. Defined target variable

- **Target:** `Churn` (Yes/No) · **Positive class:** `Yes` · **Validation:** target defined and validated on 2026-09-13, recorded in `docs/json/target_approval.json`.
- **Type justification (classification):** the target is a binary outcome flag; the business need is a *ranking score* (probability) to prioritize a fixed-capacity retention campaign, not a numeric estimate; regression on `tenure`/charges was rejected in the target evaluation for weaker actionability and leakage/proxy concerns.

## 3. Data split

Stratified, seeded (random_state 42), identical across all scripts:

| Set | Rows | Purpose |
| --- | ---: | ------- |
| Train | 4,225 | CV evaluation (5-fold stratified), candidate comparison |
| Validation | 1,409 | Model selection + hyperparameter sanity |
| Test | 1,409 | **Single final evaluation** (used once) |

Preprocessing is always fitted inside the Pipeline (per CV fold / per fit) to
avoid leakage.

## 4. Preprocessing

- **Numeric** (`tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen`): median imputation + standard scaling (needed by logistic regression, harmless for trees).
- **Categorical** (15 columns: demographics, services, contract, billing): one-hot encoding with `handle_unknown="ignore"`.
- Raw-data fix (documented in the data quality report): 11 blank `TotalCharges` values imputed as `tenure × MonthlyCharges` before splitting.
- Resulting design matrix: 19 features → 45 encoded columns (4 numeric + 41 one-hot; see `models/model_metadata.json`).

## 5. Models tested (5-fold stratified CV on train, then validation)

| Model | CV accuracy | CV ROC-AUC | CV PR-AUC (AP) | Val AP | Val ROC-AUC |
| ----- | ---: | ---: | ---: | ---: | ---: |
| Baseline (Dummy prior) | 0.735 | - | 0.265 | 0.265 | - |
| Logistic Regression | 0.803 ± 0.011 | 0.848 ± 0.011 | 0.667 ± 0.025 | **0.642** | 0.841 |
| Decision Tree (depth 5) | 0.780 ± 0.010 | 0.819 ± 0.013 | 0.600 ± 0.015 | 0.596 | 0.815 |
| Random Forest (300 trees) | 0.795 ± 0.010 | 0.840 ± 0.010 | **0.673 ± 0.011** | 0.641 | 0.838 |

**Selection rule (business-aligned):** highest **validation average precision**
(PR-AUC), chosen because the 26.5% base rate makes plain accuracy misleading
(data quality report §7) and the retention use-case cares about ranking
precision-recall trade-offs. **Selected: Logistic Regression** (val AP 0.6424).
Note: Random Forest had the best CV AP but narrowly lower validation AP; the
validation set is the tie-breaker metric per plan, and the simpler, more
interpretable model wins when metrics are effectively tied (0.6424 vs 0.6405).

## 6. Final model - single test-set evaluation

Logistic Regression refit on train + validation (5,634 rows), evaluated **once**
on the untouched test set:

| Metric | Value |
| ------ | ----: |
| Accuracy | 0.806 |
| Precision | 0.657 |
| Recall | 0.559 |
| F1 | 0.604 |
| ROC-AUC | 0.842 |
| PR-AUC (AP) | 0.634 |
| Brier score | 0.138 |

**Confusion matrix (threshold 0.5):** TN 926 · FP 109 · FN 165 · TP 209.

![Final model performance](images/model_performance_charts.png)
*Figure M1 — Single test evaluation: PR curve, ROC curve, confusion matrix and permutation importance (top 12).*

**Business view:** ranking customers by predicted risk, the top 10% catch
**27.8% of all churners (lift 2.78x vs random)**. At ~$74 ARPU for churners
(see business analysis), a campaign touching the top decile addresses ≈ $38.7K of the
$139K/mo at-risk revenue.

**Calibration:** Brier 0.138 vs base-rate-implied 0.199 → probabilities are
usable for ranking and rough expected-loss sizing. There is no dedicated
reliability-curve panel; `model_performance_charts.png` (above) contains the
PR/ROC curves, the confusion matrix and the permutation importance.

## 7. Feature importance (permutation importance, test set, 10 repeats, scoring = AP)

| Rank | Feature | Mean AP drop | Std |
| --- | --- | ---: | ---: |
| 1 | `tenure` | 0.2404 | 0.0078 |
| 2 | `InternetService` | 0.0743 | 0.0152 |
| 3 | `MonthlyCharges` | 0.0631 | 0.0141 |
| 4 | `Contract` | 0.0438 | 0.0056 |
| 5 | `TotalCharges` | 0.0282 | 0.0097 |
| 6 | `StreamingMovies` | 0.0130 | 0.0098 |
| 7 | `TechSupport` | 0.0118 | 0.0039 |
| 8 | `OnlineSecurity` | 0.0097 | 0.0035 |

The model's story matches the business analysis: early-tenure customers on
premium fiber plans with month-to-month contracts are the churn core - the
same segments the business levers target.

## 8. Artifacts

| Artifact | Path |
| -------- | ---- |
| Final model (full pipeline) | `models/final_model.joblib` |
| Fitted preprocessor | `models/preprocessor.joblib` |
| Model metadata | `models/model_metadata.json` |
| Performance metrics | `docs/json/model_performance.json` |
| Feature importance | `docs/json/feature_importance.json` |
| Performance charts | `docs/images/model_performance_charts.png` |
| Model card (summary) | `docs/model_card.md` |

## 9. Limitations

- Single snapshot: no temporal validation; future drift is unmeasured.
- Probabilities from an unweighted LR: suited to ranking; if campaign economics
  change, re-tune the decision threshold on the validation set (not the test set).
- `TotalCharges` partially encodes tenure (kept with documented collinearity);
  dropping it barely changes ranking quality but improves transfer to brand-new
  customers.
- No causal claims: the model ranks risk, it does not measure the effect of
  interventions (A/B tests remain required).

## 10. Risks and next steps

- **Risks:** class imbalance handled but recall at 0.5 threshold (0.559) may be
  below campaign needs; degrade gracefully by lowering the threshold - the PR
  curve shows precision ≥ 0.65 for recall ≤ 0.5.
- **Next steps:** threshold calibration against retention capacity; fairness
  audit if demographics are used in customer-facing decisions; periodic
  retraining with fresh snapshots; A/B validation of model-guided campaigns.

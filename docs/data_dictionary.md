# Data Dictionary - Telco Customer Churn

> Generated: 2026-09-13 17:20 UTC · Source: `data/raw/Telco-Customer-Churn.csv` · Rows: 7,043 · Columns: 21

## Overview

| Property | Value |
| -------- | ----- |
| Source file | `data/raw/Telco-Customer-Churn.csv` (CSV, comma-separated, UTF-8) |
| Rows / Columns | 7,043 / 21 |
| Grain | One row = one customer snapshot (demographics, services, contract, billing, churn outcome flag) |
| Duplicate rows | 0 |
| Primary key | `customerID` (100% unique, 0% null) |
| Data source reference | IBM Telco Customer Churn sample dataset — Kaggle: https://www.kaggle.com/datasets/blastchar/telco-customer-churn (public sample data distributed by IBM for Cognos Analytics). |
| Inferred purpose | Telecom customer-base snapshot designed for retention analysis: each record bundles who the customer is, what they subscribed to, what they pay, and whether they churned |

## Column Summary

| # | Column | Role | Type | Unique | Missing % | Description |
| - | ------ | ---- | ---- | ------ | --------- | ----------- |
| 1 | `customerID` | Identifier | identifier (alphanumeric code (likely unique key)) | 7,043 | 0.00% | Unique customer identifier with format 'NNNN-XXXX' (digits + 5 alphanumeric characters). One per customer. |
| 2 | `gender` | Dimension | categorical | 2 | 0.00% | Customer gender (Male / Female). |
| 3 | `SeniorCitizen` | Status flag | boolean (0/1) | 2 | 0.00% | Binary flag marking customers aged 65+ (1 = senior, 0 = not). Numeric encoding of a boolean. |
| 4 | `Partner` | Status flag | boolean (yes/no) | 2 | 0.00% | Whether the customer has a spouse/partner (Yes/No). |
| 5 | `Dependents` | Status flag | boolean (yes/no) | 2 | 0.00% | Whether the customer has dependents in the household (Yes/No). |
| 6 | `tenure` | Metric | numeric | 73 | 0.00% | Customer tenure with the company in completed months (0 = brand new, max 72). Integer. |
| 7 | `PhoneService` | Status flag | boolean (yes/no) | 2 | 0.00% | Whether the customer subscribes to home phone service (Yes/No). |
| 8 | `MultipleLines` | Dimension | categorical | 3 | 0.00% | Phone add-on: multiple lines (Yes / No / No phone service). The 'No phone service' value encodes the structural dependency on PhoneService. |
| 9 | `InternetService` | Dimension | categorical | 3 | 0.00% | Internet technology: DSL, Fiber optic, or No internet service. |
| 10 | `OnlineSecurity` | Dimension | categorical | 3 | 0.00% | Internet add-on: online security (Yes / No / No internet service). |
| 11 | `OnlineBackup` | Dimension | categorical | 3 | 0.00% | Internet add-on: cloud backup (Yes / No / No internet service). |
| 12 | `DeviceProtection` | Dimension | categorical | 3 | 0.00% | Internet add-on: device protection plan (Yes / No / No internet service). |
| 13 | `TechSupport` | Dimension | categorical | 3 | 0.00% | Internet add-on: tech support plan (Yes / No / No internet service). |
| 14 | `StreamingTV` | Dimension | categorical | 3 | 0.00% | Entertainment add-on: streaming TV (Yes / No / No internet service). |
| 15 | `StreamingMovies` | Dimension | categorical | 3 | 0.00% | Entertainment add-on: streaming movies (Yes / No / No internet service). |
| 16 | `Contract` | Dimension | categorical | 3 | 0.00% | Contract type: Month-to-month, One year, or Two year. Defines the customer's commitment period and exit cost. |
| 17 | `PaperlessBilling` | Status flag | boolean (yes/no) | 2 | 0.00% | Whether the customer receives paperless billing (Yes/No). |
| 18 | `PaymentMethod` | Dimension | categorical | 4 | 0.00% | Payment method: Electronic check, Mailed check, Bank transfer (automatic), or Credit card (automatic). |
| 19 | `MonthlyCharges` | Metric | numeric | 1,585 | 0.00% | Recurring monthly charge for the customer's current bundle, in USD. Range $18.25-$118.75. |
| 20 | `TotalCharges` | Metric | string | 6,531 | 0.00% | Cumulative amount billed to the customer to date, in USD. Stored as text with 11 blank strings (all tenure = 0 customers). Range $18.80-$8,684.80, right-skewed. |
| 21 | `Churn` | Status flag | boolean (yes/no) | 2 | 0.00% | Outcome flag: whether the customer left the company within the observation window (Yes = churned, 26.54%; No = retained, 73.46%). |

Roles: Identifier · Metric · Dimension · Status flag · Target · Timestamp · Free text.

## Column Details

### `customerID`

- **Role:** Identifier · **Type:** identifier (alphanumeric code (likely unique key)) · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 7,043 (100.00%)
- **Description:** Unique customer identifier with format 'NNNN-XXXX' (digits + 5 alphanumeric characters). One per customer.
- **Examples:** `7590-VHVEG`, `5575-GNVDE`, `3668-QPYBK`
- **Feature candidate:** No - 100% unique per row: zero predictive value. Exclude from features; use only as a join key / traceability ID.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None. Randomly assigned identifier.

### `gender`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Customer gender (Male / Female).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `Male` | 3,555 | 50.48% |
  | `Female` | 3,488 | 49.52% |

- **Examples:** `Female`, `Male`
- **Feature candidate:** Yes - Standard demographic segmentation variable.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None. Known at signup.

### `SeniorCitizen`

- **Role:** Status flag · **Type:** boolean (0/1) · **Storage dtype:** `int64` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Binary flag marking customers aged 65+ (1 = senior, 0 = not). Numeric encoding of a boolean.
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `0` | 5,901 | 83.79% |
  | `1` | 1,142 | 16.21% |

- **Examples:** `0`, `1`
- **Feature candidate:** Yes - Age segment proxy; useful for demographic targeting of retention offers.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `Partner`

- **Role:** Status flag · **Type:** boolean (yes/no) · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Whether the customer has a spouse/partner (Yes/No).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 3,641 | 51.7% |
  | `Yes` | 3,402 | 48.3% |

- **Examples:** `Yes`, `No`
- **Feature candidate:** Yes - Household-size proxy; multi-person households churn less in telecom.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `Dependents`

- **Role:** Status flag · **Type:** boolean (yes/no) · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Whether the customer has dependents in the household (Yes/No).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 4,933 | 70.04% |
  | `Yes` | 2,110 | 29.96% |

- **Examples:** `No`, `Yes`
- **Feature candidate:** Yes - Family bundle indicator; correlates with plan choice and stickiness.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `tenure`

- **Role:** Metric · **Type:** numeric · **Storage dtype:** `int64` · **Missing:** 0 (0.00%)
- **Unique values:** 73 (1.04%)
- **Description:** Customer tenure with the company in completed months (0 = brand new, max 72). Integer.
- **Range:** 0 … 72 · mean 32.37 · median 29 · std 24.56 · IQR outliers: 0
- **Examples:** `1`, `34`, `2`
- **Feature candidate:** Yes - Strong behavioural variable: contract age at the snapshot date.
- **Candidate target (Phase 3):** Yes. Conceivable as a retention-duration outcome (regression / survival analysis), but weaker direct business actionability; to be evaluated in Phase 3.
- **Leakage risk:** None for churn-style prediction: tenure at scoring time is known. Perfectly collinear with TotalCharges accumulation.

### `PhoneService`

- **Role:** Status flag · **Type:** boolean (yes/no) · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Whether the customer subscribes to home phone service (Yes/No).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `Yes` | 6,361 | 90.32% |
  | `No` | 682 | 9.68% |

- **Examples:** `No`, `Yes`
- **Feature candidate:** Yes - Product-mix variable.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `MultipleLines`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Phone add-on: multiple lines (Yes / No / No phone service). The 'No phone service' value encodes the structural dependency on PhoneService.
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 3,390 | 48.13% |
  | `Yes` | 2,971 | 42.18% |
  | `No phone service` | 682 | 9.68% |

- **Examples:** `No phone service`, `No`, `Yes`
- **Feature candidate:** Yes - Product-mix variable with explicit structural category.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `InternetService`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Internet technology: DSL, Fiber optic, or No internet service.
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `Fiber optic` | 3,096 | 43.96% |
  | `DSL` | 2,421 | 34.37% |
  | `No` | 1,526 | 21.67% |

- **Examples:** `DSL`, `Fiber optic`, `No`
- **Feature candidate:** Yes - Core product line; largest monthly-charge differentiator (median $91.68 fiber vs $56.15 DSL).
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `OnlineSecurity`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Internet add-on: online security (Yes / No / No internet service).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 3,498 | 49.67% |
  | `Yes` | 2,019 | 28.67% |
  | `No internet service` | 1,526 | 21.67% |

- **Examples:** `No`, `Yes`, `No internet service`
- **Feature candidate:** Yes - Value-added service; retention-relevant add-on.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `OnlineBackup`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Internet add-on: cloud backup (Yes / No / No internet service).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 3,088 | 43.84% |
  | `Yes` | 2,429 | 34.49% |
  | `No internet service` | 1,526 | 21.67% |

- **Examples:** `Yes`, `No`, `No internet service`
- **Feature candidate:** Yes - Value-added service; retention-relevant add-on.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `DeviceProtection`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Internet add-on: device protection plan (Yes / No / No internet service).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 3,095 | 43.94% |
  | `Yes` | 2,422 | 34.39% |
  | `No internet service` | 1,526 | 21.67% |

- **Examples:** `No`, `Yes`, `No internet service`
- **Feature candidate:** Yes - Value-added service; retention-relevant add-on.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `TechSupport`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Internet add-on: tech support plan (Yes / No / No internet service).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 3,473 | 49.31% |
  | `Yes` | 2,044 | 29.02% |
  | `No internet service` | 1,526 | 21.67% |

- **Examples:** `No`, `Yes`, `No internet service`
- **Feature candidate:** Yes - Service-quality proxy; retention-relevant add-on.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `StreamingTV`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Entertainment add-on: streaming TV (Yes / No / No internet service).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 2,810 | 39.9% |
  | `Yes` | 2,707 | 38.44% |
  | `No internet service` | 1,526 | 21.67% |

- **Examples:** `No`, `Yes`, `No internet service`
- **Feature candidate:** Yes - Engagement/entertainment bundle variable.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `StreamingMovies`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Entertainment add-on: streaming movies (Yes / No / No internet service).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 2,785 | 39.54% |
  | `Yes` | 2,732 | 38.79% |
  | `No internet service` | 1,526 | 21.67% |

- **Examples:** `No`, `Yes`, `No internet service`
- **Feature candidate:** Yes - Engagement/entertainment bundle variable.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `Contract`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 3 (0.04%)
- **Description:** Contract type: Month-to-month, One year, or Two year. Defines the customer's commitment period and exit cost.
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `Month-to-month` | 3,875 | 55.02% |
  | `Two year` | 1,695 | 24.07% |
  | `One year` | 1,473 | 20.91% |

- **Examples:** `Month-to-month`, `One year`, `Two year`
- **Feature candidate:** Yes - Strongest commitment/switching-cost variable in the dataset; 55% of the base is month-to-month.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None. Contract type is known at any scoring time.

### `PaperlessBilling`

- **Role:** Status flag · **Type:** boolean (yes/no) · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Whether the customer receives paperless billing (Yes/No).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `Yes` | 4,171 | 59.22% |
  | `No` | 2,872 | 40.78% |

- **Examples:** `Yes`, `No`
- **Feature candidate:** Yes - Billing-behaviour variable; interacts with payment method.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `PaymentMethod`

- **Role:** Dimension · **Type:** categorical · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 4 (0.06%)
- **Description:** Payment method: Electronic check, Mailed check, Bank transfer (automatic), or Credit card (automatic).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `Electronic check` | 2,365 | 33.58% |
  | `Mailed check` | 1,612 | 22.89% |
  | `Bank transfer (automatic)` | 1,544 | 21.92% |
  | `Credit card (automatic)` | 1,522 | 21.61% |

- **Examples:** `Electronic check`, `Mailed check`, `Bank transfer (automatic)`
- **Feature candidate:** Yes - Distinguishes manual vs automatic payments - a known friction/retention lever.
- **Candidate target (Phase 3):** No.
- **Leakage risk:** None.

### `MonthlyCharges`

- **Role:** Metric · **Type:** numeric · **Storage dtype:** `float64` · **Missing:** 0 (0.00%)
- **Unique values:** 1,585 (22.50%)
- **Description:** Recurring monthly charge for the customer's current bundle, in USD. Range $18.25-$118.75.
- **Range:** 18.25 … 118.75 · mean 64.76 · median 70.35 · std 30.09 · IQR outliers: 0
- **Examples:** `29.85`, `56.95`, `53.85`
- **Feature candidate:** Yes - Core price variable; price-sensitivity analyses.
- **Candidate target (Phase 3):** Yes. Could serve as a price/ARPU regression outcome, but weak business actionability as a target; to be evaluated in Phase 3.
- **Leakage risk:** None. Known for any active customer at scoring time.

### `TotalCharges`

- **Role:** Metric · **Type:** string · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 6,531 (92.73%)
- **Description:** Cumulative amount billed to the customer to date, in USD. Stored as text with 11 blank strings (all tenure = 0 customers). Range $18.80-$8,684.80, right-skewed.
- **Range:** 18.8 … 8684.8 · mean 2283.3 · median 1397.47 · std 2266.77 · IQR outliers: 0
- **Examples:** `29.85`, `1889.5`, `108.15`
- **Feature candidate:** Yes - Lifetime revenue proxy. Requires cleaning (numeric coercion + imputation of 11 blanks, e.g. tenure x MonthlyCharges).
- **Candidate target (Phase 3):** Yes. Candidate for a customer-value / revenue regression, but weak actionability as a direct target; to be evaluated in Phase 3.
- **Leakage risk:** Temporal-proxy risk: TotalCharges accumulates over tenure and is approximately tenure x MonthlyCharges, so it partially encodes tenure. It is available at scoring time for existing customers, but a model relying on it would not generalise to brand-new customers. Check collinearity before use.

### `Churn`

- **Role:** Status flag · **Type:** boolean (yes/no) · **Storage dtype:** `str` · **Missing:** 0 (0.00%)
- **Unique values:** 2 (0.03%)
- **Description:** Outcome flag: whether the customer left the company within the observation window (Yes = churned, 26.54%; No = retained, 73.46%).
- **Allowed values:**

  | Value | Count | % |
  | ----- | -----: | -: |
  | `No` | 5,174 | 73.46% |
  | `Yes` | 1,869 | 26.54% |

- **Examples:** `No`, `Yes`
- **Feature candidate:** No - It is the only outcome-like flag in the dataset. If it were used as a feature for any model, it would leak the very outcome being predicted. Must be excluded from feature matrices.
- **Candidate target (Phase 3):** Yes. Only outcome-like flag in the dataset; natural candidate-target for retention problems. Selection/ranking belongs to Phase 3 - no decision is made here.
- **Leakage risk:** It IS the outcome. Using it as a feature would be target leakage; predicting it is the legitimate use, pending Phase 3 approval.

## Key & Relationships

| Column | Evidence | Assessment |
| ------ | -------- | ---------- |
| `customerID` | 7,043 unique values = row count, 0 null | Primary key |
| `MultipleLines` | `No phone service` count (682) equals `PhoneService = No` count | Dependent on `PhoneService` |
| `OnlineSecurity` … `StreamingMovies` | `No internet service` count (1,526) equals `InternetService = No` count | Dependent on `InternetService` |
| `TotalCharges` | 11 blanks align exactly with `tenure = 0` rows | Dependent on `tenure` accumulation |

Single-table dataset: no foreign keys to external tables.

## Data Quality Notes

| # | Column | Issue | Evidence | Recommendation |
| - | ------ | ----- | -------- | -------------- |
| 1 | `TotalCharges` | Implicit nulls / wrong storage type | 11 blank strings `" "` stored in an otherwise numeric column (0.16%); all belong to `tenure = 0` customers | Coerce to numeric; impute as `tenure × MonthlyCharges` (first invoice) or drop the 11 rows |
| 2 | `SeniorCitizen` | Numeric encoding of a boolean | Stored as 0/1 int | Treat as categorical boolean in analysis and UI |
| 3 | `Churn` | Moderate class imbalance | Yes = 26.54% vs No = 73.46% (ratio 2.77 : 1) | If modeled, use stratified splits and imbalance-aware metrics (no target decision in this phase) |
| 4 | `TotalCharges` | Right skew (accumulation) | Max $8,684.80 vs median $1,397.48 | Not an error: reflects long-tenure customers; consider log transform or capping in modeling |
| 5 | Add-on columns | Redundant structural level | `No internet service` / `No phone service` duplicate information already in `InternetService` / `PhoneService` | Keep as-is (informative) or normalise to Yes/No + separate flag |

## Glossary

| Term | Definition |
| ---- | ---------- |
| Churn | Customer leaving the company within the observation window (`Churn = Yes`) |
| Tenure | Completed months of customer relationship (0 = brand new) |
| Month-to-month | Contract with no commitment period; customer can leave any month |
| DSL / Fiber optic | Internet technologies offered; fiber is the premium tier (median monthly charge $91.68 vs $56.15) |
| Electronic check | Manual, non-recurring payment method; contrast with automatic bank transfer / credit card |
| ARPU | Average revenue per user, approximated here by `MonthlyCharges` |

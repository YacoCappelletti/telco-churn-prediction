# API Documentation - Telco Churn Prediction API

> Phase 5 deliverable · FastAPI app: `src/api/main.py` · Run: `make api` → http://localhost:8000 · Interactive docs: `/docs` (Swagger UI)

## 1. Overview

REST API that exposes the approved churn model (`Churn`, binary
classification, logistic regression pipeline v1.0.0). Every prediction
includes the probability, risk band, main contributing factors and a business
recommendation.

## 2. Endpoints

### `GET /health`

Service + model status.

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "telco_churn_classifier",
  "model_version": "1.0.0",
  "timestamp": "2026-09-13T19:29:23+00:00"
}
```

- `status`: `ok` (model loaded) or `degraded` (service up, model missing).
- `model_loaded`: false → `/v1/predict` will answer `503`.

### `POST /v1/predict`

**Input** (all 19 model features; validation mirrors the data dictionary):

| Field | Type | Constraints |
| ----- | ---- | ----------- |
| gender | enum | `Female` \| `Male` |
| SeniorCitizen | int | 0-1 |
| Partner, Dependents, PhoneService, PaperlessBilling | enum | `Yes` \| `No` |
| tenure | int | 0-72 (completed months) |
| MultipleLines | enum | `No` \| `Yes` \| `No phone service` |
| InternetService | enum | `DSL` \| `Fiber optic` \| `No` |
| OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies | enum | `No` \| `Yes` \| `No internet service` |
| Contract | enum | `Month-to-month` \| `One year` \| `Two year` |
| PaymentMethod | enum | `Electronic check` \| `Mailed check` \| `Bank transfer (automatic)` \| `Credit card (automatic)` |
| MonthlyCharges | float | 0-500 USD |
| TotalCharges | float | 0-20000 USD |

**Response:**

```json
{
  "customer_risk": {
    "churn_probability": 0.7746,
    "prediction": "Yes",
    "risk_level": "high"
  },
  "contributing_factors": [
    {"feature": "Contract", "direction": "increases_risk", "description": "Contract type = Month-to-month pushes churn risk up"},
    {"feature": "tenure", "direction": "increases_risk", "description": "Tenure pushes churn risk up"}
  ],
  "business_recommendation": "Contact this customer within 48 hours...",
  "model_version": "1.0.0",
  "model_name": "telco_churn_classifier",
  "timestamp": "2026-09-13T19:29:23+00:00"
}
```

Risk bands (from `configs/model_config.json`): **high ≥ 0.60**, **medium ≥ 0.35**, **low < 0.35**.

**Errors:** `422` (validation, with field-level details), `503` (model unavailable), `500` (unexpected failure, logged).

### `GET /v1/model-card`

Returns `models/model_metadata.json`: name, version, approved target, problem
type, feature list, preprocessing summary, validation/test metrics, library
versions and limitations.

## 3. Model versioning

The version comes from `models/model_metadata.json` (`model_version: 1.0.0`,
produced by `scripts/evaluate_final_model.py`). The artifact path is
`models/final_model.joblib`; replacing that file + metadata file updates the
API without code changes (restart required).

## 4. Logging

Structured request logging via Python logging (`LOG_LEVEL` env, default
INFO). Each prediction logs probability and risk level; model load/unavailable
states are logged at startup.

## 5. Examples

Complete request/response examples (high-risk and low-risk profiles, health,
model card) live in `docs/json/api_examples.json`.

## 6. Tests

`tests/test_api.py` (7 tests, `make test`): health, valid prediction
(invariant checks), high-risk profile classification, invalid categorical
(422), out-of-range numeric (422), missing field (422), model card contents.

## 7. Implementation notes

- Explanation method: linear-model logit contributions
  (`coef × standardized value`) aggregated to original feature groups —
  consistent with the selected model (logistic regression).
- Recommendations are rule-based per risk band, aligned with the four
  business levers from Phase 2 (contract migration, onboarding, bundling,
  payment migration).
- Schemas: `src/api/schemas.py` · Prediction logic: `src/api/predict.py`.

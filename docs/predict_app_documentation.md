# Predictive App Documentation - Telco Churn Predictor

> Phase 6 deliverable · App: `apps/predict_app/app.py` · Run: `make predict-app` (Streamlit, port 8501 by default)

## 1. What it does

A form-based app for retention teams to score one customer at a time:

1. Enter the customer profile (19 features, grouped: demographics, services,
   contract & billing).
2. The app validates inputs client-side (select boxes bound to the data
   dictionary domains; numeric bounds) and shows **warnings** for suspicious
   combinations (e.g., tenure = 0 with a large TotalCharges).
3. It calls the prediction API (`POST /v1/predict`) and displays:
   - **Churn probability** (progress bar + metric)
   - **Prediction** at the 0.5 threshold and the **risk band**
     (high ≥ 60% / medium ≥ 35% / low < 35%)
   - **Main contributing factors** (increases/decreases risk)
   - **Business recommendation** per risk band (contract migration, bundling,
     payment migration — the four Phase 2 levers)
   - Model name/version and scoring timestamp for traceability

## 2. Configuration

- `API_BASE_URL` (env or `.env`): API address. Defaults to
  `http://localhost:8000` for local runs; in Docker Compose it is
  `http://api:8000`.
- The sidebar shows the API health (`GET /health`) on every page load: green =
  model loaded; red = API unreachable (`make api`) or model not loaded.

## 3. How to run

```bash
make api          # terminal 1 - FastAPI on :8000
make predict-app  # terminal 2 - Streamlit on :8501
```

Open http://localhost:8501. In Docker Compose both services start together
(`docker compose up`).

## 4. Input guidance

- Use the exact contract/service domains from the data dictionary — the API
  rejects unknown values with HTTP 422 and the app shows the detail.
- `tenure` is completed months (0-72); new customers = 0.
- Charges in USD; `TotalCharges` is the accumulated lifetime billing amount.

## 5. Error handling

| Situation | Behavior |
| --------- | -------- |
| API unreachable | Red banner with the fix (`make api`) |
| Model not loaded (health `degraded`) | Sidebar error; predict returns 503 |
| Invalid input (422) | Validation detail from the API shown |
| Suspicious value combinations | Yellow warnings; prediction still allowed |
| Network/timeout failure | Error message with the cause |

## 6. Example (matching `docs/json/api_examples.json`)

New fiber customer, month-to-month, electronic check, low tenure →
probability ≈ 0.77, risk **high**, recommendation: contact within 48 hours
with contract migration + protection bundle + automatic payments.

# Telco Marketing Campaign - End-to-End Churn Analytics

End-to-end analytical solution over the **IBM Telco Customer Churn** dataset
(7,043 customers × 21 columns): data audit, business analysis, an
**approved-target churn model** served through an API, a predictive Streamlit
app, a business dashboard, and Docker deployment.

> Process note: the target variable (`Churn`, binary classification) was
> proposed in Phase 3 and **explicitly approved by the user** before any
> model training (see `docs/json/target_approval.json`).

## Key findings

- 26.5% of customers churn → **$139K/month (30.5% of MRR, $1.67M annualized)**
  of revenue sits in churned accounts (churners carry +21.5% ARPU).
- Risk concentrates in: **month-to-month contracts (42.7% churn)**, the
  **first year of tenure (55.5% of all churn)**, **fiber-optic users
  (41.9%)**, and **electronic-check payers (45.3%)**.
- Final model: **Logistic Regression** (test PR-AUC 0.634, ROC-AUC 0.842,
  top-decile lift 2.78x). Full story: `docs/model_report.md`.

## Project structure

```
├── data/raw/                  # Source dataset
├── docs/                      # All reports (md), snippets/, json/, images/
├── scripts/                   # 00..02 phase scripts, q01..q05, train_*, evaluate_final_model
├── src/data/                  # Shared loaders/utils
├── src/model/                 # Preprocessing pipeline + config helpers
├── src/api/                   # FastAPI app (main, schemas, predict)
├── apps/predict_app/          # Streamlit predictive app
├── apps/dashboard/            # Streamlit business dashboard
├── models/                    # final_model.joblib, preprocessor.joblib, metadata
├── tests/                     # test_data, test_model, test_api (19 tests)
├── configs/                   # project + model configs
└── Dockerfile, docker-compose.yml, Makefile, requirements.txt
```

## Quickstart

```bash
# Local (pinned deps in a venv)
make setup          # creates venv + installs requirements.txt
make test           # 19 tests (data, model, API)
make api            # API on :8000 (Swagger at /docs)
make predict-app    # Streamlit app on :8501
make dashboard      # Business dashboard (run separately: set a different port)

# Or everything at once with Docker
make docker-up      # API :8010 · app :8511 · dashboard :8512 (see deployment docs)
```

Reproduce the full analysis from scratch:

```bash
make audit && make dictionary && make business && make proposal
# Phase 3 gate: approve the target in docs/json/target_approval.json
make train && make test
```

## Pipeline

1. **Phase 1** - Data audit: quality report + data dictionary + problem
   statement (no target selection).
2. **Phase 2** - Business analysis: 10 questions → 5 selected, each with
   script, snippet, metrics JSON and chart.
3. **Phase 3** - Target proposal (`Churn`, classification) → **user approval
   gate** (`docs/json/target_approval.json`).
4. **Phase 4** - Baseline + LR/DT/RF candidates (5-fold stratified CV) →
   single test evaluation → artifacts + reports.
5. **Phase 5** - FastAPI with validation, logging, versioning and explanations.
6. **Phase 6** - Streamlit predictive app connected to the API.
7. **Phase 7** - Business dashboard (KPIs, 5 questions, filters, actions).
8. **Deployment** - Docker Compose (api + predict_app + dashboard).

## Documentation index

| Document | Content |
| -------- | ------- |
| `docs/data_dictionary.md` | 21-column dictionary (types, domains, feature/target flags, leakage) |
| `docs/data_quality_report.md` | Missing values, duplicates, outliers, imbalance, distributions |
| `docs/problem_statement.md` | Business problems and why churn was chosen |
| `docs/business_questions.md` + `business_analysis_report.md` | 10 questions, 5 selected, insights and actions |
| `docs/target_proposal.md` | Target candidates evaluated on 14 criteria |
| `docs/model_report.md` + `model_card.md` | Training, metrics, feature importance, limitations |
| `docs/api_documentation.md` | Endpoints, schemas, errors, examples |
| `docs/predict_app_documentation.md` / `dashboard_documentation.md` | App and dashboard guides |
| `docs/deployment_documentation.md` | Docker architecture and operations |

## Governance

- Target approval gate recorded in `docs/json/target_approval.json`
  (`approved`, 2026-09-13).
- No notebooks; every insight is justified with code in `/scripts`.
- Tests: `make test` (data contracts, model artifacts, API behavior).

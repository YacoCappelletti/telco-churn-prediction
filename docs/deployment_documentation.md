# Deployment Documentation

> Deliverables: `Dockerfile`, `docker-compose.yml`, `.env.example`, this document · Verified with `docker compose up --build` from a clean environment.

## 1. Architecture

| Service | Host port | What it serves |
| ------- | --------- | -------------- |
| `api` | 8010 → container 8000 | FastAPI: `/health`, `/v1/predict`, `/v1/model-card` |
| `predict_app` | 8511 → container 8501 | Streamlit predictive app (calls the API via `http://api:8000`) |
| `dashboard` | 8512 → container 8502 | Streamlit business dashboard |

> Host ports 8010/8511/8512 were chosen because 8000/8501/8502 are occupied
> by another project on this machine; change the left side of the port
> mappings in `docker-compose.yml` freely.

All three services share one image (Python 3.13-slim + pinned
`requirements.txt`) with different startup commands. The image bundles the
code, configs, `docs/json` narrative data, the raw CSV and the trained model
artifacts — no network or volume mounts needed at runtime.

## 2. Quick start

```bash
docker compose up -d --build
```

Then:

- API Swagger UI: http://localhost:8010/docs
- Predictive app: http://localhost:8511
- Business dashboard: http://localhost:8512

Stop: `docker compose down` (or `make docker-down`).

## 3. Environment variables

Copy `.env.example` → `.env` and adjust (compose reads it automatically):

| Variable | Default | Used by |
| -------- | ------- | ------- |
| `API_HOST` / `API_PORT` | 0.0.0.0 / 8000 | API |
| `LOG_LEVEL` | INFO | API logging |
| `API_BASE_URL` | http://api:8000 | predict app → API connection |
| `MODEL_VERSION` | 1.0.0 | metadata labeling |

## 4. Health checks

The API service has a compose healthcheck (`GET /health` inside the
container). `predict_app` waits for `api` to be healthy before starting, so
the app always finds the API on boot.

## 5. Reproducibility from a clean environment

1. Fresh clone + `data/raw/Telco-Customer-Churn.csv` present.
2. `make setup` (local venv) or `docker compose up --build` (containers).
3. Reproduce analysis and artifacts from scratch:
   ```bash
   make audit && make dictionary && make business && make proposal
   # Phase 3 gate: approve target in docs/json/target_approval.json
   make train && make test
   ```
4. Artifacts are regenerated deterministically (fixed random seed 42).

## 6. Model updates

Retrain (after re-running `make train`) and rebuild the image — or simply
replace `models/final_model.joblib` and `models/model_metadata.json` and
restart the `api` service; the API loads them at startup and reports the new
version via `/health` and `/v1/model-card`.

## 7. Verification performed

- `docker compose build` succeeds from a clean state.
- All three services start and respond: API `/health` returns
  `model_loaded: true`; both Streamlit apps return HTTP 200 with the expected
  titles.
- API prediction smoke test with the high-risk profile from
  `docs/json/api_examples.json` returns probability 0.79 / risk high; invalid
  input returns 422.

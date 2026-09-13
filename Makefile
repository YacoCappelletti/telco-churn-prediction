PY       := venv/bin/python
PIP      := venv/bin/pip
API_PORT := 8000

.PHONY: setup audit dictionary problem business proposal train api predict-app dashboard docker-build docker-up docker-down test clean

setup:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

## Phase 1
audit:
	$(PY) scripts/00_data_audit.py

dictionary:
	$(PY) scripts/01_create_data_dictionary.py

## Phase 2
business:
	$(PY) scripts/q01_churn_rate_by_contract.py
	$(PY) scripts/q02_tenure_vs_churn.py
	$(PY) scripts/q03_services_and_churn.py
	$(PY) scripts/q04_revenue_at_risk.py
	$(PY) scripts/q05_payment_and_billing.py

## Phase 3
proposal:
	$(PY) scripts/02_target_proposal.py

## Phase 4
train:
	$(PY) scripts/train_baseline.py
	$(PY) scripts/train_candidate_models.py
	$(PY) scripts/evaluate_final_model.py

## Phase 5-7
api:
	$(PY) -m uvicorn src.api.main:app --host 0.0.0.0 --port $(API_PORT)

predict-app:
	$(PY) -m streamlit run apps/predict_app/app.py

dashboard:
	$(PY) -m streamlit run apps/dashboard/app.py

## Deployment
docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

## Tests
test:
	$(PY) -m pytest tests/ -v

clean:
	rm -rf __pycache__ src/__pycache__ src/api/__pycache__ tests/__pycache__ .pytest_cache

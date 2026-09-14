"""FastAPI application exposing the Telco churn prediction model.

Endpoints:
- GET  /health         -> service and model status
- POST /v1/predict     -> churn probability + explanation + recommendation
- GET  /v1/model-card  -> trained model metadata (model card)

Run: make api  (uvicorn src.api.main:app --host 0.0.0.0 --port 8000)
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from src.api.predict import load_metadata, load_model, predict_one
from src.api.schemas import HealthOutput, PredictionInput, PredictionOutput
from src.model.pipeline import load_config

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("telco_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    app.state.model = load_model()
    app.state.metadata = load_metadata()
    app.state.config = load_config()
    if app.state.model is not None:
        logger.info(
            "Model %s v%s loaded",
            app.state.metadata.get("model_name"),
            app.state.metadata.get("model_version"),
        )
    else:
        logger.error("Model not loaded - /v1/predict will return 503")
    yield
    app.state.model = None


app = FastAPI(
    title="Telco Churn Prediction API",
    version="1.0.0",
    description=(
        "Predicts customer churn probability for a telecom operator and "
        "explains the main contributing factors with a business recommendation. "
        "Trained on the `Churn` target (see docs/target_proposal.md)."
    ),
    lifespan=lifespan,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health", response_model=HealthOutput)
def health() -> HealthOutput:
    """Liveness/readiness probe with model availability."""
    model_loaded = getattr(app.state, "model", None) is not None
    metadata = getattr(
        app.state, "metadata", {"model_name": "unknown", "model_version": "unknown"}
    )
    return HealthOutput(
        status="ok" if model_loaded else "degraded",
        model_loaded=model_loaded,
        model_name=metadata.get("model_name", "unknown"),
        model_version=metadata.get("model_version", "unknown"),
        timestamp=_now(),
    )


@app.post("/v1/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput) -> PredictionOutput:
    """Score one customer: churn probability, drivers and recommendation."""
    model = getattr(app.state, "model", None)
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not available. Check /health and the model artifacts.",
        )
    try:
        result = predict_one(
            model,
            payload.model_dump(),
            config=app.state.config,
            metadata=app.state.metadata,
        )
    except Exception as exc:  # pragma: no cover - defensive catch-all
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc
    logger.info(
        "prediction prob=%.4f risk=%s",
        result["customer_risk"]["churn_probability"],
        result["customer_risk"]["risk_level"],
    )
    return PredictionOutput(**result)


@app.get("/v1/model-card")
def model_card() -> dict:
    """Full model metadata (name, version, metrics, features, limitations).

    Risk bands are merged from the model config so clients (e.g. the Streamlit
    app) can render thresholds from the single source of truth.
    """
    metadata = getattr(app.state, "metadata", None)
    if not metadata:
        raise HTTPException(status_code=503, detail="Model metadata not available.")
    config = getattr(app.state, "config", None) or {}
    return {**metadata, "risk_bands": config.get("risk_bands", {})}

import logging
import uuid
from typing import Any

import joblib
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from auth import verify_api_key
from config import settings
from models import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MTCars MPG Prediction API",
    description="A production-style FastAPI app that serves a sklearn model.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(429, "Rate limit exceeded"))
app.add_middleware(SlowAPIMiddleware)

model_bundle: dict[str, Any] | None = None


@app.on_event("startup")
def load_model() -> None:
    global model_bundle
    model_bundle = joblib.load(settings.model_path)
    logger.info("model loaded from %s", settings.model_path)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    if model_bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


@app.post("/v1/predict", response_model=PredictionResponse)
@limiter.limit("100/minute")
def predict(
    request: Request,
    prediction_request: PredictionRequest,
    api_key: str = Depends(verify_api_key),
) -> PredictionResponse:
    try:
        model = model_bundle["model"]
        model_version = model_bundle["model_version"]

        prediction = model.predict([prediction_request.features])[0]
        confidence = model.predict_proba([prediction_request.features]).max()

        return PredictionResponse(
            prediction=float(prediction),
            confidence=float(confidence),
            model_version=model_version,
            request_id=str(uuid.uuid4()),
        )
    except Exception as exc:
        logger.error("prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail="Prediction failed")


@app.post("/v1/predict/batch", response_model=BatchPredictionResponse)
@limiter.limit("30/minute")
def batch_predict(
    request: Request,
    batch_request: BatchPredictionRequest,
    api_key: str = Depends(verify_api_key),
) -> BatchPredictionResponse:
    if len(batch_request.instances) > settings.max_batch_size:
        raise HTTPException(status_code=400, detail="Batch size too large")

    try:
        model = model_bundle["model"]
        model_version = model_bundle["model_version"]

        predictions = model.predict(batch_request.instances)
        probabilities = model.predict_proba(batch_request.instances)

        confidences = probabilities.max(axis=1)

        return BatchPredictionResponse(
            predictions=[float(x) for x in predictions],
            confidences=[float(x) for x in confidences],
            count=len(batch_request.instances),
            model_version=model_version,
        )
    except Exception as exc:
        logger.error("batch prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail="Batch prediction failed")


@app.get("/v1/model/info")
def model_info(api_key: str = Depends(verify_api_key)) -> dict[str, Any]:
    if model_bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_version": model_bundle["model_version"],
        "features": model_bundle["features"],
        "target": model_bundle["target"],
        "model_type": "RandomForestClassifier",
    }

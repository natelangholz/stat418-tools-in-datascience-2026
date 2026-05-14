"""Production FastAPI application serving an Iris species classifier."""
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import joblib
import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from auth import verify_api_key
from config import settings
from models import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfo,
    PredictionRequest,
    PredictionResponse,
    ReadyResponse,
)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Model state ──────────────────────────────────────────────────────────────
_model = None
CLASS_NAMES = ["setosa", "versicolor", "virginica"]
FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]


# ── Lifespan (load model at startup) ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup; release on shutdown."""
    global _model
    try:
        _model = joblib.load(settings.model_path)
        logger.info(f"Model loaded from '{settings.model_path}'")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    yield
    _model = None
    logger.info("Model unloaded")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Iris Species Classifier API",
    description="Production-ready ML API that predicts Iris flower species from measurements.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware: request logging ───────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its response status."""
    req_id = str(uuid.uuid4())[:8]
    logger.info(f"[{req_id}] {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"[{req_id}] → {response.status_code}")
    return response


# ── Health & readiness ────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health_check() -> HealthResponse:
    """Liveness check — returns 200 if the service is running."""
    return HealthResponse(status="healthy")


@app.get("/ready", response_model=ReadyResponse, tags=["Monitoring"])
def readiness_check() -> ReadyResponse:
    """Readiness check — returns 200 only if the model is loaded."""
    if _model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded")
    return ReadyResponse(status="ready", model_loaded=True)


# ── Model info ────────────────────────────────────────────────────────────────
@app.get("/v1/model/info", response_model=ModelInfo, tags=["Model"])
def model_info(api_key: str = Depends(verify_api_key)) -> ModelInfo:
    """Return metadata about the loaded model."""
    if _model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded")
    return ModelInfo(
        name="RandomForestClassifier",
        version="v1.0",
        description="Iris species classifier trained on the UCI Iris dataset (150 samples).",
        features=FEATURE_NAMES,
        classes=CLASS_NAMES,
        accuracy=1.0,
    )


# ── Single prediction ─────────────────────────────────────────────────────────
@app.post("/v1/predict", response_model=PredictionResponse, tags=["Prediction"])
@limiter.limit("100/minute")
def predict(
    request: Request,
    body: PredictionRequest,
    api_key: str = Depends(verify_api_key),
) -> PredictionResponse:
    """Predict the Iris species for a single flower measurement.

    Requires the `api-key` header. Rate limited to 100 requests/minute.
    """
    if _model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded")
    try:
        X = np.array([body.features])
        pred_idx = int(_model.predict(X)[0])
        proba = _model.predict_proba(X)[0]
        confidence = float(proba.max())
        logger.info(f"Prediction: class={CLASS_NAMES[pred_idx]}, confidence={confidence:.3f}")
        return PredictionResponse(
            prediction=float(pred_idx),
            predicted_class=CLASS_NAMES[pred_idx],
            confidence=confidence,
            model_version="v1.0",
            request_id=str(uuid.uuid4()),
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed")


# ── Batch prediction ──────────────────────────────────────────────────────────
@app.post("/v1/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
@limiter.limit("20/minute")
def predict_batch(
    request: Request,
    body: BatchPredictionRequest,
    api_key: str = Depends(verify_api_key),
) -> BatchPredictionResponse:
    """Predict Iris species for multiple flower measurements at once.

    Accepts up to 100 instances per request. Rate limited to 20/minute.
    """
    if _model is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not loaded")
    if len(body.instances) > settings.max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Batch size exceeds maximum of {settings.max_batch_size}",
        )
    try:
        X = np.array(body.instances)
        pred_indices = _model.predict(X).tolist()
        predicted_classes = [CLASS_NAMES[int(i)] for i in pred_indices]
        logger.info(f"Batch prediction: {len(pred_indices)} instances")
        return BatchPredictionResponse(
            predictions=[float(i) for i in pred_indices],
            predicted_classes=predicted_classes,
            count=len(pred_indices),
            model_version="v1.0",
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Batch prediction failed")

"""Production FastAPI service for soccer player market value prediction.

Serves a RandomForest regressor trained on 2,013 players from the top 5
European leagues. Exposes health checks, single and batch prediction, and
model metadata, with API key auth, rate limiting, and CORS.
"""
import logging
import uuid
from typing import Dict, List, Tuple

import joblib
import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from auth import verify_api_key
from config import settings
from models import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Player Market Value API",
    description="Predicts soccer player market values from performance stats.",
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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Model bundle is populated at startup: model, features, version, metrics.
_bundle: Dict = None


@app.on_event("startup")
def load_model() -> None:
    """Load the model bundle from disk when the service starts."""
    global _bundle
    try:
        _bundle = joblib.load(settings.model_path)
        logger.info("Model loaded from %s (version %s)", settings.model_path, _bundle["model_version"])
    except Exception as e:  # noqa: BLE001 - log and stay up so /ready reports 503
        logger.error("Failed to load model: %s", e)
        _bundle = None


def _predict_one(features: List[float]) -> Tuple[float, float]:
    """Predict market value and a confidence score for one feature vector.

    Confidence is derived from the spread of the RandomForest's trees:
    a tight spread (trees agree) gives confidence near 1.
    """
    model = _bundle["model"]
    X = np.asarray(features, dtype=float).reshape(1, -1)
    tree_preds = np.array([tree.predict(X)[0] for tree in model.estimators_])
    log_pred = float(tree_preds.mean())
    log_std = float(tree_preds.std())
    value = float(np.exp(log_pred))
    confidence = float(np.exp(-log_std))  # in (0, 1]
    return round(value, 2), round(confidence, 4)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Liveness probe. Always returns 200 while the process is running."""
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check() -> Dict[str, str]:
    """Readiness probe. Returns 503 until the model is loaded."""
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


@app.post("/v1/predict", response_model=PredictionResponse)
@limiter.limit("100/minute")
def predict(
    request: Request,
    payload: PredictionRequest,
    api_key: str = Depends(verify_api_key),
) -> PredictionResponse:
    """Predict the market value for a single player."""
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    request_id = str(uuid.uuid4())
    try:
        value, confidence = _predict_one(payload.features)
    except Exception as e:  # noqa: BLE001
        logger.error("[%s] prediction failed: %s", request_id, e)
        raise HTTPException(status_code=500, detail="Prediction failed")

    logger.info("[%s] predicted EUR %.0f", request_id, value)
    return PredictionResponse(
        prediction=value,
        confidence=confidence,
        model_version=_bundle["model_version"],
        request_id=request_id,
    )


@app.post("/v1/predict/batch", response_model=BatchPredictionResponse)
@limiter.limit("20/minute")
def predict_batch(
    request: Request,
    payload: BatchPredictionRequest,
    api_key: str = Depends(verify_api_key),
) -> BatchPredictionResponse:
    """Predict market values for up to 100 players in one request."""
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(payload.instances) > settings.max_batch_size:
        raise HTTPException(
            status_code=422,
            detail=f"Batch size exceeds limit of {settings.max_batch_size}",
        )

    request_id = str(uuid.uuid4())
    try:
        predictions = [_predict_one(row)[0] for row in payload.instances]
    except Exception as e:  # noqa: BLE001
        logger.error("[%s] batch prediction failed: %s", request_id, e)
        raise HTTPException(status_code=500, detail="Batch prediction failed")

    logger.info("[%s] predicted batch of %d", request_id, len(predictions))
    return BatchPredictionResponse(
        predictions=predictions,
        count=len(predictions),
        model_version=_bundle["model_version"],
    )


@app.get("/v1/model/info")
def model_info(api_key: str = Depends(verify_api_key)) -> Dict:
    """Return model metadata: version, features, and training metrics."""
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "model_version": _bundle["model_version"],
        "model_type": "RandomForestRegressor",
        "target": _bundle["target"],
        "features": _bundle["features"],
        "n_features": len(_bundle["features"]),
        "n_train": _bundle["n_train"],
        "metrics": _bundle["metrics"],
    }

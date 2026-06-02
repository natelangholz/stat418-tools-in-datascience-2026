"""MTCARS FastAPI application."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "model.pkl"
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        load_model()
    except FileNotFoundError:
        logger.warning("Model not loaded at startup; /ready will report unavailable")
    yield


app = FastAPI(
    title="MTCARS MPG Prediction API",
    description="Linear regression API predicting mpg from vehicle features.",
    version="1.0.0",
    lifespan=lifespan,
)

_model_artifact: dict[str, Any] | None = None


class PredictionRequest(BaseModel):
    wt: float = Field(..., gt=0, description="Vehicle weight (1000 lbs)")
    hp: float = Field(..., gt=0, description="Gross horsepower")


def load_model() -> dict[str, Any]:
    global _model_artifact
    if _model_artifact is not None:
        return _model_artifact

    if not MODEL_PATH.is_file():
        logger.error("Model file not found at %s", MODEL_PATH)
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    _model_artifact = joblib.load(MODEL_PATH)
    logger.info("Loaded model from %s with features %s", MODEL_PATH, _model_artifact["features"])
    return _model_artifact


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "MTCARS MPG API",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "predict": "POST /predict",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    try:
        artifact = load_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "status": "ready",
        "features": ",".join(artifact["features"]),
        "target": artifact["target"],
    }


@app.post("/predict")
def predict(request: PredictionRequest) -> dict[str, float]:
    try:
        artifact = load_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    model = artifact["model"]
    features = artifact["features"]
    row = pd.DataFrame(
        [[getattr(request, name) for name in features]],
        columns=features,
    )
    predicted = float(model.predict(row)[0])

    return {"predicted_mpg": round(predicted, 2)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

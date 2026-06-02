from __future__ import annotations
import os

import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel, Field
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier


app = FastAPI(title="fullstack-backend")


class PredictRequest(BaseModel):
    sepal_length: float = Field(..., gt=0)
    sepal_width: float = Field(..., gt=0)
    petal_length: float = Field(..., gt=0)
    petal_width: float = Field(..., gt=0)


iris = load_iris()
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(iris.data, iris.target)
target_names = list(iris.target_names)

CACHE: dict[tuple[float, float, float, float], str] = {}
PREDICTION_LOG: list[dict[str, object]] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/history")
def history() -> dict[str, list[dict[str, object]]]:
    return {"requests": PREDICTION_LOG}


@app.post("/predict")
def predict(request: PredictRequest) -> dict[str, object]:
    features = (
        request.sepal_length,
        request.sepal_width,
        request.petal_length,
        request.petal_width,
    )

    if features in CACHE:
        prediction = CACHE[features]
        cached = True
    else:
        predicted_class = model.predict([list(features)])[0]
        prediction = target_names[int(predicted_class)]
        CACHE[features] = prediction
        cached = False

    record = {
        "sepal_length": request.sepal_length,
        "sepal_width": request.sepal_width,
        "petal_length": request.petal_length,
        "petal_width": request.petal_width,
        "prediction": prediction,
        "cached": cached,
    }
    PREDICTION_LOG.append(record)
    return record


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="fullstack-backend")


class PredictRequest(BaseModel):
    query: str


CACHE: dict[str, str] = {}
PREDICTION_LOG: list[dict[str, str | bool]] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/history")
def history() -> dict[str, list[dict[str, str | bool]]]:
    return {"items": PREDICTION_LOG}


@app.post("/predict")
def predict(request: PredictRequest) -> dict[str, str | bool]:
    if request.query in CACHE:
        result = CACHE[request.query]
        cached = True
    else:
        result = f"prediction-for:{request.query.lower().strip()}"
        CACHE[request.query] = result
        cached = False

    record = {"query": request.query, "prediction": result, "cached": cached}
    PREDICTION_LOG.append(record)
    return record


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="basic-cicd-demo")


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/predict")
def predict(request: PredictRequest) -> dict[str, float]:
    prediction = sum(request.features) / len(request.features)
    return {"prediction": float(prediction)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent

model = joblib.load(BASE_DIR / "ikea_interest_model.pkl")

app = FastAPI(
    title="IKEA Product Interest API",
    description="API for predicting high consumer interest for furniture products.",
    version="1.0"
)


class ProductInput(BaseModel):
    category: str
    price: float
    rating: float
    name_length: int = 3
    page_text_length: int = 2000


@app.get("/")
def root():
    return {"message": "IKEA Product Interest API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(product: ProductInput):
    input_df = pd.DataFrame([
        {
            "category": product.category,
            "price": product.price,
            "rating": product.rating,
            "name_length": product.name_length,
            "page_text_length": product.page_text_length,
        }
    ])

    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    return {
        "prediction": "high_interest" if prediction == 1 else "low_interest",
        "probability_high_interest": probability,
        "interest_score": round(probability * 100)
    }

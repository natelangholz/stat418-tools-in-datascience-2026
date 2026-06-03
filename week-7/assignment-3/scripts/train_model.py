"""Train a linear regression model on mtcars.csv and save the artifact."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "mtcars.csv"
MODEL_PATH = ROOT / "models" / "model.pkl"

# Predictors: weight (wt) and horsepower (hp) predict mpg.
FEATURES = ["wt", "hp"]
TARGET = "mpg"


def train() -> None:
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df[TARGET]

    model = LinearRegression()
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": model,
        "features": FEATURES,
        "target": TARGET,
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")
    print(f"Features: {FEATURES}, target: {TARGET}")
    print(f"Coefficients: {dict(zip(FEATURES, model.coef_))}")
    print(f"Intercept: {model.intercept_:.4f}")


if __name__ == "__main__":
    train()

"""Train the player market value model and save it as model.pkl.

Run once before serving the API. Produces a bundle that main.py loads at startup.
The dataset covers 2,013 players across the top 5 European leagues, with market
values spanning EUR 50k to EUR 200M.
"""
import logging

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_PATH = "../../../../final-project-work/sungjinchoi/data/processed/model_dataset.csv"
FEATURES = ["age", "appearances", "goals", "assists", "minutes", "yellow_cards", "red_cards"]
MODEL_VERSION = "v1.0"


def load_data() -> pd.DataFrame:
    """Load the processed player dataset and drop rows missing features or target."""
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=FEATURES + ["market_value"])
    logger.info("Loaded %d players", len(df))
    return df


def train() -> None:
    """Train a RandomForest regressor on log market value and save the bundle."""
    df = load_data()
    X = df[FEATURES].values
    y = np.log(df["market_value"].values)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=300, max_depth=14, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    r2 = r2_score(y_test, pred)
    mae_eur = mean_absolute_error(np.exp(y_test), np.exp(pred))
    logger.info("Test R2 (log target): %.3f", r2)
    logger.info("Test MAE: EUR %.2fM", mae_eur / 1e6)

    bundle = {
        "model": model,
        "features": FEATURES,
        "target": "log_market_value",
        "model_version": MODEL_VERSION,
        "n_train": len(X_train),
        "metrics": {"r2": round(r2, 3), "mae_eur": round(float(mae_eur), 0)},
    }
    joblib.dump(bundle, "model.pkl", compress=3)
    logger.info("Saved model.pkl (%d features, %d training rows)", len(FEATURES), len(X_train))


if __name__ == "__main__":
    train()

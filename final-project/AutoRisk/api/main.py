"""
AutoRisk Flask API
==================
Serves the Random Forest risk classifier trained on NHTSA recall/complaint data.

Endpoints
---------
GET  /health          → {"status": "ok", "model": "random_forest", ...}
GET  /vehicles        → list of all (year, make, model) combinations in training data
POST /predict         → predict high-risk probability for a given vehicle
GET  /vehicles/stats  → full stats row for a given vehicle (year + make + model query params)

Run locally (from repo root)
-----------------------------
    pip install -r api/requirements.txt
    python main.py

Docker
------
    podman build -f api/Dockerfile -t autorisk-api .
    podman run --rm -p 8080:8080 autorisk-api
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# main.py lives at the repo root (AutoRisk/), so data is right next to it.
# In Docker: main.py is at /app/main.py, data is at /app/data/processed/.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
_DATA_DIR = _HERE / "data" / "processed"
LABELED_CSV = _DATA_DIR / "vehicle_risk_features_labeled.csv"

# ---------------------------------------------------------------------------
# Feature config  (must match src/model_baseline.py)
# ---------------------------------------------------------------------------
SAFE_FEATURES = [
    "year",
    "vehicle_age",
    "make",
    "brand_category",
    "recall_count",
    "recall_restraint_count",
    "recall_brake_count",
    "recall_electrical_count",
    "recall_engine_count",
    "recall_powertrain_count",
    "recall_fuel_count",
    "recall_steering_count",
    "recall_suspension_count",
    "recall_structure_count",
    "recall_other_count",
]
LABEL_COL = "risk_label"

# ---------------------------------------------------------------------------
# Global model + data (loaded once at startup)
# ---------------------------------------------------------------------------
MODEL: Pipeline | None = None
DF: pd.DataFrame | None = None
TEST_ACCURACY: float = 0.0
TEST_F1: float = 0.0


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    categorical = [c for c in SAFE_FEATURES if df[c].dtype == "object"]
    numeric = [c for c in SAFE_FEATURES if c not in categorical]

    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    return ColumnTransformer([
        ("num", num_pipe, numeric),
        ("cat", cat_pipe, categorical),
    ])


def train_model(df: pd.DataFrame) -> tuple[Pipeline, dict]:
    X = df[SAFE_FEATURES].copy()
    y = df[LABEL_COL].astype(int).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = Pipeline([
        ("preprocessor", build_preprocessor(df)),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "test_accuracy": float(accuracy_score(y_test, preds)),
        "test_f1": float(f1_score(y_test, preds, zero_division=0)),
    }

    log.info("Model trained. Test accuracy=%.3f  F1=%.3f",
             metrics["test_accuracy"], metrics["test_f1"])
    return model, metrics


def load_everything():
    global MODEL, DF, TEST_ACCURACY, TEST_F1

    if not LABELED_CSV.exists():
        raise FileNotFoundError(
            f"Labeled CSV not found: {LABELED_CSV}\n"
            "Run src/eda.py first to generate it."
        )

    df = pd.read_csv(LABELED_CSV)
    df = df.dropna(subset=[LABEL_COL]).copy()
    df[LABEL_COL] = df[LABEL_COL].astype(int)
    DF = df
    log.info("Loaded %d rows from %s", len(df), LABELED_CSV)

    MODEL, metrics = train_model(df)
    TEST_ACCURACY = metrics["test_accuracy"]
    TEST_F1 = metrics["test_f1"]
    log.info("Startup complete.")


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)


@app.before_request
def _ensure_loaded():
    """Lazy-load on first request (useful for testing without full startup)."""
    global MODEL, DF
    if MODEL is None:
        load_everything()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "model": "random_forest",
        "test_accuracy": round(TEST_ACCURACY, 4),
        "test_f1": round(TEST_F1, 4),
        "n_training_rows": int(len(DF)) if DF is not None else 0,
    })


@app.get("/vehicles")
def vehicles():
    """Return all unique (year, make, base_model) combos."""
    if DF is None:
        return jsonify({"error": "model not loaded"}), 503

    records = (
        DF[["year", "make", "base_model"]]
        .drop_duplicates()
        .sort_values(["year", "make", "base_model"])
        .to_dict(orient="records")
    )
    return jsonify({"count": len(records), "vehicles": records})


@app.get("/vehicles/stats")
def vehicle_stats():
    """
    Return full stats row for a vehicle.
    Query params: year (int), make (str), model (str)
    """
    if DF is None:
        return jsonify({"error": "model not loaded"}), 503

    year = request.args.get("year", type=int)
    make = request.args.get("make", "").strip().upper()
    model_name = request.args.get("model", "").strip().upper()

    if not year or not make or not model_name:
        return jsonify({"error": "year, make, and model are required"}), 400

    mask = (
        (DF["year"] == year)
        & (DF["make"].str.upper() == make)
        & (DF["base_model"].str.upper() == model_name)
    )
    rows = DF[mask]

    if rows.empty:
        return jsonify({"error": f"Vehicle not found: {year} {make} {model_name}"}), 404

    row = rows.iloc[0].replace({np.nan: None})
    return jsonify(row.to_dict())


@app.post("/predict")
def predict():
    """
    Predict high-risk probability.

    Body (JSON):
    {
        "year": 2022,
        "make": "Toyota",
        "recall_count": 3,
        "recall_restraint_count": 1,
        "recall_brake_count": 0,
        "recall_electrical_count": 0,
        "recall_engine_count": 0,
        "recall_powertrain_count": 1,
        "recall_fuel_count": 0,
        "recall_steering_count": 0,
        "recall_suspension_count": 0,
        "recall_structure_count": 0,
        "recall_other_count": 1
    }
    """
    if MODEL is None:
        return jsonify({"error": "model not loaded"}), 503

    body = request.get_json(silent=True) or {}

    year = body.get("year")
    make = body.get("make", "")

    if not year:
        return jsonify({"error": "'year' is required"}), 400

    current_year = 2026
    vehicle_age = current_year - int(year)

    brand_category = body.get("brand_category")
    if not brand_category:
        make_lower = make.lower()
        if make_lower in {"toyota", "honda", "nissan", "mazda", "subaru"}:
            brand_category = "japanese_ice"
        elif make_lower in {"hyundai", "kia"}:
            brand_category = "korean_ice"
        elif make_lower in {"ford", "chevrolet", "gmc", "ram", "jeep", "dodge"}:
            brand_category = "domestic_ice"
        else:
            brand_category = "other"

    row = {
        "year": int(year),
        "vehicle_age": vehicle_age,
        "make": str(make).title(),
        "brand_category": brand_category,
        "recall_count": int(body.get("recall_count", 0)),
        "recall_restraint_count": int(body.get("recall_restraint_count", 0)),
        "recall_brake_count": int(body.get("recall_brake_count", 0)),
        "recall_electrical_count": int(body.get("recall_electrical_count", 0)),
        "recall_engine_count": int(body.get("recall_engine_count", 0)),
        "recall_powertrain_count": int(body.get("recall_powertrain_count", 0)),
        "recall_fuel_count": int(body.get("recall_fuel_count", 0)),
        "recall_steering_count": int(body.get("recall_steering_count", 0)),
        "recall_suspension_count": int(body.get("recall_suspension_count", 0)),
        "recall_structure_count": int(body.get("recall_structure_count", 0)),
        "recall_other_count": int(body.get("recall_other_count", 0)),
    }

    X = pd.DataFrame([row])

    try:
        proba = MODEL.predict_proba(X)[0]
        high_risk_proba = float(proba[1])
        prediction = int(MODEL.predict(X)[0])
    except Exception as exc:
        log.exception("Prediction error")
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "high_risk_probability": round(high_risk_proba, 4),
        "prediction": prediction,
        "label": "high-risk" if prediction == 1 else "low-risk",
        "vehicle_age": vehicle_age,
        "source": "model",
    })


@app.get("/makes")
def makes():
    if DF is None:
        return jsonify({"error": "model not loaded"}), 503
    return jsonify({"makes": sorted(DF["make"].unique().tolist())})


@app.get("/models")
def models_for_make():
    if DF is None:
        return jsonify({"error": "model not loaded"}), 503

    make = request.args.get("make", "").strip()
    year = request.args.get("year", type=int)

    mask = DF["make"].str.lower() == make.lower()
    if year:
        mask &= DF["year"] == year

    models = sorted(DF[mask]["base_model"].unique().tolist())
    return jsonify({"models": models})


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    load_everything()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

"""Flask API: forecasts, EIA data refresh, and model training."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")
load_dotenv()

from app_lib.config import (  # noqa: E402
    FORECAST_METHODS,
    METADATA_PATH,
    RAW_GAS_CSV,
    SARIMA_MODEL_PATH,
    XGBOOST_MODEL_PATH,
)
from app_lib.features import FEATURE_COLUMNS, load_raw_prices  # noqa: E402
from app_lib.models import run_forecast  # noqa: E402
from app_lib.pipeline import (  # noqa: E402
    EIA_LINKS,
    collect_from_eia,
    train_models,
)

app = Flask(__name__)

_metadata: dict | None = None


def clear_metadata_cache() -> None:
    global _metadata
    _metadata = None


def get_metadata() -> dict:
    global _metadata
    if _metadata is None:
        path = Path(os.environ.get("METADATA_PATH", METADATA_PATH))
        _metadata = json.loads(path.read_text(encoding="utf-8"))
    return _metadata


def get_raw_path() -> Path:
    return Path(os.environ.get("RAW_GAS_CSV", RAW_GAS_CSV))


@app.get("/")
def index():
    """Browser-friendly API landing page."""
    return jsonify(
        {
            "name": "U.S. retail gasoline forecast API",
            "status": "ok",
            "endpoints": {
                "health": "GET /health",
                "metadata": "GET /metadata",
                "predict": "POST /predict with JSON {'horizon': 8, 'method': 'xgboost'}",
                "data_sources": "GET /data/sources",
                "data_history": "GET /data/history",
            },
            "example_predict": {
                "url": "/predict",
                "method": "POST",
                "json": {"horizon": 8, "method": "xgboost"},
            },
        }
    )


@app.get("/health")
def health():
    has_key = bool((os.environ.get("EIA_API_KEY") or "").strip())
    return jsonify(
        {
            "status": "ok",
            "methods": list(FORECAST_METHODS),
            "eia_api_key_configured": has_key,
        }
    )


@app.get("/data/sources")
def data_sources():
    """Clickable EIA URLs for documentation / registration."""
    return jsonify(
        {
            "eia": EIA_LINKS,
            "description": "Register for a key, then POST /pipeline/run or /data/collect to refresh gasoline_weekly.csv.",
        }
    )


@app.post("/data/collect")
def data_collect():
    """Pull latest weekly gasoline from EIA Open Data API."""
    try:
        payload = request.get_json(silent=True) or {}
        require_key = bool(payload.get("require_eia_key", True))
        result = collect_from_eia(get_raw_path(), require_key=require_key)
        clear_metadata_cache()
        return jsonify({"ok": True, **result})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/data/history")
def data_history():
    """Return the historical gasoline series used by the API."""
    try:
        raw = load_raw_prices(get_raw_path())
        rows = [
            {"period": str(row.period.date()), "price": float(row.price)}
            for row in raw.itertuples(index=False)
        ]
        return jsonify(
            {
                "ok": True,
                "last_data_period": rows[-1]["period"] if rows else None,
                "n_rows": len(rows),
                "series": rows,
            }
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.post("/models/train")
def models_train():
    """Retrain the fast deployed model on the current CSV."""
    try:
        result = train_models(get_raw_path(), include_sarima=False)
        clear_metadata_cache()
        return jsonify({"ok": True, **result})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.post("/pipeline/run")
def pipeline_run():
    """One-click: fetch from EIA (if key set) then retrain the fast deployed model."""
    try:
        payload = request.get_json(silent=True) or {}
        require_key = bool(payload.get("require_eia_key", True))
        collect_result = collect_from_eia(get_raw_path(), require_key=require_key)
        train_result = train_models(get_raw_path(), include_sarima=False)
        result = {
            "ok": True,
            "collect": collect_result,
            "train": train_result,
            "message": collect_result["message"] + " " + train_result["message"],
        }
        clear_metadata_cache()
        return jsonify(result)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/metadata")
def metadata():
    try:
        meta = get_metadata()
        raw = load_raw_prices(get_raw_path())
        return jsonify(
            {
                "last_data_period": str(raw["period"].iloc[-1].date()),
                "n_rows": int(len(raw)),
                "methods": list(FORECAST_METHODS),
                "models": meta.get("models", meta),
                "feature_columns": meta.get("feature_columns", FEATURE_COLUMNS),
                "pipeline": {
                    "collect": "POST /data/collect",
                    "train": "POST /models/train",
                    "full": "POST /pipeline/run",
                    "sources": "GET /data/sources",
                },
            }
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.post("/predict")
def predict():
    try:
        payload = request.get_json(silent=True) or {}
        horizon = int(payload.get("horizon", 4))
        method = str(payload.get("method", "xgboost")).lower().strip()
        if method not in FORECAST_METHODS:
            return jsonify({"error": f"method must be one of {list(FORECAST_METHODS)}"}), 400

        raw = load_raw_prices(get_raw_path())
        xgb_path = Path(os.environ.get("XGBOOST_MODEL_PATH", XGBOOST_MODEL_PATH))
        sarima_path = Path(os.environ.get("SARIMA_MODEL_PATH", SARIMA_MODEL_PATH))
        preds, label = run_forecast(method, raw, horizon, xgb_path, sarima_path)
        model_meta = get_metadata().get("models", {}).get(method, {})

        return jsonify(
            {
                "method": method,
                "method_label": label,
                "horizon_weeks": horizon,
                "forecasts": preds,
                "last_historical_period": str(raw["period"].iloc[-1].date()),
                "validation_mae": model_meta.get("validation_mae"),
                "validation_rmse": model_meta.get("validation_rmse"),
            }
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=True)

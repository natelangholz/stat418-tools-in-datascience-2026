"""Train and forecast with XGBoost (recursive lags) or SARIMA (statsmodels)."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from statsmodels.tsa.statespace.sarimax import SARIMAX

from app_lib.config import METADATA_PATH, SARIMA_MODEL_PATH, XGBOOST_MODEL_PATH
from app_lib.features import (
    FEATURE_COLUMNS,
    build_feature_row_from_history,
    load_raw_prices,
    modeling_frame,
    recursive_forecast,
)


def holdout_weeks(n: int) -> int:
    if n < 120:
        return max(8, n // 5)
    return 52


def train_xgboost(raw_csv: Path, model_path: Path) -> dict:
    raw = load_raw_prices(raw_csv)
    df = modeling_frame(raw)
    test_size = holdout_weeks(len(df))

    X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = df["price"].to_numpy(dtype=float)
    train_X, train_y = X[:-test_size], y[:-test_size]
    test_X, test_y = X[-test_size:], y[-test_size:]

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train_X, train_y)
    pred = model.predict(test_X)
    mae = float(np.mean(np.abs(test_y - pred)))
    rmse = float(np.sqrt(np.mean((test_y - pred) ** 2)))

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    return {
        "method": "xgboost",
        "holdout_weeks": test_size,
        "validation_mae": mae,
        "validation_rmse": rmse,
        "n_train_rows": int(len(train_X)),
        "description": "Gradient boosted trees on lag + calendar features (recursive multi-step forecast).",
    }


def _fit_sarima(train_y: np.ndarray):
    """Fit seasonal SARIMA on weekly series; fall back to non-seasonal ARIMA if needed."""
    orders = [
        ((1, 1, 1), (1, 1, 1, 52), "SARIMA(1,1,1)(1,1,1,52)"),
        ((2, 1, 2), (1, 1, 1, 52), "SARIMA(2,1,2)(1,1,1,52)"),
        ((2, 1, 2), (0, 0, 0, 0), "ARIMA(2,1,2)"),
    ]
    last_err = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for order, seasonal, label in orders:
            try:
                model = SARIMAX(
                    train_y,
                    order=order,
                    seasonal_order=seasonal,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                result = model.fit(disp=False, maxiter=200)
                if result.mle_retvals.get("converged", True) is False:
                    continue
                return result, label, order, seasonal
            except Exception as exc:  # noqa: BLE001
                last_err = exc
    raise RuntimeError(f"SARIMA/ARIMA fit failed: {last_err}")


def train_sarima(raw_csv: Path, model_path: Path) -> dict:
    raw = load_raw_prices(raw_csv)
    y = raw["price"].to_numpy(dtype=float)
    test_size = holdout_weeks(len(y))
    train_y, test_y = y[:-test_size], y[-test_size:]

    result, spec, order, seasonal = _fit_sarima(train_y)
    pred = np.asarray(result.forecast(steps=test_size), dtype=float)
    mae = float(np.mean(np.abs(test_y - pred)))
    rmse = float(np.sqrt(np.mean((test_y - pred) ** 2)))

    bundle = {
        "params": np.asarray(result.params, dtype=float),
        "order": order,
        "seasonal_order": seasonal,
        "spec": spec,
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    return {
        "method": "sarima",
        "model_spec": spec,
        "holdout_weeks": test_size,
        "validation_mae": mae,
        "validation_rmse": rmse,
        "n_train_rows": int(len(train_y)),
        "description": "Univariate SARIMA/ARIMA on weekly price (direct multi-step forecast).",
    }


def train_all(raw_csv: Path, modeling_csv: Path, metadata_path: Path) -> dict:
    raw = load_raw_prices(raw_csv)
    modeling_csv.parent.mkdir(parents=True, exist_ok=True)
    modeling_frame(raw).to_csv(modeling_csv, index=False)

    xgb_meta = train_xgboost(raw_csv, XGBOOST_MODEL_PATH)
    sarima_meta = train_sarima(raw_csv, SARIMA_MODEL_PATH)

    meta = {
        "last_data_period": raw["period"].iloc[-1].strftime("%Y-%m-%d"),
        "feature_columns": FEATURE_COLUMNS,
        "models": {
            "xgboost": xgb_meta,
            "sarima": sarima_meta,
        },
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def load_xgboost(path: Path | None = None):
    return joblib.load(path or XGBOOST_MODEL_PATH)


def load_sarima(path: Path | None = None) -> dict:
    return joblib.load(path or SARIMA_MODEL_PATH)


def forecast_xgboost(
    model: xgb.XGBRegressor,
    history_dates: pd.Series,
    history_prices: list[float],
    horizon: int,
) -> list[dict]:
    return recursive_forecast(model, history_dates, history_prices, horizon)


def forecast_sarima(bundle: dict, raw: pd.DataFrame, horizon: int) -> list[dict]:
    last_period = pd.Timestamp(raw["period"].iloc[-1])
    if "result" in bundle:
        result = bundle["result"]
    else:
        model = SARIMAX(
            raw["price"].to_numpy(dtype=float),
            order=tuple(bundle["order"]),
            seasonal_order=tuple(bundle["seasonal_order"]),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        result = model.filter(np.asarray(bundle["params"], dtype=float))
    pred = np.asarray(result.forecast(steps=horizon), dtype=float)
    out = []
    for h in range(1, horizon + 1):
        next_date = last_period + pd.DateOffset(weeks=h)
        out.append(
            {
                "period": next_date.strftime("%Y-%m-%d"),
                "forecast_price": float(pred[h - 1]),
            }
        )
    return out


def run_forecast(
    method: str,
    raw: pd.DataFrame,
    horizon: int,
    xgb_path: Path | None = None,
    sarima_path: Path | None = None,
) -> tuple[list[dict], str]:
    method = method.lower().strip()
    if method not in ("xgboost", "sarima"):
        raise ValueError("method must be 'xgboost' or 'sarima'")
    if horizon < 1 or horizon > 52:
        raise ValueError("horizon must be between 1 and 52")

    if method == "xgboost":
        model = load_xgboost(xgb_path)
        preds = forecast_xgboost(model, raw["period"], raw["price"].tolist(), horizon)
        label = "XGBoost (recursive lags)"
    else:
        bundle = load_sarima(sarima_path)
        preds = forecast_sarima(bundle, raw, horizon)
        label = bundle.get("spec", "SARIMA")
    return preds, label

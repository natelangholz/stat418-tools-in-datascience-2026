"""Feature engineering for weekly U.S. retail gasoline (tabular time series)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

LAG_WINDOWS = (1, 2, 4, 8, 52)
FEATURE_COLUMNS = [f"lag_{w}" for w in LAG_WINDOWS] + ["month", "weekofyear"]


def load_raw_prices(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["period"])
    df = df.sort_values("period").reset_index(drop=True)
    df["price"] = df["price"].astype(float)
    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for w in LAG_WINDOWS:
        out[f"lag_{w}"] = out["price"].shift(w)
    out["month"] = out["period"].dt.month.astype(int)
    out["weekofyear"] = out["period"].dt.isocalendar().week.astype(int)
    return out


def modeling_frame(raw: pd.DataFrame) -> pd.DataFrame:
    m = add_lag_features(raw)
    return m.dropna(subset=FEATURE_COLUMNS + ["price"]).reset_index(drop=True)


def build_feature_row_from_history(prices: list[float], forecast_date: pd.Timestamp) -> np.ndarray:
    """Single row matching FEATURE_COLUMNS order (recursive forecast)."""
    if len(prices) < max(LAG_WINDOWS):
        raise ValueError(f"Need at least {max(LAG_WINDOWS)} historical prices.")
    row = []
    for w in LAG_WINDOWS:
        row.append(float(prices[-w]))
    row.append(int(forecast_date.month))
    row.append(int(forecast_date.isocalendar().week))
    return np.array(row, dtype=float).reshape(1, -1)


def recursive_forecast(
    model,
    history_dates: pd.Series,
    history_prices: list[float],
    horizon: int,
) -> list[dict]:
    """Multi-step ahead by feeding each prediction back into lag features."""
    if horizon < 1 or horizon > 52:
        raise ValueError("horizon must be between 1 and 52 weeks")
    last_date = pd.Timestamp(history_dates.iloc[-1])
    prices = list(history_prices)
    out: list[dict] = []
    for h in range(1, horizon + 1):
        next_date = last_date + pd.DateOffset(weeks=h)
        X = build_feature_row_from_history(prices, next_date)
        pred = float(model.predict(X)[0])
        out.append({"period": next_date.strftime("%Y-%m-%d"), "forecast_price": pred})
        prices.append(pred)
    return out

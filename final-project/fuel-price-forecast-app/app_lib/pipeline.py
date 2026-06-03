"""EIA data refresh and model training (callable from CLI, API, or Streamlit)."""

from __future__ import annotations

import os
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

from app_lib.config import (
    DEFAULT_EIA_SERIES,
    EIA_DATA_URL,
    METADATA_PATH,
    MODELING_CSV,
    RAW_GAS_CSV,
    XGBOOST_MODEL_PATH,
)
from app_lib.features import FEATURE_COLUMNS, load_raw_prices, modeling_frame
from app_lib.models import train_all, train_xgboost

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
load_dotenv()

EIA_LINKS = {
    "portal": "https://www.eia.gov/opendata/",
    "register": "https://www.eia.gov/opendata/register.php",
    "documentation": "https://www.eia.gov/opendata/documentation.php",
    "gasoline_series_browser": "https://www.eia.gov/opendata/browser/petroleum/pri/gnd",
}


def _synthetic_weekly(n_weeks: int = 450, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n_weeks)
    base = 3.15
    seasonal = 0.12 * np.sin(2 * np.pi * t / 52.0)
    ar = np.zeros(n_weeks)
    for i in range(1, n_weeks):
        ar[i] = 0.92 * ar[i - 1] + rng.normal(0, 0.035)
    prices = np.clip(base + seasonal + ar, 1.5, 6.5)
    start = pd.Timestamp("2005-01-03")
    dates = start + pd.to_timedelta(t * 7, unit="D")
    return pd.DataFrame({"period": dates.normalize(), "price": prices.astype(float)})


def fetch_eia_weekly(api_key: str, series_id: str) -> pd.DataFrame:
    rows: list[dict] = []
    offset = 0
    length = 5000
    while True:
        params = {
            "api_key": api_key,
            "frequency": "weekly",
            "data[0]": "value",
            "facets[series][]": series_id,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": length,
        }
        r = requests.get(EIA_DATA_URL, params=params, timeout=90)
        r.raise_for_status()
        payload = r.json()
        if "error" in payload:
            err = payload["error"]
            msg = err.get("message", err) if isinstance(err, dict) else str(err)
            raise RuntimeError(msg)
        chunk = payload.get("response", {}).get("data", [])
        if not chunk:
            break
        for row in chunk:
            rows.append(
                {
                    "period": pd.to_datetime(row["period"]),
                    "price": float(row["value"]),
                }
            )
        if len(chunk) < length:
            break
        offset += length

    if not rows:
        raise RuntimeError("EIA returned no rows; check EIA_SERIES_ID and API route.")
    return (
        pd.DataFrame(rows)
        .drop_duplicates(subset=["period"])
        .sort_values("period")
        .reset_index(drop=True)
    )


def collect_from_eia(
    raw_csv: Path | None = None,
    *,
    require_key: bool = False,
) -> dict:
    """Download weekly gasoline from EIA (or synthetic if no key and require_key=False)."""
    raw_csv = raw_csv or RAW_GAS_CSV
    raw_csv.parent.mkdir(parents=True, exist_ok=True)

    api_key = (os.environ.get("EIA_API_KEY") or "").strip()
    series_id = (os.environ.get("EIA_SERIES_ID") or DEFAULT_EIA_SERIES).strip()

    if api_key:
        df = fetch_eia_weekly(api_key, series_id)
        source = "eia"
        message = f"Downloaded {len(df)} rows from EIA through {df['period'].iloc[-1].date()}."
    elif require_key:
        raise ValueError(
            "EIA_API_KEY is not set. Add it to .env (see .env.example) or register at "
            f"{EIA_LINKS['register']}"
        )
    else:
        df = _synthetic_weekly()
        source = "synthetic"
        message = "EIA_API_KEY not set — wrote synthetic demo data instead."

    df.to_csv(raw_csv, index=False)
    return {
        "source": source,
        "series_id": series_id,
        "n_rows": int(len(df)),
        "last_period": str(df["period"].iloc[-1].date()),
        "path": str(raw_csv),
        "message": message,
    }


def train_models(
    raw_csv: Path | None = None,
    modeling_csv: Path | None = None,
    metadata_path: Path | None = None,
    *,
    include_sarima: bool = True,
) -> dict:
    raw_csv = raw_csv or RAW_GAS_CSV
    modeling_csv = modeling_csv or MODELING_CSV
    metadata_path = metadata_path or METADATA_PATH
    if not raw_csv.exists():
        raise FileNotFoundError(f"Missing {raw_csv}. Run data collection first.")
    if include_sarima:
        meta = train_all(raw_csv, modeling_csv, metadata_path)
        message = "Models retrained on latest data."
    else:
        raw = load_raw_prices(raw_csv)
        modeling_csv.parent.mkdir(parents=True, exist_ok=True)
        modeling_frame(raw).to_csv(modeling_csv, index=False)
        xgb_meta = train_xgboost(raw_csv, XGBOOST_MODEL_PATH)
        previous = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        meta = {
            "last_data_period": raw["period"].iloc[-1].strftime("%Y-%m-%d"),
            "feature_columns": FEATURE_COLUMNS,
            "models": {
                "xgboost": xgb_meta,
            },
        }
        sarima_meta = previous.get("models", {}).get("sarima")
        if sarima_meta:
            meta["models"]["sarima"] = sarima_meta
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        message = "XGBoost retrained on latest data. SARIMA kept as the packaged comparison model for deployment speed."
    return {
        "message": message,
        "last_data_period": meta["last_data_period"],
        "models": meta["models"],
    }


def run_full_pipeline(
    *,
    require_eia_key: bool = True,
    raw_csv: Path | None = None,
    modeling_csv: Path | None = None,
    metadata_path: Path | None = None,
) -> dict:
    """Fetch EIA data then retrain XGBoost + SARIMA."""
    collect_result = collect_from_eia(raw_csv, require_key=require_eia_key)
    train_result = train_models(raw_csv, modeling_csv, metadata_path)
    return {
        "ok": True,
        "collect": collect_result,
        "train": train_result,
        "message": collect_result["message"] + " " + train_result["message"],
    }

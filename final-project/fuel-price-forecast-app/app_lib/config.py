"""Paths and defaults for the fuel-price app."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW_GAS_CSV = ROOT / "data" / "raw" / "gasoline_weekly.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELING_CSV = PROCESSED_DIR / "gasoline_modeling.csv"
MODELS_DIR = ROOT / "models"
XGBOOST_MODEL_PATH = MODELS_DIR / "xgboost.joblib"
SARIMA_MODEL_PATH = MODELS_DIR / "sarima.joblib"
METADATA_PATH = MODELS_DIR / "metadata.json"

# Legacy alias (older single-model builds)
MODEL_PATH = XGBOOST_MODEL_PATH

FORECAST_METHODS = ("xgboost", "sarima")

EIA_DATA_URL = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
DEFAULT_EIA_SERIES = "EMM_EPM0_PTE_NUS_DPG"

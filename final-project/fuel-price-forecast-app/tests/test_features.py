import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app_lib.features import (  # noqa: E402
    FEATURE_COLUMNS,
    build_feature_row_from_history,
    modeling_frame,
)


def test_inference_row_matches_training_row():
    rng = np.random.default_rng(0)
    prices = (3.0 + rng.normal(0, 0.1, size=120)).tolist()
    dates = pd.date_range("2020-01-06", periods=120, freq="W-MON")
    raw = pd.DataFrame({"period": dates, "price": prices})
    m = modeling_frame(raw)
    r = 80
    expected = m[FEATURE_COLUMNS].iloc[r - 52].to_numpy(dtype=float)
    hist = raw["price"].iloc[:r].tolist()
    got = build_feature_row_from_history(hist, pd.Timestamp(raw["period"].iloc[r]))
    np.testing.assert_allclose(got.ravel(), expected, rtol=1e-6)

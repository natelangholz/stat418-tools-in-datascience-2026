#!/usr/bin/env python3
"""Train XGBoost and SARIMA models."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app_lib.pipeline import train_models  # noqa: E402


def main() -> None:
    result = train_models()
    print("Training complete.")
    for name, m in result["models"].items():
        print(f"  [{name}] holdout MAE: {m['validation_mae']:.4f}  RMSE: {m['validation_rmse']:.4f}")


if __name__ == "__main__":
    main()

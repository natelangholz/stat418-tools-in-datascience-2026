#!/usr/bin/env python3
"""Download weekly U.S. retail gasoline from EIA Open Data API (v2)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app_lib.pipeline import collect_from_eia  # noqa: E402


def main() -> None:
    result = collect_from_eia(require_key=False)
    print(result["message"])
    print(f"Wrote {result['path']}")


if __name__ == "__main__":
    main()

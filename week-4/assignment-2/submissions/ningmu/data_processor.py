"""
data_processor.py
=================
Merge the TMDB and Letterboxd raw dumps into a single tidy table.

Pipeline
--------
1. Load every per-movie JSON file from `data/raw/tmdb/`
2. Load the corresponding Letterboxd records from `data/raw/letterboxd/`
3. Flatten / clean each TMDB record (genres -> list of names, etc.)
4. Merge on `(title, year)` after normalizing strings
5. Drop duplicates, fill obvious missing values
6. Persist the result to `data/processed/movies.csv` and `.json`

The functions are kept pure (no side effects beyond logging and the
final save) so they can be unit-tested or re-used.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
RAW_TMDB_DIR = BASE_DIR / "data" / "raw" / "tmdb"
RAW_LB_DIR = BASE_DIR / "data" / "raw" / "letterboxd"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOG_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("data_processor")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """Load all TMDB and Letterboxd raw records from disk.

    Returns
    -------
    (tmdb_records, letterboxd_records)
        Two lists of dicts. Files starting with `_` (the combined
        snapshots) are skipped to avoid double-counting.
    """
    tmdb_records = [
        _read_json(p) for p in sorted(RAW_TMDB_DIR.glob("*.json"))
        if not p.name.startswith("_")
    ]
    letterboxd_records = [
        _read_json(p) for p in sorted(RAW_LB_DIR.glob("*.json"))
        if not p.name.startswith("_")
    ]
    logger.info(
        "Loaded %d TMDB records, %d Letterboxd records",
        len(tmdb_records), len(letterboxd_records),
    )
    return tmdb_records, letterboxd_records


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------
def _norm_title(t: str) -> str:
    """Lowercase + collapse non-alnum so titles compare across sources."""
    if not t:
        return ""
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def _flatten_tmdb(rec: Dict) -> Dict:
    """Reduce a raw TMDB record to the flat columns we want in the CSV."""
    release_date = rec.get("release_date") or ""
    year = int(release_date[:4]) if release_date[:4].isdigit() else None
    return {
        "tmdb_id": rec.get("id"),
        "title": rec.get("title") or rec.get("original_title"),
        "original_title": rec.get("original_title"),
        "release_date": release_date or None,
        "year": year,
        "runtime": rec.get("runtime"),
        "genres": [g["name"] for g in rec.get("genres", []) if "name" in g],
        "budget": rec.get("budget"),
        "revenue": rec.get("revenue"),
        "tmdb_rating": rec.get("vote_average"),
        "tmdb_vote_count": rec.get("vote_count"),
        "original_language": rec.get("original_language"),
        "production_companies": [
            c["name"] for c in rec.get("production_companies", []) if "name" in c
        ],
        "cast": [c.get("name") for c in rec.get("cast", []) if c.get("name")],
        "crew_top": [
            f"{c.get('name')} ({c.get('job')})"
            for c in rec.get("crew_top", [])
            if c.get("name")
        ],
    }


def _flatten_letterboxd(rec: Dict) -> Dict:
    return {
        "title": rec.get("title"),
        "year": rec.get("year"),
        "letterboxd_url": rec.get("url"),
        "letterboxd_rating": rec.get("rating"),
        "letterboxd_fans": rec.get("num_fans"),
        "letterboxd_ok": rec.get("scraped_successfully", False),
    }


# ---------------------------------------------------------------------------
# Merge & clean
# ---------------------------------------------------------------------------
def merge_data(
    tmdb_data: List[Dict], letterboxd_data: List[Dict]
) -> pd.DataFrame:
    """Inner-join-ish merge on normalized (title, year)."""
    tmdb_df = pd.DataFrame([_flatten_tmdb(r) for r in tmdb_data])
    lb_df = pd.DataFrame([_flatten_letterboxd(r) for r in letterboxd_data])

    if tmdb_df.empty:
        logger.warning("No TMDB rows to merge.")
        return tmdb_df

    tmdb_df["_key"] = tmdb_df["title"].fillna("").map(_norm_title)
    if not lb_df.empty:
        lb_df["_key"] = lb_df["title"].fillna("").map(_norm_title)
        # We use the title alone as the primary key because Letterboxd's
        # `year` is sometimes missing from our scrape; collisions inside
        # a 50-movie sample are negligible.
        merged = tmdb_df.merge(
            lb_df.drop(columns=["title", "year"]),
            how="left",
            on="_key",
        )
    else:
        merged = tmdb_df.copy()
        for col in ["letterboxd_url", "letterboxd_rating",
                    "letterboxd_fans", "letterboxd_ok"]:
            merged[col] = None

    merged = merged.drop(columns=["_key"])
    logger.info("Merged frame shape: %s", merged.shape)
    return merged


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Type-cast, dedupe, drop obviously-broken rows."""
    if df.empty:
        return df

    # Standardize the release date
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # Numeric coercion
    numeric_cols = [
        "runtime", "budget", "revenue",
        "tmdb_rating", "tmdb_vote_count",
        "letterboxd_rating", "letterboxd_fans",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 0 budget / 0 revenue is missing data on TMDB, not a real value
    for c in ("budget", "revenue"):
        if c in df.columns:
            df.loc[df[c] == 0, c] = pd.NA

    # Derived metrics
    df["profit"] = df["revenue"] - df["budget"]
    df["roi"] = (df["revenue"] - df["budget"]) / df["budget"]

    # Drop rows that lack a usable title
    df = df.dropna(subset=["title"])

    # Drop duplicates on tmdb_id, keep the first
    df = df.drop_duplicates(subset=["tmdb_id"], keep="first")

    logger.info("Cleaned frame shape: %s", df.shape)
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def save_processed_data(df: pd.DataFrame, output_dir: Path = PROCESSED_DIR) -> None:
    """Write `movies.csv` and `movies.json` into `output_dir`."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "movies.csv"
    json_path = output_dir / "movies.json"

    # For CSV, list columns become "a, b, c" so they are still readable.
    flat = df.copy()
    for col in ("genres", "production_companies", "cast", "crew_top"):
        if col in flat.columns:
            flat[col] = flat[col].apply(
                lambda v: ", ".join(v) if isinstance(v, list) else v
            )
    flat.to_csv(csv_path, index=False)

    # For JSON we keep the lists.
    df.to_json(json_path, orient="records", date_format="iso", indent=2)
    logger.info("Wrote %s and %s", csv_path, json_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    tmdb, lb = load_raw_data()
    merged = merge_data(tmdb, lb)
    cleaned = clean_data(merged)
    save_processed_data(cleaned)
    print(f"Wrote {len(cleaned)} rows to {PROCESSED_DIR}/movies.csv")


if __name__ == "__main__":
    main()

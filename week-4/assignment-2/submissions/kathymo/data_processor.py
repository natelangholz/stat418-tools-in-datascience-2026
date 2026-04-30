"""
data_processor.py
-----------------
Loads raw TMDB and Letterboxd data, saves processed output as CSV and JSON.

Data sources (read-only):
  - data/raw/tmdb/all_movies.json          — produced by api_collector.py
  - data/raw/letterboxd/letterboxd_movies.json — produced by web_scraper.py
"""

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Paths — same BASE_DIR pattern as api_collector.py and web_scraper.py
# ---------------------------------------------------------------------------

BASE_DIR       = Path(__file__).resolve().parent

LOG_DIR        = BASE_DIR / "logs"
DATA_DIR       = BASE_DIR / "data"
TMDB_DIR       = DATA_DIR / "raw" / "tmdb"
LETTERBOXD_DIR = DATA_DIR / "raw" / "letterboxd"
PROCESSED_DIR  = DATA_DIR / "processed"

LOG_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename=str(LOG_DIR / "data_processor.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_COLS = ["tmdb_id", "title"]

NUMERIC_RANGES: Dict[str, Tuple[float, float]] = {
    "tmdb_rating":      (0.0, 10.0),
    "letterboxd_rating": (0.0, 5.0),   # Letterboxd is out of 5
    "num_fans":         (0.0, float("inf")),
    "runtime":          (1.0, 600.0),
    "tmdb_vote_count":  (0.0, float("inf")),
    "budget":           (0.0, float("inf")),
    "revenue":          (0.0, float("inf")),
}


# ---------------------------------------------------------------------------
# 1. load_raw_data
# ---------------------------------------------------------------------------

def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """
    Load raw JSON data from both sources into lists of dicts.

    Reads:
      - data/raw/tmdb/all_movies.json               (from api_collector.py)
      - data/raw/letterboxd/letterboxd_movies.json  (from web_scraper.py)

    Falls back to reading individual per-movie JSON files if the combined
    file is missing for either source.

    Returns:
        Tuple of (tmdb_records, letterboxd_records). Either list may be
        empty if the source files are not found, but an error is logged.
    """
    tmdb_records        = _load_tmdb()
    letterboxd_records  = _load_letterboxd()
    logger.info(
        "Loaded %d TMDB records and %d Letterboxd records.",
        len(tmdb_records), len(letterboxd_records),
    )
    return tmdb_records, letterboxd_records


def _load_tmdb() -> List[Dict]:
    """Load TMDB records from all_movies.json or individual files."""
    combined = TMDB_DIR / "all_movies.json"
    if combined.exists():
        try:
            with combined.open(encoding="utf-8") as fh:
                data = json.load(fh)
            logger.info("Loaded %d TMDB records from %s", len(data), combined)
            return data
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read %s: %s — trying individual files.", combined, exc)

    records: List[Dict] = []
    for path in sorted(TMDB_DIR.glob("[0-9]*.json")):
        try:
            with path.open(encoding="utf-8") as fh:
                records.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            continue
    if records:
        logger.info("Loaded %d TMDB records from individual files.", len(records))
    else:
        logger.error("No TMDB data found in %s. Run api_collector.py first.", TMDB_DIR)
    return records


def _load_letterboxd() -> List[Dict]:
    """
    Load Letterboxd records from the combined JSON produced by web_scraper.py.

    Tries letterboxd_movies.json first, then falls back to individual
    per-slug JSON files written by scrape_movie_page().
    """
    # Try the combined master file written by web_scraper.py __main__
    for candidate in ["letterboxd_movies.json", "letterboxd_movie_data.json"]:
        combined = LETTERBOXD_DIR / candidate
        if combined.exists():
            try:
                with combined.open(encoding="utf-8") as fh:
                    data = json.load(fh)
                logger.info("Loaded %d Letterboxd records from %s", len(data), combined)
                return data
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Could not read %s: %s — trying individual files.", combined, exc)

    # Fall back to individual slug files
    records: List[Dict] = []
    for path in sorted(LETTERBOXD_DIR.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as fh:
                records.append(json.load(fh))
        except (json.JSONDecodeError, OSError):
            continue
    if records:
        logger.info("Loaded %d Letterboxd records from individual files.", len(records))
    else:
        logger.warning(
            "No Letterboxd data found in %s. Run web_scraper.py first. "
            "Proceeding with TMDB data only.",
            LETTERBOXD_DIR,
        )
    return records


# ---------------------------------------------------------------------------
# 2. merge_data
# ---------------------------------------------------------------------------

def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    """
    Merge TMDB and Letterboxd records into a single DataFrame on tmdb_id.

    TMDB records are flattened first (nested lists like genres and top_5_cast
    are converted to pipe-separated strings). The merge is a LEFT join so
    every TMDB movie is kept even if the Letterboxd scrape failed or returned
    no data.

    Letterboxd records that failed scraping (scraped_successfully=False) are
    excluded from the join so they don't overwrite good data with NaNs.

    Args:
        tmdb_data:        List of movie dicts from api_collector.py.
        letterboxd_data:  List of scrape-result dicts from web_scraper.py.

    Returns:
        Merged DataFrame. Letterboxd columns (letterboxd_rating, num_fans,
        letterboxd_url) will be NaN for any movie whose scrape failed.
    """
    if not tmdb_data:
        logger.error("tmdb_data is empty — cannot build DataFrame.")
        return pd.DataFrame()

    # --- Flatten TMDB records ---
    tmdb_rows: List[Dict] = []
    for movie in tmdb_data:
        genres = movie.get("genres", [])
        genres_str = "|".join(genres) if isinstance(genres, list) else str(genres or "")

        companies = movie.get("production_companies", [])
        companies_str = "|".join(companies) if isinstance(companies, list) else str(companies or "")

        cast = movie.get("top_5_cast", [])
        if isinstance(cast, list):
            cast_str = "|".join(
                c.get("name", "") if isinstance(c, dict) else str(c)
                for c in cast
            )
        else:
            cast_str = str(cast or "")

        tmdb_rows.append({
            "tmdb_id":              movie.get("tmdb_id"),
            "imdb_id":              movie.get("imdb_id"),
            "title":                movie.get("title"),
            "original_title":       movie.get("original_title"),
            "original_language":    movie.get("original_language"),
            "release_date":         movie.get("release_date"),
            "runtime":              movie.get("runtime"),
            "status":               movie.get("status"),
            "overview":             movie.get("overview"),
            "genres":               genres_str,
            "tmdb_rating":          movie.get("tmdb_rating"),
            "tmdb_vote_count":      movie.get("tmdb_vote_count"),
            "tmdb_popularity":      movie.get("tmdb_popularity"),
            "budget":               movie.get("budget"),
            "revenue":              movie.get("revenue"),
            "director":             movie.get("director"),
            "top_5_cast":           cast_str,
            "production_companies": companies_str,
        })

    tmdb_df = pd.DataFrame(tmdb_rows)
    logger.info("TMDB DataFrame: %d rows × %d columns", *tmdb_df.shape)

    # --- Flatten Letterboxd records (keep only successful scrapes) ---
    if letterboxd_data:
        lb_rows: List[Dict] = []
        for rec in letterboxd_data:
            if not rec.get("scraped_successfully", False):
                logger.debug("Skipping failed Letterboxd record: %s", rec.get("title"))
                continue
            lb_rows.append({
                "tmdb_id":           rec.get("tmdb_id"),
                "letterboxd_rating": rec.get("rating"),   # float out of 5
                "num_fans":          rec.get("num_fans"),  # int
                "letterboxd_url":    rec.get("url"),
            })
        lb_df = pd.DataFrame(lb_rows) if lb_rows else pd.DataFrame(
            columns=["tmdb_id", "letterboxd_rating", "num_fans", "letterboxd_url"]
        )
        logger.info("Letterboxd DataFrame: %d rows × %d columns", *lb_df.shape)
    else:
        lb_df = pd.DataFrame(
            columns=["tmdb_id", "letterboxd_rating", "num_fans", "letterboxd_url"]
        )
        logger.warning("No Letterboxd data — merging TMDB only.")

    # --- Left join on tmdb_id ---
    if not lb_df.empty and "tmdb_id" in lb_df.columns:
        # Ensure types match for the join
        tmdb_df["tmdb_id"] = pd.to_numeric(tmdb_df["tmdb_id"], errors="coerce")
        lb_df["tmdb_id"]   = pd.to_numeric(lb_df["tmdb_id"],   errors="coerce")
        merged = tmdb_df.merge(lb_df, on="tmdb_id", how="left")
    else:
        merged = tmdb_df.copy()
        for col in ["letterboxd_rating", "num_fans", "letterboxd_url"]:
            merged[col] = pd.NA

    matched = merged["letterboxd_rating"].notna().sum()
    logger.info(
        "Merged DataFrame: %d rows × %d columns (%d/%d matched on tmdb_id).",
        merged.shape[0], merged.shape[1], matched, len(merged),
    )
    return merged


# ---------------------------------------------------------------------------
# 3. clean_data
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the merged DataFrame.

    Steps performed:
      1. Drop rows missing all required identifiers (tmdb_id, title)
      2. Remove exact duplicates on tmdb_id
      3. Standardise release_date to datetime; extract release_year
      4. Coerce all numeric columns to float/int
      5. Replace out-of-range values with NaN
      6. Replace 0 budget/revenue with NaN (TMDB stores 0 for "unknown")
      7. Derive profit and ROI where budget and revenue are both known
      8. Standardise string columns (strip whitespace, empty string → NaN)
      9. Log a missing-value summary

    Args:
        df: Merged DataFrame from merge_data().

    Returns:
        Cleaned DataFrame ready for analysis.
    """
    if df.empty:
        logger.warning("clean_data received an empty DataFrame — returning as-is.")
        return df

    original_len = len(df)

    # 1. Drop rows missing required identifiers
    df = df.dropna(subset=REQUIRED_COLS)
    if len(df) < original_len:
        logger.info(
            "Dropped %d rows missing required columns (%s).",
            original_len - len(df), REQUIRED_COLS,
        )

    # 2. Remove duplicates on tmdb_id (keep first occurrence)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["tmdb_id"], keep="first")
    dupes_removed = before_dedup - len(df)
    if dupes_removed:
        logger.info("Removed %d duplicate tmdb_id rows.", dupes_removed)

    # 3. Standardise dates
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year.astype("Int64")

    # 4. Coerce numeric columns
    for col in NUMERIC_RANGES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Replace out-of-range values with NaN
    for col, (lo, hi) in NUMERIC_RANGES.items():
        if col in df.columns and hi != float("inf"):
            bad_mask = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
            if bad_mask.any():
                logger.warning(
                    "Setting %d out-of-range values to NaN in '%s'.",
                    bad_mask.sum(), col,
                )
                df.loc[bad_mask, col] = pd.NA

    # 6. Replace 0 budget/revenue with NaN (TMDB uses 0 for "unknown")
    for col in ["budget", "revenue"]:
        if col in df.columns:
            zeros = (df[col] == 0).sum()
            if zeros:
                df[col] = df[col].replace(0, pd.NA)
                logger.info("Replaced %d zero values with NaN in '%s'.", zeros, col)

    # 7. Derive profit and ROI
    if "budget" in df.columns and "revenue" in df.columns:
        both_known = df["budget"].notna() & df["revenue"].notna()
        df["profit"] = pd.NA
        df["roi"]    = pd.NA
        df.loc[both_known, "profit"] = (
            df.loc[both_known, "revenue"] - df.loc[both_known, "budget"]
        )
        nonzero_budget = both_known & (df["budget"] != 0)
        df.loc[nonzero_budget, "roi"] = (
            df.loc[nonzero_budget, "profit"] / df.loc[nonzero_budget, "budget"]
        ).round(4)
        logger.info("Derived profit/ROI for %d movies.", both_known.sum())

    # 8. Standardise string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        try:
            df[col] = df[col].astype(str).where(df[col].notna(), other=pd.NA)
            df[col] = df[col].str.strip()
            df[col] = df[col].replace("", pd.NA).replace("None", pd.NA).replace("nan", pd.NA)
        except Exception:
            pass

    # 9. Log missing-value summary
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        pct = (missing / len(df) * 100).round(1)
        summary = "\n".join(
            f"    {col}: {cnt} missing ({pct[col]}%)"
            for col, cnt in missing.items()
        )
        logger.info("Missing value summary after cleaning:\n%s", summary)

    logger.info("Cleaning complete: %d rows × %d columns.", *df.shape)
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. save_processed_data
# ---------------------------------------------------------------------------

def save_processed_data(df: pd.DataFrame, output_dir: str) -> None:
    """
    Save the processed DataFrame as both CSV and JSON.

    Files written:
      <output_dir>/movies.csv   — standard CSV, index excluded
      <output_dir>/movies.json  — records-oriented JSON

    Args:
        df:         Cleaned DataFrame from clean_data().
        output_dir: Directory path to write output files (created if absent).
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    csv_path  = out / "movies.csv"
    json_path = out / "movies.json"

    # --- CSV ---
    df.to_csv(csv_path, index=False)
    logger.info("Saved CSV  → %s  (%d rows, %d columns)", csv_path, *df.shape)

    # --- JSON ---
    df_for_json = df.copy()

    for col in df_for_json.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        df_for_json[col] = df_for_json[col].dt.strftime("%Y-%m-%d")

    raw_records = df_for_json.to_dict(orient="records")
    clean_records = []
    for row in raw_records:
        clean_row = {}
        for k, v in row.items():
            if v is pd.NA:
                clean_row[k] = None
            elif isinstance(v, float) and math.isnan(v):
                clean_row[k] = None
            elif hasattr(v, "__class__") and type(v).__name__ in ("NAType", "NaTType"):
                clean_row[k] = None
            else:
                clean_row[k] = v
        clean_records.append(clean_row)

    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(clean_records, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Saved JSON → %s  (%d records)", json_path, len(clean_records))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full processing pipeline from the command line."""
    print("Loading raw data...")
    tmdb_data, letterboxd_data = load_raw_data()

    if not tmdb_data:
        print(
            "\n  No TMDB data found.\n"
            f"    Expected: {TMDB_DIR}/all_movies.json\n"
            "    Run api_collector.py first."
        )
        return

    print(f"  TMDB records        : {len(tmdb_data)}")
    print(f"  Letterboxd records  : {len(letterboxd_data)}")

    print("\nMerging data on tmdb_id...")
    merged = merge_data(tmdb_data, letterboxd_data)
    print(f"  Merged shape : {merged.shape[0]} rows × {merged.shape[1]} columns")

    print("\nCleaning data...")
    cleaned = clean_data(merged)
    print(f"  Cleaned shape: {cleaned.shape[0]} rows × {cleaned.shape[1]} columns")

    print(f"\nSaving processed data to {PROCESSED_DIR}/")
    save_processed_data(cleaned, str(PROCESSED_DIR))

    print(f"\n  movies.csv  → {PROCESSED_DIR}/movies.csv")
    print(f"  movies.json → {PROCESSED_DIR}/movies.json")
    print(f"  Log         → {LOG_DIR}/data_processor.log")

    # Quick preview
    preview_cols = [c for c in
        ["title", "release_year", "tmdb_rating", "letterboxd_rating", "num_fans", "genres"]
        if c in cleaned.columns
    ]
    print("\nSample (first 5 rows):")
    print(cleaned[preview_cols].head().to_string(index=False))


if __name__ == "__main__":
    main()
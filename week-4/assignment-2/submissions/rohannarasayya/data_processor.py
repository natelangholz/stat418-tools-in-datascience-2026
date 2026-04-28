"""
data_processor.py
-----------------
Merges and cleans the TMDB and Letterboxd raw datasets, then saves the
result to data/processed/.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "data_processor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("data_processor")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TMDB_PATH = Path("data/raw/tmdb/all_movies.json")
LETTERBOXD_PATH = Path("data/raw/letterboxd/all_letterboxd.json")
OUTPUT_DIR = Path("data/processed")


# ---------------------------------------------------------------------------
# Required functions
# ---------------------------------------------------------------------------


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """
    Load the raw TMDB and Letterboxd JSON files from disk.

    Returns
    -------
    tuple of (list, list)
        (tmdb_data, letterboxd_data) — each is a list of dicts.

    Raises
    ------
    FileNotFoundError
        If either source file does not exist.
    """
    try:
        with open(TMDB_PATH, encoding="utf-8") as f:
            tmdb_data: List[Dict] = json.load(f)
        logger.info("Loaded %d TMDB records from %s", len(tmdb_data), TMDB_PATH)
    except OSError as exc:
        logger.error("Cannot load TMDB data: %s", exc)
        raise

    try:
        with open(LETTERBOXD_PATH, encoding="utf-8") as f:
            letterboxd_data: List[Dict] = json.load(f)
        logger.info(
            "Loaded %d Letterboxd records from %s", len(letterboxd_data), LETTERBOXD_PATH
        )
    except OSError as exc:
        logger.error("Cannot load Letterboxd data: %s", exc)
        raise

    return tmdb_data, letterboxd_data


def merge_data(
    tmdb_data: List[Dict], letterboxd_data: List[Dict]
) -> pd.DataFrame:
    """
    Merge TMDB and Letterboxd datasets on normalised title + release year.

    Uses a left join so all TMDB records are preserved even when there is
    no matching Letterboxd entry (e.g. slug mismatch or scraping failure).
    Both sides are normalised (lowercased, stripped) before joining to
    reduce sensitivity to minor title differences.

    Parameters
    ----------
    tmdb_data : list of dict
        Records from the TMDB API collector.
    letterboxd_data : list of dict
        Records from the Letterboxd scraper.

    Returns
    -------
    pd.DataFrame
        Merged dataframe with TMDB columns on the left and Letterboxd
        columns (lb_rating, fan_count) on the right.
    """
    tmdb_df = pd.json_normalize(tmdb_data)

    # Normalise TMDB side for the join
    tmdb_df["_norm_title"] = tmdb_df["title"].str.lower().str.strip()
    tmdb_df["release_year"] = (
        pd.to_datetime(tmdb_df["release_date"], errors="coerce")
        .dt.year
        .astype("Int64")
    )

    # Build a clean Letterboxd dataframe (rows with 'error' get NaN ratings)
    lb_clean: List[Dict] = []
    for record in letterboxd_data:
        has_error = "error" in record
        lb_clean.append({
            "title": record.get("title"),
            "year": record.get("year"),
            "lb_rating": None if has_error else record.get("lb_rating"),
            "fan_count": None if has_error else record.get("fan_count"),
        })
    lb_df = pd.DataFrame(lb_clean)
    lb_df["_norm_title"] = lb_df["title"].str.lower().str.strip()
    lb_df["release_year"] = pd.to_numeric(lb_df["year"], errors="coerce").astype("Int64")

    merged = pd.merge(
        tmdb_df,
        lb_df[["_norm_title", "release_year", "lb_rating", "fan_count"]],
        on=["_norm_title", "release_year"],
        how="left",
    )
    merged.drop(columns=["_norm_title"], inplace=True)

    logger.info(
        "Merged dataframe shape: %s (%d TMDB, %d Letterboxd input records)",
        merged.shape,
        len(tmdb_data),
        len(letterboxd_data),
    )
    return merged


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardise the merged dataframe.

    Operations performed:
    - Convert 'release_date' to datetime.
    - Replace budget/revenue values of 0 or None with NaN.
    - Coerce ratings to float.
    - Extract genre names from list-of-dicts to list-of-strings.
    - Drop exact duplicate rows.

    Parameters
    ----------
    df : pd.DataFrame
        Raw merged dataframe from merge_data().

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe.
    """
    df = df.copy()

    # --- Dates ---
    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # --- Budget / Revenue ---
    for col in ("budget", "revenue"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].replace(0, np.nan)

    # --- Ratings ---
    for col in ("vote_average", "lb_rating"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ("vote_count", "fan_count", "runtime"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Genres: list-of-dicts → list-of-strings ---
    if "genres" in df.columns:
        def extract_genre_names(val):
            """Convert TMDB genre list-of-dicts to list-of-name-strings."""
            if isinstance(val, list):
                return [g["name"] for g in val if isinstance(g, dict) and "name" in g]
            return []

        df["genres"] = df["genres"].apply(extract_genre_names)

    # --- Drop exact duplicates ---
    # Use tmdb_id as the dedup key because list-type columns (genres, cast, crew)
    # are not hashable and prevent a full row comparison.
    before = len(df)
    if "tmdb_id" in df.columns:
        df = df.drop_duplicates(subset=["tmdb_id"])
    else:
        # Fallback: deduplicate on all non-list columns
        hashable_cols = [
            c for c in df.columns
            if not df[c].apply(lambda x: isinstance(x, list)).any()
        ]
        df = df.drop_duplicates(subset=hashable_cols)
    dropped = before - len(df)
    if dropped:
        logger.info("Dropped %d exact duplicate rows", dropped)

    logger.info("Cleaned dataframe: %d rows, %d columns", *df.shape)
    return df


def save_processed_data(df: pd.DataFrame, output_dir: str) -> None:
    """
    Save the processed dataframe to CSV and JSON in *output_dir*.

    Files written:
    - {output_dir}/movies.csv
    - {output_dir}/movies.json

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned, merged dataframe.
    output_dir : str
        Directory path (will be created if it does not exist).
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # --- CSV ---
    csv_path = out / "movies.csv"
    try:
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info("Saved CSV to %s (%d rows)", csv_path, len(df))
    except OSError as exc:
        logger.error("Failed to write CSV: %s", exc)

    # --- JSON ---
    json_path = out / "movies.json"
    try:
        # Convert datetime to ISO string for JSON serialisation
        df_json = df.copy()
        if "release_date" in df_json.columns:
            df_json["release_date"] = df_json["release_date"].astype(str)
        records = df_json.where(pd.notna(df_json), other=None).to_dict(orient="records")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        logger.info("Saved JSON to %s (%d records)", json_path, len(records))
    except OSError as exc:
        logger.error("Failed to write JSON: %s", exc)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tmdb_data, letterboxd_data = load_raw_data()
    merged = merge_data(tmdb_data, letterboxd_data)
    cleaned = clean_data(merged)
    save_processed_data(cleaned, str(OUTPUT_DIR))
    print(f"Processed {len(cleaned)} movies -> {OUTPUT_DIR}/")

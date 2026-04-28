"""Load, merge, clean, and save TMDB + Letterboxd movie data."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

TMDB_DIR = Path("data/raw/tmdb")
LETTERBOXD_DIR = Path("data/raw/letterboxd")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _load_json_file(path: Path) -> List[Dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def _load_individual_files(directory: Path, glob: str) -> List[Dict]:
    records: List[Dict] = []
    for path in sorted(directory.glob(glob)):
        try:
            records.extend(_load_json_file(path))
        except Exception as exc:
            logger.warning(f"Skipping {path}: {exc}")
    return records


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """Load raw data from TMDB and Letterboxd sources.

    Prefers the combined all_*.json file; falls back to individual files.

    Returns:
        (tmdb_records, letterboxd_records)
    """
    tmdb_combined = TMDB_DIR / "all_movies.json"
    if tmdb_combined.exists():
        tmdb_data = _load_json_file(tmdb_combined)
        logger.info(f"Loaded {len(tmdb_data)} TMDB records from {tmdb_combined}")
    else:
        tmdb_data = _load_individual_files(TMDB_DIR, "movie_*.json")
        logger.info(f"Loaded {len(tmdb_data)} TMDB records from individual files")

    lb_combined = LETTERBOXD_DIR / "all_letterboxd.json"
    if lb_combined.exists():
        lb_data = _load_json_file(lb_combined)
        logger.info(f"Loaded {len(lb_data)} Letterboxd records from {lb_combined}")
    else:
        lb_data = _load_individual_files(LETTERBOXD_DIR, "*.json")
        logger.info(f"Loaded {len(lb_data)} Letterboxd records from individual files")

    return tmdb_data, lb_data


# ---------------------------------------------------------------------------
# Merging
# ---------------------------------------------------------------------------

def _normalize_title(title: Optional[str]) -> str:
    """Lowercase, strip, collapse whitespace for title matching."""
    if not title:
        return ""
    return re.sub(r"\s+", " ", title.lower().strip())


def _extract_year(release_date: Optional[str]) -> Optional[int]:
    """Parse TMDB 'YYYY-MM-DD' release_date to an integer year."""
    if not release_date or len(str(release_date)) < 4:
        return None
    try:
        return int(str(release_date)[:4])
    except ValueError:
        return None


def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    """Left-join TMDB records onto Letterboxd records on (title, year).

    Uses a left join so every TMDB record is kept even without a Letterboxd
    match. Letterboxd-only columns are NaN for unmatched rows.

    Args:
        tmdb_data: Records from api_collector.collect_all_data().
        letterboxd_data: Records from web_scraper.scrape_multiple_movies().

    Returns:
        Merged DataFrame.
    """
    df_tmdb = pd.DataFrame(tmdb_data)
    df_lb = pd.DataFrame(letterboxd_data)

    if df_tmdb.empty:
        logger.warning("TMDB data is empty — returning empty DataFrame")
        return pd.DataFrame()

    # TMDB has release_date, not year — derive the join key
    df_tmdb["_year"] = df_tmdb["release_date"].apply(_extract_year)
    df_tmdb["_join_title"] = df_tmdb["title"].apply(_normalize_title)

    if df_lb.empty:
        logger.warning("Letterboxd data is empty — no Letterboxd columns will be added")
        df_tmdb.drop(columns=["_year", "_join_title"], inplace=True)
        return df_tmdb

    # Exclude failed scrapes from the join
    if "error" in df_lb.columns:
        df_lb = df_lb[df_lb["error"].isna()].copy()

    df_lb["_year"] = pd.to_numeric(df_lb.get("year", pd.Series(dtype=float)), errors="coerce")
    df_lb["_join_title"] = df_lb["title"].apply(_normalize_title)

    # Select and rename Letterboxd columns to keep
    lb_cols = {
        "letterboxd_rating": "letterboxd_rating",
        "letterboxd_rating_count": "letterboxd_rating_count",
        "letterboxd_fans": "letterboxd_fans",
        "url": "letterboxd_url",
        "slug": "letterboxd_slug",
        "scraped_at": "scraped_at_lb",
    }
    available = {k: v for k, v in lb_cols.items() if k in df_lb.columns}
    df_lb = df_lb.rename(columns=available)
    keep = ["_join_title", "_year"] + [v for v in available.values()]
    df_lb = df_lb[[c for c in keep if c in df_lb.columns]]

    merged = df_tmdb.merge(df_lb, on=["_join_title", "_year"], how="left")
    merged.drop(columns=["_join_title", "_year"], inplace=True)

    matched = merged["letterboxd_rating"].notna().sum() if "letterboxd_rating" in merged.columns else 0
    logger.info(
        f"Merged: {len(merged)} records total, "
        f"{matched} matched to Letterboxd, "
        f"{len(merged) - matched} TMDB-only"
    )
    return merged


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the merged DataFrame.

    - Parses release_date; derives year column.
    - Casts numeric columns; converts TMDB sentinel 0 → NaN for budget/revenue.
    - Scales Letterboxd rating (0.5–5.0) to 0–10 into column 'rating_lb'.
    - Adds flat string versions of list columns for CSV compatibility.
    - Drops duplicate TMDB IDs (keeps first).
    - Drops rows missing title.

    Args:
        df: Merged DataFrame from merge_data().

    Returns:
        Cleaned DataFrame.
    """
    if df.empty:
        return df

    df = df.copy()

    # --- Dates and year ---
    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df["year"] = df["release_date"].dt.year.astype("Int64")

    # --- Numeric casting ---
    int_cols = ["runtime", "vote_count", "budget", "revenue",
                "letterboxd_rating_count", "letterboxd_fans"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    float_cols = ["vote_average", "letterboxd_rating"]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # TMDB encodes "unknown" budget/revenue as 0 — replace with NaN
    for col in ("budget", "revenue"):
        if col in df.columns:
            df[col] = df[col].where(df[col] != 0, other=pd.NA)

    # --- Scale Letterboxd rating (0.5–5) → rating_lb (0–10) ---
    if "letterboxd_rating" in df.columns:
        df["rating_lb"] = (df["letterboxd_rating"] * 2).round(2)
        df.drop(columns=["letterboxd_rating"], inplace=True)

    # --- Validate rating ranges ---
    for col in ("vote_average", "rating_lb"):
        if col in df.columns:
            out = df[col].notna() & ~df[col].between(0, 10)
            if out.any():
                logger.warning(f"Clamping {out.sum()} out-of-range values in '{col}'")
                df.loc[out, col] = df.loc[out, col].clip(0, 10)

    # --- Drop rows missing essential identity ---
    before = len(df)
    df = df.dropna(subset=["title"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with missing title")

    # --- Deduplicate on TMDB id ---
    if "id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["id"], keep="first")
        removed = before - len(df)
        if removed:
            logger.info(f"Removed {removed} duplicate TMDB records")

    # --- Flatten list columns for CSV export (keep originals for JSON) ---
    def list_to_str(v: object) -> str:
        if isinstance(v, list):
            # Handle list-of-dicts (cast/crew) and list-of-strings (genres)
            parts = []
            for item in v:
                if isinstance(item, dict):
                    parts.append(item.get("name", ""))
                else:
                    parts.append(str(item))
            return ", ".join(p for p in parts if p)
        return str(v) if pd.notna(v) else ""

    for col in ("genres", "production_companies", "cast", "crew"):
        if col in df.columns:
            df[f"{col}_str"] = df[col].apply(list_to_str)

    # --- Sort by TMDB rating descending for readable output ---
    if "vote_average" in df.columns:
        df = df.sort_values("vote_average", ascending=False).reset_index(drop=True)

    lb_count = df["rating_lb"].notna().sum() if "rating_lb" in df.columns else 0
    logger.info(
        f"Clean complete: {len(df)} rows × {len(df.columns)} columns; "
        f"{lb_count} rows have Letterboxd ratings"
    )
    return df


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

def save_processed_data(df: pd.DataFrame, output_dir: str = "data/processed") -> None:
    """Save the processed DataFrame as JSON and CSV.

    JSON keeps list columns intact (required by analyze_data.genre_analysis).
    CSV uses flattened string versions of list columns.

    Files written:
        movies_processed.json          — stable name for analysis scripts
        movies_processed_YYYYMMDD.json — timestamped snapshot
        movies_processed.csv

    Args:
        df: Cleaned DataFrame.
        output_dir: Destination directory.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    date_suffix = datetime.now().strftime("%Y%m%d")
    str_cols = [c for c in df.columns if c.endswith("_str")]

    # --- JSON: drop *_str columns, keep raw lists ---
    df_json = df.drop(columns=str_cols)
    records = json.loads(
        df_json.to_json(orient="records", date_format="iso", default_handler=str)
    )
    for name in (f"movies_processed_{date_suffix}.json", "movies_processed.json"):
        path = out / name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        logger.info(f"Saved JSON → {path}")

    # --- CSV: drop raw list columns, keep *_str versions ---
    list_cols = [c for c in df.columns if c in ("genres", "production_companies", "cast", "crew")]
    df_csv = df.drop(columns=list_cols).copy()
    # Serialise any remaining non-scalar values
    for col in df_csv.select_dtypes(include="object").columns:
        df_csv[col] = df_csv[col].apply(
            lambda v: json.dumps(v) if isinstance(v, (list, dict)) else v
        )
    csv_path = out / "movies_processed.csv"
    df_csv.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV  → {csv_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_pipeline() -> pd.DataFrame:
    """Run the full load → merge → clean → save pipeline."""
    logger.info("Starting data processing pipeline")
    tmdb_data, lb_data = load_raw_data()

    if not tmdb_data:
        logger.error("No TMDB data found. Run api_collector.py first.")
        return pd.DataFrame()

    merged = merge_data(tmdb_data, lb_data)
    cleaned = clean_data(merged)
    save_processed_data(cleaned)

    logger.info(f"Pipeline complete: {len(cleaned)} movies processed")
    return cleaned


if __name__ == "__main__":
    df = run_pipeline()
    if not df.empty:
        print(f"\nProcessed {len(df)} movies")
        display_cols = ["title", "year", "vote_average", "rating_lb",
                        "letterboxd_fans", "genres_str"]
        display_cols = [c for c in display_cols if c in df.columns]
        print(df[display_cols].head(10).to_string(index=False))

import json
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# setup
TMDB_RAW_PATH = Path("data/raw/tmdb/tmdb_raw.json")
LETTERBOXD_RAW_PATH = Path("data/raw/letterboxd/letterboxd_raw.json")
PROCESSED_DIR = Path("data/processed")

logging.basicConfig(
    filename="logs/data_processor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# load raw JSON data from TMDB and letterboxd
def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    if not TMDB_RAW_PATH.exists():
        raise FileNotFoundError(f"TMDB raw data not found at {TMDB_RAW_PATH}. Run api_collector.py first.")
    if not LETTERBOXD_RAW_PATH.exists():
        raise FileNotFoundError(f"Letterboxd raw data not found at {LETTERBOXD_RAW_PATH}. Run web_scraper.py first.")
 
    with open(TMDB_RAW_PATH, "r", encoding="utf-8") as f:
        tmdb_data = json.load(f)
 
    with open(LETTERBOXD_RAW_PATH, "r", encoding="utf-8") as f:
        letterboxd_data = json.load(f)
 
    logger.info(f"Loaded {len(tmdb_data)} TMDB records and {len(letterboxd_data)} Letterboxd records.")
    print(f"[Processor] Loaded {len(tmdb_data)} TMDB records and {len(letterboxd_data)} Letterboxd records.")
    return tmdb_data, letterboxd_data
 
# merge TMDB and letterboxd data; movies are matched on title and year; if not successfully scraped, the title is dropped
def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    tmdb_df = pd.DataFrame(tmdb_data)
    letterboxd_df = pd.DataFrame(letterboxd_data)
 
    # Extract year from release_date (format: "YYYY-MM-DD")
    tmdb_df["year"] = pd.to_datetime(tmdb_df["release_date"], errors="coerce").dt.year
 
    # Build a normalized merge key: lowercase title + year
    tmdb_df["merge_key"]       = tmdb_df["title"].str.lower().str.strip() + "_" + tmdb_df["year"].astype(str)
    letterboxd_df["merge_key"] = letterboxd_df["title"].str.lower().str.strip() + "_" + letterboxd_df["year"].astype(str)
 
    # Only keep successfully scraped Letterboxd records
    letterboxd_df = letterboxd_df[letterboxd_df["scraped_successfully"] == True]
 
    # Keep only the Letterboxd columns we need
    letterboxd_df = letterboxd_df[["merge_key", "letterboxd_rating", "num_fans", "url"]]
 
    # Inner join — drops any movie not found on Letterboxd
    merged = pd.merge(tmdb_df, letterboxd_df, on="merge_key", how="inner")
 
    # Drop the merge key column — no longer needed
    merged = merged.drop(columns=["merge_key"])
 
    logger.info(f"Merged dataset has {len(merged)} records.")
    print(f"[Processor] Merged dataset: {len(merged)} records.")
    return merged
 
# clean and validate merged dataframe
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    original_len = len(df)
 
    # Remove duplicates by TMDB ID
    df = df.drop_duplicates(subset="tmdb_id")
    logger.info(f"Removed {original_len - len(df)} duplicate rows.")
 
    # Standardize release_date to datetime
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
 
    # Ensure numeric types
    numeric_cols = ["budget", "revenue", "runtime", "tmdb_rating", "tmdb_vote_count",
                    "letterboxd_rating", "num_fans"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
 
    # TMDB uses 0 for unknown budget/revenue — replace with NaN
    df["budget"]  = df["budget"].replace(0, pd.NA)
    df["revenue"] = df["revenue"].replace(0, pd.NA)
 
    # Rename url to letterboxd_url for clarity
    if "url" in df.columns:
        df = df.rename(columns={"url": "letterboxd_url"})
 
    logger.info(f"Cleaned dataset has {len(df)} records.")
    print(f"[Processor] Cleaned dataset: {len(df)} records.")
    return df
 
# save processed dataframe as CSV and json
def save_processed_data(df: pd.DataFrame, output_dir: str = str(PROCESSED_DIR)) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
 
    csv_path = output_path / "movies_processed.csv"
    json_path = output_path / "movies_processed.json"
 
    # Save CSV — convert lists (genres, cast etc.) to strings for CSV compatibility
    df_csv = df.copy()
    for col in ["genres", "cast", "directors", "production_companies"]:
        if col in df_csv.columns:
            df_csv[col] = df_csv[col].apply(
                lambda x: ", ".join([str(i) for i in x]) if isinstance(x, list) else x
            )
    df_csv.to_csv(csv_path, index=False)
 
    # Save JSON — preserves list columns as-is
    df.to_json(json_path, orient="records", indent=2, date_format="iso")
 
    logger.info(f"Saved processed data to {csv_path} and {json_path}.")
    print(f"[Processor] Saved → {csv_path}")
    print(f"[Processor] Saved → {json_path}")
 
 
# ── Entry point ───────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    tmdb_data, letterboxd_data = load_raw_data()
    merged = merge_data(tmdb_data, letterboxd_data)
    cleaned = clean_data(merged)
    save_processed_data(cleaned)
    print(f"\n[Processor] Done. Final dataset: {len(cleaned)} movies.")
    print(cleaned[["title", "release_date", "tmdb_rating", "letterboxd_rating", "num_fans"]].head(10).to_string())

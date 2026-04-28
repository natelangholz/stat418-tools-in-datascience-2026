import glob
import json
import os
import logging
import pandas as pd
from typing import Dict, List, Tuple

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/data_processor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

TMDB_FIELDS = [
    "id", "title", "release_date", "runtime", "genres",
    "budget", "revenue", "vote_average", "vote_count",
    "production_companies", "original_language",
]
LB_FIELDS = ["letterboxd_rating", "letterboxd_fans"]


def _normalize_title(title: str) -> str:
    """Lowercase and strip a title for merge key construction."""
    return title.lower().strip()


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """Load raw TMDB detail files and Letterboxd JSON files from disk."""
    tmdb_records: List[Dict] = []
    for path in sorted(glob.glob("data/raw/tmdb/tmdb_movies_data.json")):
        with open(path, encoding="utf-8") as f:
            tmdb_records.extend(json.load(f).get("movies", []))
        logging.info(f"Loaded TMDB file: {path}")

    lb_records: List[Dict] = []
    for path in sorted(glob.glob("data/raw/letterboxd/letterboxd_movies_data.json")):
        with open(path, encoding="utf-8") as f:
            lb_records.extend(json.load(f).get("movies", []))
        logging.info(f"Loaded Letterboxd file: {path}")

    logging.info(f"Loaded {len(tmdb_records)} TMDB records, {len(lb_records)} Letterboxd records")
    return tmdb_records, lb_records


def _flatten_tmdb(record: Dict) -> Dict:
    """Extract and flatten relevant fields from a raw TMDB record."""
    details = record.get("details", {})

    genres_raw = details.get("genres") or []
    genres_str = "|".join(g["name"] for g in genres_raw if isinstance(g, dict))

    companies_raw = details.get("production_companies") or []
    companies_str = "|".join(c["name"] for c in companies_raw if isinstance(c, dict))

    return {
        "id": details.get("id"),
        "title": record.get("title", ""),
        "release_date": details.get("release_date", ""),
        "runtime": details.get("runtime"),
        "genres": genres_str,
        "budget": details.get("budget") or 0,
        "revenue": details.get("revenue") or 0,
        "vote_average": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "production_companies": companies_str,
        "original_language": details.get("original_language", ""),
    }


def merge_data(tmdb_data: List[Dict], lb_data: List[Dict]) -> pd.DataFrame:
    """Left-join TMDB records to Letterboxd records on normalised title + year."""
    tmdb_rows = [_flatten_tmdb(r) for r in tmdb_data]
    tmdb_df = pd.DataFrame(tmdb_rows)
    tmdb_df["_year"] = pd.to_datetime(tmdb_df["release_date"], errors="coerce").dt.year
    tmdb_df["_key"] = tmdb_df["title"].apply(_normalize_title) + "_" + tmdb_df["_year"].astype(str)

    lb_rows = []
    for r in lb_data:
        title = r.get("title", "")
        year = r.get("year")
        if not title or not year:
            continue
        lb_rows.append({
            "_key": _normalize_title(title) + "_" + str(int(year)),
            "letterboxd_rating": r.get("rating"),
            "letterboxd_fans": r.get("num_fans"),
        })
    lb_df = pd.DataFrame(lb_rows).drop_duplicates(subset="_key") if lb_rows else pd.DataFrame(columns=["_key", "letterboxd_rating", "letterboxd_fans"])

    merged = tmdb_df.merge(lb_df, on="_key", how="left")

    unmatched = merged["letterboxd_rating"].isna().sum()
    logging.info(f"Merged {len(merged)} rows; {unmatched} without Letterboxd data")

    merged.drop(columns=["_key", "_year"], inplace=True)
    return merged


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, coerce numeric fields, drop bad rows and duplicates."""
    df = df.copy()
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0).astype(int)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0).astype(int)
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce")
    df["letterboxd_rating"] = pd.to_numeric(df["letterboxd_rating"], errors="coerce")
    df["letterboxd_fans"] = pd.to_numeric(df["letterboxd_fans"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["title"])
    df = df[df["title"].str.strip() != ""]
    df = df.drop_duplicates(subset=["id"])
    logging.info(f"Cleaned: {before} → {len(df)} rows")
    return df.reset_index(drop=True)


def save_processed_data(df: pd.DataFrame, output_dir: str = "data/processed") -> None:
    """Write processed data to CSV and JSON."""
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "movies.csv")
    df.to_csv(csv_path, index=False)
    logging.info(f"Saved CSV: {csv_path} ({len(df)} rows)")

    json_path = os.path.join(output_dir, "movies.json")
    df.to_json(json_path, orient="records", indent=2, date_format="iso")
    logging.info(f"Saved JSON: {json_path}")


if __name__ == "__main__":
    tmdb_data, lb_data = load_raw_data()
    df = merge_data(tmdb_data, lb_data)
    df = clean_data(df)
    save_processed_data(df)
    print(f"Processed {len(df)} movies → data/processed/movies.csv")
    print(df[["title", "release_date", "vote_average", "letterboxd_rating"]].head(10).to_string())

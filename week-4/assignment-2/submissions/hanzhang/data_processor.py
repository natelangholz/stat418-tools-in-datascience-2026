import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


TMDB_PATH = Path("data/raw/tmdb/tmdb_movies_raw.json")
LETTERBOXD_PATH = Path("data/raw/letterboxd/letterboxd_movies_raw.json")
OUTPUT_DIR = Path("data/processed")
LOG_DIR = Path("logs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    if not TMDB_PATH.exists():
        raise FileNotFoundError(f"Missing file: {TMDB_PATH}")

    if not LETTERBOXD_PATH.exists():
        raise FileNotFoundError(f"Missing file: {LETTERBOXD_PATH}")

    with open(TMDB_PATH, "r", encoding="utf-8") as f:
        tmdb_data = json.load(f)

    with open(LETTERBOXD_PATH, "r", encoding="utf-8") as f:
        letterboxd_data = json.load(f)

    logging.info(f"Loaded {len(tmdb_data)} TMDB records")
    logging.info(f"Loaded {len(letterboxd_data)} Letterboxd records")

    return tmdb_data, letterboxd_data


def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    tmdb_df = pd.DataFrame(tmdb_data)
    letterboxd_df = pd.DataFrame(letterboxd_data)

    tmdb_df["release_year"] = pd.to_datetime(
        tmdb_df["release_date"],
        errors="coerce"
    ).dt.year

    merged_df = pd.merge(
        tmdb_df,
        letterboxd_df,
        left_on=["title", "release_year"],
        right_on=["title", "year"],
        how="left"
    )

    logging.info(f"Merged data shape: {merged_df.shape}")
    return merged_df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    cleaned["release_date"] = pd.to_datetime(cleaned["release_date"], errors="coerce")
    cleaned["release_year"] = cleaned["release_date"].dt.year

    numeric_columns = [
        "runtime",
        "budget",
        "revenue",
        "tmdb_rating",
        "vote_count",
        "popularity",
        "letterboxd_rating",
        "letterboxd_fans"
    ]

    for col in numeric_columns:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned.loc[cleaned["budget"] <= 1000, "budget"] = pd.NA
    cleaned.loc[cleaned["revenue"] <= 1000, "revenue"] = pd.NA

    cleaned["profit"] = cleaned["revenue"] - cleaned["budget"]

    cleaned["letterboxd_rating_10"] = cleaned["letterboxd_rating"] * 2

    cleaned["genres_text"] = cleaned["genres"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )

    cleaned["production_companies_text"] = cleaned["production_companies"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )

    cleaned["top_cast_text"] = cleaned["top_cast"].apply(
        lambda cast: ", ".join(
            person.get("name", "") for person in cast
        ) if isinstance(cast, list) else ""
    )

    cleaned["top_crew_text"] = cleaned["top_crew"].apply(
        lambda crew: ", ".join(
            f"{person.get('name', '')} ({person.get('job', '')})"
            for person in crew
        ) if isinstance(crew, list) else ""
    )

    cleaned = cleaned.drop_duplicates(subset=["tmdb_id"], keep="first")

    selected_columns = [
        "tmdb_id",
        "title",
        "release_date",
        "release_year",
        "runtime",
        "genres_text",
        "budget",
        "revenue",
        "profit",
        "tmdb_rating",
        "letterboxd_rating",
        "letterboxd_rating_10",
        "vote_count",
        "letterboxd_fans",
        "popularity",
        "original_language",
        "production_companies_text",
        "top_cast_text",
        "top_crew_text",
        "overview",
        "letterboxd_url",
        "scrape_success",
        "error"
    ]

    cleaned = cleaned[[col for col in selected_columns if col in cleaned.columns]]

    logging.info(f"Cleaned data shape: {cleaned.shape}")
    return cleaned


def save_processed_data(df: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> None:
    csv_path = output_dir / "movies_processed.csv"
    json_path = output_dir / "movies_processed.json"

    df.to_csv(csv_path, index=False)

    df.to_json(
        json_path,
        orient="records",
        indent=2,
        force_ascii=False,
        date_format="iso"
    )

    logging.info(f"Saved processed CSV to {csv_path}")
    logging.info(f"Saved processed JSON to {json_path}")

    print(f"Saved processed CSV to {csv_path}")
    print(f"Saved processed JSON to {json_path}")
    print(f"Total processed rows: {len(df)}")


def main():
    tmdb_data, letterboxd_data = load_raw_data()
    merged_df = merge_data(tmdb_data, letterboxd_data)
    cleaned_df = clean_data(merged_df)
    save_processed_data(cleaned_df)


if __name__ == "__main__":
    main()

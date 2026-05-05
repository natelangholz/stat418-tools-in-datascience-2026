import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """Load TMDB and Letterboxd data."""
    tmdb_data = []
    letterboxd_data = []

    raw_dir = Path("data/raw")
    scraped_dir = Path("data/scraped")

    for file in raw_dir.glob("movie_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            tmdb_data.append(json.load(f))

    all_movies_file = scraped_dir / "all_movies.json"

    if all_movies_file.exists():
        with open(all_movies_file, "r", encoding="utf-8") as f:
            letterboxd_data = json.load(f)

    return tmdb_data, letterboxd_data


def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    """Merge TMDB and Letterboxd data on title and year."""

    tmdb_rows = []

    for item in tmdb_data:
        details = item.get("details", {})

        release_date = details.get("release_date", "")
        year = release_date[:4] if release_date else None

        tmdb_rows.append({
            "title": details.get("title"),
            "year": year,
            "release_date": release_date,
            "runtime": details.get("runtime"),

            "genres": [
                genre.get("name")
                for genre in details.get("genres", [])
                ],

            "budget": details.get("budget"),
            "revenue": details.get("revenue"),

            "tmdb_rating": details.get("vote_average"),
            "tmdb_vote_count": details.get("vote_count"),

            "production_companies": [
                company.get("name")
                for company in details.get("production_companies", [])
                ],

            "original_language": details.get("original_language"),

            "cast_top_5": [
             {
                "name": actor.get("name"),
                "character": actor.get("character")
                }
            for actor in item.get("credits", {}).get("cast", [])[:5]
                ],

            "crew_top_5": [
            {
            "name": person.get("name"),
            "job": person.get("job")
            }
            for person in item.get("credits", {}).get("crew", [])[:5]
        ]
    })
   

    letterboxd_rows = []

    for item in letterboxd_data:
        letterboxd_rows.append({
            "title": item.get("title"),
            "year": str(item.get("year")) if item.get("year") else None,
            "letterboxd_rating": item.get("rating"),
            "letterboxd_fans": item.get("num_fans"),
            "letterboxd_url": item.get("url"),
            "scraped_successfully": item.get("scraped_successfully")
        })

    tmdb_df = pd.DataFrame(tmdb_rows)
    letterboxd_df = pd.DataFrame(letterboxd_rows)

    merged_df = pd.merge(
        tmdb_df,
        letterboxd_df,
        on=["title", "year"],
        how="left"
    )

    return merged_df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean merged data."""

    df = df.copy()
    

    df["title"] = df["title"].str.strip()
    df["year"] = df["year"].astype(str)

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    numeric_columns = [
        "tmdb_rating",
        "tmdb_vote_count",
        "runtime",
        "budget",
        "revenue",
        "letterboxd_rating",
        "letterboxd_fans"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["letterboxd_rating"] = df["letterboxd_rating"].fillna(0)
    df["letterboxd_fans"] = df["letterboxd_fans"].fillna(0)

    df = df.drop_duplicates(subset=["title", "year"])

    return df


def save_processed_data(df: pd.DataFrame, output_dir: str):
    """Save processed data as CSV and JSON."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    df_for_csv = df.copy()

    list_columns = [
        "genres",
        "production_companies",
        "cast_top_5",
        "crew_top_5"
    ]

    for col in list_columns:
        if col in df_for_csv.columns:
            df_for_csv[col] = df_for_csv[col].apply(json.dumps)

    df_for_csv.to_csv(output_path / "processed_movies.csv", index=False)
    df.to_json(output_path / "processed_movies.json", orient="records", indent=4)


if __name__ == "__main__":
    tmdb_data, letterboxd_data = load_raw_data()

    merged_df = merge_data(tmdb_data, letterboxd_data)
    clean_df = clean_data(merged_df)

    save_processed_data(clean_df, "data/processed")

    print(f"Processed {len(clean_df)} movies.")
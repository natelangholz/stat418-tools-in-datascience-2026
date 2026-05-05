import os
import json
import pandas as pd
from typing import Dict, List, Tuple


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """Load TMDB and Letterboxd data."""
    with open("data/raw/tmdb/tmdb_movies.json", "r") as f:
        tmdb_data = json.load(f)

    with open("data/raw/letterboxd/letterboxd_movies.json", "r") as f:
        letterboxd_data = json.load(f)

    return tmdb_data, letterboxd_data


def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    """Merge TMDB and Letterboxd data."""
    tmdb_rows = []

    for movie in tmdb_data:
        row = {
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "year": movie.get("release_date", "")[:4],
            "runtime": movie.get("runtime"),
            "budget": movie.get("budget"),
            "revenue": movie.get("revenue"),
            "tmdb_rating": movie.get("vote_average"),
            "vote_count": movie.get("vote_count"),
            "genres": ", ".join([g["name"] for g in movie.get("genres", [])]),
            "original_language": movie.get("original_language"),
            "top_cast": ", ".join(movie.get("top_cast", [])),
            "top_crew": ", ".join(movie.get("top_crew", []))
        }

        tmdb_rows.append(row)

    tmdb_df = pd.DataFrame(tmdb_rows)
    letterboxd_df = pd.DataFrame(letterboxd_data)

    df = pd.merge(tmdb_df, letterboxd_df, on=["title", "year"], how="left")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean movie data."""
    df = df.drop_duplicates(subset=["title", "year"])

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce")
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["tmdb_rating"] = pd.to_numeric(df["tmdb_rating"], errors="coerce")
    df["letterboxd_rating"] = pd.to_numeric(df["letterboxd_rating"], errors="coerce")
    df["num_fans"] = pd.to_numeric(df["num_fans"], errors="coerce")

    df["profit"] = df["revenue"] - df["budget"]

    return df


def save_processed_data(df: pd.DataFrame, output_dir: str) -> None:
    """Save processed data."""
    os.makedirs(output_dir, exist_ok=True)

    df.to_csv(f"{output_dir}/processed_movies.csv", index=False)
    df.to_json(f"{output_dir}/processed_movies.json", orient="records", indent=2)


if __name__ == "__main__":
    tmdb_data, letterboxd_data = load_raw_data()

    df = merge_data(tmdb_data, letterboxd_data)
    df = clean_data(df)

    save_processed_data(df, "data/processed")

    print("Processed data saved.")
    print(df.head())
    print(df.shape)
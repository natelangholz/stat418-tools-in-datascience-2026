import json
import os
import pandas as pd
from typing import Tuple, List, Dict


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    """Load raw JSON files from TMDB and Letterboxd collectors."""
    with open('data/raw/tmdb/movies.json') as f:
        tmdb_data = json.load(f)
    with open('data/raw/letterboxd/ratings.json') as f:
        letterboxd_data = json.load(f)
    return tmdb_data, letterboxd_data


def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    """Left-join TMDB and Letterboxd data on normalized movie title."""
    tmdb_df = pd.DataFrame(tmdb_data)
    lb_df = pd.DataFrame(letterboxd_data)

    # Normalize titles for matching
    tmdb_df['title_key'] = tmdb_df['title'].str.lower().str.strip()
    lb_df['title_key'] = lb_df['title'].str.lower().str.strip()

    merged = tmdb_df.merge(
        lb_df[['title_key', 'letterboxd_rating', 'num_fans', 'scraped_successfully']],
        on='title_key',
        how='left'
    ).drop(columns=['title_key'])
    return merged


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the merged dataframe."""
    # Drop duplicates
    df = df.drop_duplicates(subset='id')

    # Parse release date
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year

    # Replace 0 budget/revenue with NaN (TMDB returns 0 when unknown)
    df['budget'] = df['budget'].replace(0, pd.NA)
    df['revenue'] = df['revenue'].replace(0, pd.NA)

    # Convert genres list to pipe-separated string for CSV compatibility
    df['genres_str'] = df['genres'].apply(
        lambda g: '|'.join(g) if isinstance(g, list) else ''
    )
    df['cast_str'] = df['cast'].apply(
        lambda c: '|'.join(c) if isinstance(c, list) else ''
    )
    df['directors_str'] = df['directors'].apply(
        lambda d: '|'.join(d) if isinstance(d, list) else ''
    )

    return df.reset_index(drop=True)


def save_processed_data(df: pd.DataFrame, output_dir: str) -> None:
    """Save processed dataframe as both CSV and JSON to output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    # Save CSV (drop list columns)
    csv_df = df.drop(columns=['genres', 'cast', 'directors', 'production_companies'], errors='ignore')
    csv_path = os.path.join(output_dir, 'movies_processed.csv')
    csv_df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")

    # Save JSON
    json_path = os.path.join(output_dir, 'movies_processed.json')
    df.to_json(json_path, orient='records', indent=2, default_handler=str, date_format='iso')
    print(f"Saved JSON: {json_path}")


if __name__ == '__main__':
    tmdb_data, letterboxd_data = load_raw_data()
    print(f"Loaded {len(tmdb_data)} TMDB records, {len(letterboxd_data)} Letterboxd records")

    df = merge_data(tmdb_data, letterboxd_data)
    df = clean_data(df)
    print(f"After merge & clean: {len(df)} rows, {df.columns.tolist()}")

    save_processed_data(df, 'data/processed')

    # Quick summary
    print(f"\nLetterboxd rating available: {df['letterboxd_rating'].notna().sum()}/{len(df)}")
    print(f"Budget available: {df['budget'].notna().sum()}/{len(df)}")
    print(df[['title', 'tmdb_rating', 'letterboxd_rating', 'release_year']].head(10).to_string(index=False))

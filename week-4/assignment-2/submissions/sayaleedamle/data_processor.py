import json
import os
import logging
import pandas as pd
from typing import Dict, List, Tuple

os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs', exist_ok=True)
os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/processed', exist_ok=True)

logging.basicConfig(
    filename='stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs/data_processor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------- #
# 1. LOAD RAW DATA                                                               #
# Reads the JSON files saved by api_collector.py and web_scrapper.py.           #
# Returns two lists of dicts — one per source.                                  #
# ---------------------------------------------------------------------------- #
def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    tmdb_path = 'stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw/movies_full.json'
    letterboxd_path = 'stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw/letterboxd_movies.json'

    with open(tmdb_path, encoding='utf-8') as f:
        raw_tmdb = json.load(f)
    logger.info(f"Loaded {len(raw_tmdb)} TMDB records from {tmdb_path}")

    with open(letterboxd_path, encoding='utf-8') as f:
        letterboxd_data = json.load(f)
    logger.info(f"Loaded {len(letterboxd_data)} Letterboxd records from {letterboxd_path}")

    # TMDB records are nested: {'details': {...}, 'credits': {...}}
    # Flatten to a single dict per movie, pulling cast/crew into top-level keys.
    tmdb_data = []
    for record in raw_tmdb:
        details = record.get('details', {})
        credits = record.get('credits', {})
        flat = {**details}
        flat['cast'] = [
            {'name': m.get('name'), 'character': m.get('character'), 'order': m.get('order')}
            for m in credits.get('cast', [])[:10]   # top-10 billed cast
        ]
        flat['crew'] = [
            {'name': m.get('name'), 'job': m.get('job'), 'department': m.get('department')}
            for m in credits.get('crew', [])
            if m.get('job') in ('Director', 'Writer', 'Producer')
        ]
        tmdb_data.append(flat)

    return tmdb_data, letterboxd_data


# ---------------------------------------------------------------------------- #
# 2. MERGE DATA                                                                  #
# Joins on lowercase title + year so minor capitalisation differences don't     #
# prevent a match. Letterboxd columns are suffixed _lb to avoid collisions.     #
# ---------------------------------------------------------------------------- #
def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    tmdb_df = pd.DataFrame(tmdb_data)
    lb_df = pd.DataFrame(letterboxd_data)

    # Normalise join keys
    tmdb_df['_title_key'] = tmdb_df['title'].str.lower().str.strip()
    tmdb_df['_year_key'] = pd.to_datetime(
        tmdb_df['release_date'], errors='coerce'
    ).dt.year

    lb_df['_title_key'] = lb_df['title'].str.lower().str.strip()
    lb_df['_year_key'] = lb_df['year']

    lb_df = lb_df.rename(columns={'rating': 'lb_rating', 'num_fans': 'lb_num_fans'})
    lb_cols = ['_title_key', '_year_key', 'lb_rating', 'lb_num_fans', 'url']

    merged = tmdb_df.merge(
        lb_df[lb_cols],
        on=['_title_key', '_year_key'],
        how='left',
    )
    merged = merged.drop(columns=['_title_key', '_year_key'])

    logger.info(
        f"Merged: {len(tmdb_df)} TMDB + {len(lb_df)} Letterboxd → {len(merged)} rows "
        f"({merged['lb_rating'].notna().sum()} matched)"
    )
    return merged


# ---------------------------------------------------------------------------- #
# 3. CLEAN DATA                                                                  #
# • Standardises release_date to YYYY-MM-DD                                     #
# • Normalises TMDB vote_average (0-10) and lb_rating (0-5) to 0-10            #
# • Fills missing numeric values with column medians                            #
# • Fills missing string values with 'Unknown'                                  #
# • Drops exact duplicate rows                                                  #
# ---------------------------------------------------------------------------- #
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- dates ---
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce').dt.strftime('%Y-%m-%d')

    # --- ratings: normalise lb_rating from 0-5 scale to 0-10 ---
    if 'lb_rating' in df.columns:
        df['lb_rating_normalized'] = df['lb_rating'] * 2

    # --- rename TMDB rating column for clarity ---
    if 'vote_average' in df.columns:
        df = df.rename(columns={'vote_average': 'tmdb_rating'})

    # --- missing numerics → median ---
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        median = df[col].median()
        missing = df[col].isna().sum()
        if missing:
            df[col] = df[col].fillna(median)
            logger.info(f"Filled {missing} missing values in '{col}' with median {median:.2f}")

    # --- missing strings → 'Unknown' ---
    string_cols = df.select_dtypes(include='object').columns
    for col in string_cols:
        missing = df[col].isna().sum()
        if missing:
            df[col] = df[col].fillna('Unknown')
            logger.info(f"Filled {missing} missing values in '{col}' with 'Unknown'")

    # --- duplicates ---
    # Columns with list/dict values can't be hashed by pandas.
    # Deduplicate on scalar columns only, then keep the full row.
    before = len(df)
    hashable_cols = [
        c for c in df.columns
        if not df[c].map(lambda x: isinstance(x, (list, dict))).any()
    ]
    df = df[~df[hashable_cols].duplicated()]
    removed = before - len(df)
    if removed:
        logger.info(f"Removed {removed} duplicate rows")

    logger.info(f"Clean data: {len(df)} rows, {len(df.columns)} columns")
    return df


# ---------------------------------------------------------------------------- #
# 4. SAVE PROCESSED DATA                                                         #
# Writes the cleaned DataFrame to both CSV and JSON in output_dir.              #
# ---------------------------------------------------------------------------- #
def save_processed_data(df: pd.DataFrame, output_dir: str = 'stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/processed'):
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'movies_processed.csv')
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV: {csv_path} ({len(df)} rows)")

    json_path = os.path.join(output_dir, 'movies_processed.json')
    df.to_json(json_path, orient='records', indent=2, force_ascii=False)
    logger.info(f"Saved JSON: {json_path} ({len(df)} rows)")


# ---------------------------------------------------------------------------- #
# MAIN                                                                           #
# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    tmdb_data, letterboxd_data = load_raw_data()
    merged = merge_data(tmdb_data, letterboxd_data)
    cleaned = clean_data(merged)
    save_processed_data(cleaned)
    print(f"Done — {len(cleaned)} movies processed.")
    print(cleaned[['title', 'release_date', 'tmdb_rating', 'lb_rating_normalized']].head())

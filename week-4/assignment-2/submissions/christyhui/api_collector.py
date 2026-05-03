import requests
import os
import time
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional


# load API key and perform setup
env_path = os.path.join(os.path.expanduser("~"), "Documents", ".env")

load_dotenv(env_path)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
RATE_LIMIT_SLEEP = 0.25
MAX_RETRIES = 3
RETRY_DELAY = 2.0

Path("logs").mkdir(exist_ok=True)
Path("data/raw/tmdb").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename='logs/api_collector.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# create helper functions to collect data from API

def make_request(endpoint: str, params: Optional[Dict] = None) -> Dict:
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY

    url = f"{BASE_URL}/{endpoint}"

    for attempt in range(1, MAX_RETRIES + 1):
        time.sleep(RATE_LIMIT_SLEEP)
        try:
            response = requests.get(url, params = params, timeout = 10)
            response.raise_for_status()
            logger.info(f"{datetime.now().isoformat()} - GET /{endpoint} - 200 OK")
            return response.json()
        except requests.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            logger.warning(f"HTTP {status} on /{endpoint} (attempt {attempt}/{MAX_RETRIES})")
            if status == 429:
                # Rate limited — back off longer than usual
                time.sleep(RETRY_DELAY * attempt * 2)
            elif attempt == MAX_RETRIES:
                logger.error(f"Giving up on /{endpoint} after {MAX_RETRIES} attempts.")
                raise
            else:
                time.sleep(RETRY_DELAY * attempt)
        except requests.RequestException as e:
            logger.warning(f"Request error on /{endpoint} (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES:
                logger.error(f"Giving up on /{endpoint} after {MAX_RETRIES} attempts.")
                raise
            time.sleep(RETRY_DELAY * attempt)


def get_popular_movies(page: int = 1) -> List[Dict]:
    data = make_request("movie/popular", {"page": page})
    results = data.get("results", [])
    logger.info(f"Fetched {len(results)} popular movies from page {page}.")
    return results

def get_movie_details(movie_id: int) -> Dict:
    data = make_request(f"movie/{movie_id}")
    logger.info(f"Fetched details for movie ID {movie_id}: {data.get('title', '?')}")
    return data

def get_movie_credits(movie_id: int) -> Dict:
    data = make_request(f"movie/{movie_id}/credits")
    logger.info(f"Fetched credits for movie ID {movie_id}.")
    return data

def build_movie_record(details: Dict, credits: Dict) -> Dict:

    top_cast = [
        {
            "name": member.get("name"),
            "character": member.get("character"),
            "order": member.get("order"),
        }
        for member in credits.get("cast", [])[:5]
    ]
 
    directors = [
        {"name": member.get("name")}
        for member in credits.get("crew", [])
        if member.get("job") == "Director"
    ]
 
    return {
        # Identification
        "tmdb_id": details.get("id"),
        "title": details.get("title"),
        "original_title": details.get("original_title"),
        "original_language":  details.get("original_language"),

        # Release & runtime
        "release_date": details.get("release_date"),
        "runtime": details.get("runtime"),

        # Genres
        "genres": [g["name"] for g in details.get("genres", [])],

        # Financial
        "budget": details.get("budget"),
        "revenue": details.get("revenue"),

        # Ratings
        "tmdb_rating": details.get("vote_average"),
        "tmdb_vote_count": details.get("vote_count"),

        # Production
        "production_companies": [c["name"] for c in details.get("production_companies", [])],

        # People
        "cast": top_cast,
        "directors": directors,

        # Overview
        "overview": details.get("overview"),

        # Metadata
        "collected_at": datetime.now().isoformat(),
    }
 
 
def collect_all_data(num_items: int = 50) -> List[Dict]:
    logger.info(f"Starting collection for {num_items} movies.")
    print(f"[TMDB] Collecting {num_items} movies...")
 
    # get movie summaries
    summaries: List[Dict] = []
    page = 1
    while len(summaries) < num_items:
        page_results = get_popular_movies(page=page)
        if not page_results:
            logger.warning(f"No results returned on page {page}. Stopping early.")
            break
        summaries.extend(page_results)
        page += 1
 
    summaries = summaries[:num_items]
    logger.info(f"Gathered {len(summaries)} movie summaries.")
 
    # get details + credits
    enriched: List[Dict] = []
    failed: List[int] = []
 
    for i, summary in enumerate(summaries, start=1):
        movie_id = summary.get("id")
        title = summary.get("title", "Unknown")
        print(f"  [{i}/{len(summaries)}] {title} (ID: {movie_id})")
 
        try:
            details = get_movie_details(movie_id)
            credits = get_movie_credits(movie_id)
            record = build_movie_record(details, credits)
            enriched.append(record)
        except Exception as e:
            logger.error(f"Skipping movie ID {movie_id} ({title}): {e}")
            failed.append(movie_id)
 
    logger.info(f"Collection complete. {len(enriched)} succeeded, {len(failed)} failed.")
    print(f"\n[TMDB] Done. {len(enriched)} collected, {len(failed)} skipped.")
    return enriched
 
 
def save_data(data: List[Dict], filename: str = "tmdb_raw.json") -> str:
    output_path = Path("data/raw/tmdb") / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} records to {output_path}.")
    print(f"[TMDB] Raw data saved → {output_path}")
    return str(output_path)
 
 
# ── Entry point ───────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    movies = collect_all_data(num_items=50)
    save_data(movies, filename="tmdb_raw.json")

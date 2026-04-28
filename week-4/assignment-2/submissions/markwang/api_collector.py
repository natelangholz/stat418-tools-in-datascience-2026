"""TMDB API data collector for movie data."""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

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

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RAW_DATA_DIR = Path("data/raw/tmdb")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiting: 40 requests per 10 seconds
_RATE_LIMIT_REQUESTS = 40
_RATE_LIMIT_WINDOW = 10.0
_request_times: List[float] = []


def _enforce_rate_limit() -> None:
    """Enforce TMDB API rate limit of 40 requests per 10 seconds."""
    global _request_times
    now = time.time()
    _request_times = [t for t in _request_times if now - t < _RATE_LIMIT_WINDOW]
    if len(_request_times) >= _RATE_LIMIT_REQUESTS:
        sleep_time = _RATE_LIMIT_WINDOW - (now - _request_times[0]) + 0.05
        if sleep_time > 0:
            logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
    _request_times.append(time.time())


def _make_request(
    endpoint: str,
    params: Optional[Dict] = None,
    retries: int = 3,
) -> Optional[Dict]:
    """Make a rate-limited GET request to the TMDB API with retry logic."""
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY is not set. Add it to your .env file.")

    url = f"{TMDB_BASE_URL}/{endpoint}"
    request_params: Dict = {"api_key": TMDB_API_KEY}
    if params:
        request_params.update(params)

    for attempt in range(retries):
        _enforce_rate_limit()
        try:
            logger.info(f"GET {url} (attempt {attempt + 1}/{retries})")
            response = requests.get(url, params=request_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            if status == 429:
                wait = 2 ** attempt
                logger.warning(f"Rate limited (429), retrying in {wait}s")
                time.sleep(wait)
            elif status == 404:
                logger.warning(f"Not found (404): {url}")
                return None
            else:
                logger.error(f"HTTP {status} error: {exc}")
                if attempt == retries - 1:
                    return None
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as exc:
            logger.error(f"Request error: {exc}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


def get_popular_movies(page: int = 1) -> List[Dict]:
    """Fetch one page of popular movies from TMDB.

    Args:
        page: Page number (1-indexed).

    Returns:
        List of movie summary dicts from TMDB.
    """
    data = _make_request("movie/popular", {"page": page, "language": "en-US"})
    if not data:
        return []
    movies = data.get("results", [])
    logger.info(f"Fetched {len(movies)} popular movies (page {page})")
    return movies


def get_movie_details(movie_id: int) -> Dict:
    """Fetch full details for a single movie.

    Args:
        movie_id: TMDB movie ID.

    Returns:
        Movie detail dict, or empty dict on failure.
    """
    data = _make_request(f"movie/{movie_id}", {"language": "en-US"})
    if not data:
        logger.warning(f"No details for movie_id={movie_id}")
        return {}
    logger.info(f"Got details: {data.get('title', movie_id)}")
    return data


def get_movie_credits(movie_id: int) -> Dict:
    """Fetch cast and crew for a movie, returning top 5 of each.

    Args:
        movie_id: TMDB movie ID.

    Returns:
        Dict with 'cast' and 'crew' lists (up to 5 entries each).
    """
    data = _make_request(f"movie/{movie_id}/credits", {"language": "en-US"})
    if not data:
        return {"cast": [], "crew": []}
    cast = data.get("cast", [])[:5]
    crew = data.get("crew", [])[:5]
    logger.info(f"Got credits for movie_id={movie_id}: {len(cast)} cast, {len(crew)} crew")
    return {"cast": cast, "crew": crew}


def collect_all_data(num_items: int = 50) -> List[Dict]:
    """Collect enriched data for the top num_items popular movies.

    Fetches the popular movie list, then retrieves details and credits for
    each movie. Saves raw API responses to data/raw/tmdb/.

    Args:
        num_items: Number of movies to collect.

    Returns:
        List of enriched movie dicts.
    """
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY not found. Set it in your .env file.")

    logger.info(f"Starting TMDB data collection for {num_items} movies")

    # Gather enough movie IDs from popular pages
    all_summaries: List[Dict] = []
    page = 1
    while len(all_summaries) < num_items:
        page_movies = get_popular_movies(page)
        if not page_movies:
            break
        all_summaries.extend(page_movies)
        page += 1

    all_summaries = all_summaries[:num_items]

    # Save raw popular list
    popular_path = RAW_DATA_DIR / "popular_movies.json"
    with open(popular_path, "w") as f:
        json.dump(all_summaries, f, indent=2)
    logger.info(f"Saved popular movie list to {popular_path}")

    # Enrich each movie with details and credits
    enriched: List[Dict] = []
    for i, summary in enumerate(all_summaries, 1):
        movie_id = summary["id"]
        logger.info(f"Processing {i}/{len(all_summaries)}: movie_id={movie_id}")

        details = get_movie_details(movie_id)
        credits = get_movie_credits(movie_id)

        if not details:
            logger.warning(f"Skipping movie_id={movie_id} — no details returned")
            continue

        record: Dict = {
            "id": details.get("id"),
            "title": details.get("title"),
            "release_date": details.get("release_date"),
            "runtime": details.get("runtime"),
            "genres": [g["name"] for g in details.get("genres", [])],
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "vote_average": details.get("vote_average"),
            "vote_count": details.get("vote_count"),
            "original_language": details.get("original_language"),
            "production_companies": [
                pc["name"] for pc in details.get("production_companies", [])
            ],
            "overview": details.get("overview"),
            "cast": [
                {
                    "name": c["name"],
                    "character": c.get("character"),
                    "order": c.get("order"),
                }
                for c in credits.get("cast", [])
            ],
            "crew": [
                {
                    "name": c["name"],
                    "job": c.get("job"),
                    "department": c.get("department"),
                }
                for c in credits.get("crew", [])
            ],
            "collected_at": datetime.now().isoformat(),
        }
        enriched.append(record)

        # Save individual file for debugging
        movie_path = RAW_DATA_DIR / f"movie_{movie_id}.json"
        with open(movie_path, "w") as f:
            json.dump(record, f, indent=2)

    # Save combined file
    combined_path = RAW_DATA_DIR / "all_movies.json"
    with open(combined_path, "w") as f:
        json.dump(enriched, f, indent=2)
    logger.info(f"Saved {len(enriched)} enriched movies to {combined_path}")

    return enriched


if __name__ == "__main__":
    movies = collect_all_data(num_items=50)
    print(f"Collected data for {len(movies)} movies")

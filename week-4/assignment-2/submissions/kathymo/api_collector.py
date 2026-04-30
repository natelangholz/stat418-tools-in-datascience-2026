
"""
api_collector.py
----------------
Collects movie data from The Movie Database (TMDB) API.

Data sources:
  - TMDB REST API v3 (https://api.themoviedb.org/3)
    Academic / non-commercial use only.

Ethical guidelines followed:
  - Rate limiting: max 40 requests per 10 seconds (enforced via token bucket)
  - Exponential-backoff retry on transient errors
  - All requests logged with timestamps
  - No personal user data collected
  - Data used for academic purposes only (UCLA STAT418)
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Directory setup  (created before logging so FileHandler never fails)
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
TMDB_DIR = DATA_DIR / "raw" / "tmdb"

for folder in [LOG_DIR, TMDB_DIR, DATA_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

RAW_TMDB_DIR = TMDB_DIR
# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "api_collector.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# TMDB allows 40 requests per 10 seconds
RATE_LIMIT_REQUESTS = 40
RATE_LIMIT_WINDOW = 10.0  # seconds

MAX_RETRIES = 3
RETRY_BACKOFF = 2  

# ---------------------------------------------------------------------------
# Rate limiter  (token-bucket — keeps a sliding window of timestamps)
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Ensures we never exceed TMDB's 40-requests-per-10-seconds limit."""

    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS,
                 window: float = RATE_LIMIT_WINDOW) -> None:
        self.max_requests = max_requests
        self.window = window
        self._timestamps: List[float] = []

    def wait(self) -> None:
        """Block until a new request slot is available."""
        now = time.time()
        # Drop timestamps outside the current window
        self._timestamps = [t for t in self._timestamps if now - t < self.window]
        if len(self._timestamps) >= self.max_requests:
            sleep_for = self.window - (now - self._timestamps[0]) + 0.05
            if sleep_for > 0:
                logger.debug("Rate limit reached – sleeping %.2fs", sleep_for)
                time.sleep(sleep_for)
        self._timestamps.append(time.time())


# ---------------------------------------------------------------------------
# Main collector class  (matches the provided template + required extensions)
# ---------------------------------------------------------------------------

class TMDBCollector:
    """
    Authenticates with the TMDB API and collects movie data.

    Implements:
      - Token-bucket rate limiting (40 req / 10 s)
      - Exponential-backoff retry logic
      - Per-movie JSON persistence to data/raw/tmdb/
      - Timestamped logging of every API call
    """

    def __init__(self) -> None:
        self.api_key: Optional[str] = os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "TMDB_API_KEY not found. "
                "Add it to your .env file: TMDB_API_KEY=your_key_here"
            )

        self.base_url: str = TMDB_BASE_URL
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            "User-Agent": "UCLA STAT418 Student - student@ucla.edu",
            "Accept": "application/json",
        })

        # Legacy interval kept for reference; actual throttling uses _RateLimiter
        self.last_request_time: float = 0
        self.min_request_interval: float = 0.25   # 4 req/s soft floor

        self._rate_limiter = _RateLimiter()
        logger.info("TMDBCollector initialised (api_key=***%s)", self.api_key[-4:])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rate_limit(self) -> None:
        """
        Enforce rate limits.

        Uses both the legacy per-request interval (min_request_interval)
        and the sliding-window token bucket (_rate_limiter) so that burst
        behaviour is fully controlled.
        """
        # Legacy simple delay
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        # Token-bucket window check
        self._rate_limiter.wait()
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a TMDB API GET request with rate limiting and retry logic.

        Args:
            endpoint: API path, e.g. 'movie/popular' or 'movie/550'.
            params:   Extra query parameters (api_key is injected automatically).

        Returns:
            Parsed JSON response as a dict.

        Raises:
            requests.HTTPError: After MAX_RETRIES failed attempts.
        """
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(1, MAX_RETRIES + 1):
            self._rate_limit()
            timestamp = datetime.now(timezone.utc).isoformat()
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                logger.info("[%s] GET /%s → 200 OK", timestamp, endpoint)
                return response.json()

            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response else "N/A"
                if status == 429:
                    wait = RETRY_BACKOFF ** attempt
                    logger.warning(
                        "[%s] 429 Too Many Requests for /%s – retrying in %ss",
                        timestamp, endpoint, wait,
                    )
                    time.sleep(wait)
                elif attempt == MAX_RETRIES:
                    logger.error(
                        "[%s] GET /%s failed after %d attempts: %s",
                        timestamp, endpoint, MAX_RETRIES, exc,
                    )
                    raise
                else:
                    logger.warning(
                        "[%s] Attempt %d for /%s failed (%s) – retrying…",
                        timestamp, attempt, endpoint, exc,
                    )
                    time.sleep(RETRY_BACKOFF * attempt)

            except requests.exceptions.RequestException as exc:
                if attempt == MAX_RETRIES:
                    logger.error(
                        "[%s] Network error for /%s after %d attempts: %s",
                        timestamp, endpoint, MAX_RETRIES, exc,
                    )
                    raise
                logger.warning(
                    "[%s] Network error on attempt %d for /%s: %s",
                    timestamp, attempt, endpoint, exc,
                )
                time.sleep(RETRY_BACKOFF * attempt)

        return {}  # unreachable; satisfies type checker

    # ------------------------------------------------------------------
    # Required public functions
    # ------------------------------------------------------------------

    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """
        Fetch one page of popular movies from TMDB.

        Args:
            page: Page number (1-indexed; each page contains up to 20 results).

        Returns:
            List of movie summary dicts (title, id, release_date, etc.)
        """
        data = self._make_request("movie/popular", {"page": page})
        results = data.get("results", [])
        logger.info("Fetched %d popular movies from page %d", len(results), page)
        return results

    def get_movie_details(self, movie_id: int) -> Dict:
        """
        Fetch full details for a single movie.

        Includes: title, release date, runtime, genres, budget, revenue,
        production companies, original language, TMDB rating, vote count,
        overview, status, and IMDb ID (used for cross-referencing).

        Args:
            movie_id: TMDB numeric movie ID.

        Returns:
            Movie detail dict.
        """
        data = self._make_request(f"movie/{movie_id}")
        logger.info(
            "Fetched details for movie %d – '%s'",
            movie_id, data.get("title", "unknown"),
        )
        return data

    def get_movie_credits(self, movie_id: int) -> Dict:
        """
        Fetch cast and crew for a movie.

        Args:
            movie_id: TMDB numeric movie ID.

        Returns:
            Dict with 'cast' (ordered by billing) and 'crew' lists.
        """
        data = self._make_request(f"movie/{movie_id}/credits")
        logger.info(
            "Fetched credits for movie %d – %d cast, %d crew",
            movie_id,
            len(data.get("cast", [])),
            len(data.get("crew", [])),
        )
        return data

    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        """
        Collect popular movies with full details and credits.

        Fetches enough pages of popular movies to reach *num_items*, then
        enriches each entry with:
          - Full movie details (runtime, budget, revenue, genres,
            production companies, original language, etc.)
          - Top-5 cast members and director from credits

        Each movie is saved as an individual JSON file in data/raw/tmdb/
        and a combined all_movies.json is written at the end.

        Args:
            num_items: Target number of movies to collect (default 50).

        Returns:
            List of enriched movie dicts, one per collected movie.
        """
        logger.info("Starting collection of %d movies…", num_items)
        enriched: List[Dict] = []
        page = 1

        while len(enriched) < num_items:
            movies = self.get_popular_movies(page=page)
            if not movies:
                logger.warning("No results on page %d – stopping early.", page)
                break

            for movie in movies:
                if len(enriched) >= num_items:
                    break

                movie_id: int = movie["id"]
                try:
                    details = self.get_movie_details(movie_id)
                    credits = self.get_movie_credits(movie_id)
                except requests.RequestException:
                    logger.error("Skipping movie %d due to persistent API error.", movie_id)
                    continue

                record = self._build_record(details, credits)
                enriched.append(record)
                self._save_movie_json(movie_id, record)
                logger.info(
                    "Collected %d/%d – '%s'",
                    len(enriched), num_items, record.get("title", "?"),
                )

            page += 1

        # Save combined dataset
        combined_path = RAW_TMDB_DIR / "all_movies.json"
        with combined_path.open("w", encoding="utf-8") as fh:
            json.dump(enriched, fh, indent=2, ensure_ascii=False)
        logger.info(
            "Collection complete. %d movies saved → %s", len(enriched), combined_path
        )
        return enriched

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_record(details: Dict, credits: Dict) -> Dict:
        """
        Flatten and structure a movie record for storage.

        Extracts the required fields from raw API responses:
          - Title, release date, runtime
          - Genres (list of names)
          - Budget and revenue
          - TMDB rating and vote count
          - Top-5 cast members
          - Director (from crew)
          - Production companies (list of names)
          - Original language
          - IMDb ID (for cross-referencing with web scraper)

        Args:
            details: Response from get_movie_details().
            credits: Response from get_movie_credits().

        Returns:
            Structured dict ready for JSON serialisation.
        """
        genres = [g["name"] for g in details.get("genres", [])]
        production_companies = [
            pc["name"] for pc in details.get("production_companies", [])
        ]

        cast = credits.get("cast", [])
        top_5_cast = [
            {"name": c["name"], "character": c.get("character", ""), "order": c.get("order", i)}
            for i, c in enumerate(cast[:5])
        ]

        crew = credits.get("crew", [])
        director = next(
            (c["name"] for c in crew if c.get("job") == "Director"), None
        )

        return {
            # Identifiers
            "tmdb_id": details.get("id"),
            "imdb_id": details.get("imdb_id"),
            # Core fields
            "title": details.get("title"),
            "original_title": details.get("original_title"),
            "original_language": details.get("original_language"),
            "release_date": details.get("release_date"),
            "runtime": details.get("runtime"),
            "status": details.get("status"),
            "overview": details.get("overview"),
            # Classification
            "genres": genres,
            # Ratings
            "tmdb_rating": details.get("vote_average"),
            "tmdb_vote_count": details.get("vote_count"),
            "tmdb_popularity": details.get("popularity"),
            # Financial
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            # Cast & crew
            "top_5_cast": top_5_cast,
            "director": director,
            # Production
            "production_companies": production_companies,
            # Metadata
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _save_movie_json(movie_id: int, record: Dict) -> None:
        """
        Persist a single movie record to data/raw/tmdb/<movie_id>.json.

        Args:
            movie_id: TMDB movie ID (used as filename).
            record:   Structured movie dict from _build_record().
        """
        path = RAW_TMDB_DIR / f"{movie_id}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
        logger.debug("Saved → %s", path)


# ---------------------------------------------------------------------------
# Module-level convenience wrappers
# (satisfy the assignment's bare function signature requirement)
# ---------------------------------------------------------------------------

_collector: Optional[TMDBCollector] = None


def _get_collector() -> TMDBCollector:
    """Return (or lazily create) the module-level TMDBCollector instance."""
    global _collector
    if _collector is None:
        _collector = TMDBCollector()
    return _collector


def get_popular_movies(page: int = 1) -> List[Dict]:
    """
    Fetch one page of popular movies.

    Args:
        page: Page number (1-indexed).

    Returns:
        List of movie summary dicts.
    """
    return _get_collector().get_popular_movies(page=page)


def get_movie_details(movie_id: int) -> Dict:
    """
    Fetch full details for a single movie.

    Args:
        movie_id: TMDB movie ID.

    Returns:
        Movie detail dict.
    """
    return _get_collector().get_movie_details(movie_id)


def get_movie_credits(movie_id: int) -> Dict:
    """
    Fetch cast and crew for a movie.

    Args:
        movie_id: TMDB movie ID.

    Returns:
        Dict with 'cast' and 'crew' lists.
    """
    return _get_collector().get_movie_credits(movie_id)


def collect_all_data(num_items: int = 50) -> List[Dict]:
    """
    Collect popular movies with full details and credits.

    Args:
        num_items: Target number of movies to collect.

    Returns:
        List of enriched movie dicts.
    """
    return _get_collector().collect_all_data(num_items=num_items)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the collector from the command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect popular movie data from the TMDB API."
    )
    parser.add_argument(
        "--num-items", type=int, default=50,
        help="Number of movies to collect (default: 50)",
    )
    args = parser.parse_args()

    collector = TMDBCollector()
    movies = collector.collect_all_data(num_items=args.num_items)
    print(f"\n✅  Collected {len(movies)} movies.")

if __name__ == "__main__":
    main()
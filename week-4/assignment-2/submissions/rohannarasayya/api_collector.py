"""
api_collector.py
----------------
Collects movie data from the TMDB API for 50+ movies, making three API calls
per movie (details, credits, external IDs). Saves results as JSON files.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "api_collector.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("api_collector")

# ---------------------------------------------------------------------------
# TMDBCollector class
# ---------------------------------------------------------------------------

BASE_URL = "https://api.themoviedb.org/3"
MIN_REQUEST_INTERVAL = 0.25  # max 40 requests per 10 seconds
MAX_RETRIES = 3


class TMDBCollector:
    """Collects movie data from the TMDB API with rate limiting and retry logic."""

    def __init__(self) -> None:
        """Load API key from .env and initialise session."""
        load_dotenv()
        self.api_key: str = os.getenv("TMDB_API_KEY", "")
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in environment / .env file")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._last_request_time: float = 0.0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rate_limit(self) -> None:
        """Sleep if needed to stay within the 40-requests/10-second limit."""
        elapsed = time.time() - self._last_request_time
        wait = MIN_REQUEST_INTERVAL - elapsed
        if wait > 0:
            time.sleep(wait)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make an authenticated GET request with retry logic.

        Parameters
        ----------
        endpoint : str
            API path (relative to BASE_URL), e.g. '/movie/popular'.
        params : dict, optional
            Additional query parameters.

        Returns
        -------
        dict
            Parsed JSON response.

        Raises
        ------
        RuntimeError
            If all retries are exhausted.
        """
        url = f"{BASE_URL}{endpoint}"
        query: Dict = {"api_key": self.api_key}
        if params:
            query.update(params)

        for attempt in range(1, MAX_RETRIES + 1):
            self._rate_limit()
            try:
                logger.info("GET %s (attempt %d)", endpoint, attempt)
                response = self.session.get(url, params=query, timeout=10)
                self._last_request_time = time.time()
                if response.status_code == 200:
                    return response.json()
                logger.warning(
                    "Non-200 response %d for %s", response.status_code, endpoint
                )
            except requests.RequestException as exc:
                logger.warning("Request exception on attempt %d: %s", attempt, exc)
                self._last_request_time = time.time()

            if attempt < MAX_RETRIES:
                backoff = 2 ** (attempt - 1)  # 1s, 2s, 4s
                logger.info("Retrying in %ds…", backoff)
                time.sleep(backoff)

        raise RuntimeError(
            f"All {MAX_RETRIES} retries exhausted for endpoint {endpoint}"
        )

    # ------------------------------------------------------------------
    # Public data-fetching methods
    # ------------------------------------------------------------------

    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """
        Fetch one page of popular movies from TMDB.

        Parameters
        ----------
        page : int
            Page number (1-based).

        Returns
        -------
        list of dict
            Movie stub objects from the 'results' key.
        """
        data = self._make_request("/movie/popular", {"page": page})
        return data.get("results", [])

    def get_movie_details(self, movie_id: int) -> Dict:
        """
        Fetch full details for a single movie.

        Treats budget/revenue of 0 as None (TMDB uses 0 for unknown).

        Parameters
        ----------
        movie_id : int
            TMDB movie ID.

        Returns
        -------
        dict
            Movie details including title, release_date, runtime, genres, etc.
        """
        data = self._make_request(f"/movie/{movie_id}")
        # Treat 0 as unknown
        if data.get("budget") == 0:
            data["budget"] = None
        if data.get("revenue") == 0:
            data["revenue"] = None
        return data

    def get_movie_credits(self, movie_id: int) -> Dict:
        """
        Fetch cast and crew for a movie, returning top-5 cast and filtered crew.

        Cast entries contain 'name' and 'character'. Crew is filtered to
        Director and Producer roles only.

        Parameters
        ----------
        movie_id : int
            TMDB movie ID.

        Returns
        -------
        dict
            Keys: 'cast' (list of dicts), 'crew' (list of dicts).
        """
        data = self._make_request(f"/movie/{movie_id}/credits")
        cast = [
            {"name": m["name"], "character": m.get("character", "")}
            for m in data.get("cast", [])[:5]
        ]
        crew = [
            {"name": m["name"], "job": m.get("job", "")}
            for m in data.get("crew", [])
            if m.get("job") in ("Director", "Producer")
        ]
        return {"cast": cast, "crew": crew}

    def get_movie_external_ids(self, movie_id: int) -> Dict:
        """
        Fetch external IDs for a movie (IMDB, Wikidata, etc.).

        Parameters
        ----------
        movie_id : int
            TMDB movie ID.

        Returns
        -------
        dict
            External ID mapping; 'imdb_id' is the key join field.
        """
        return self._make_request(f"/movie/{movie_id}/external_ids")

    def collect_all_data(self, num_items: int = 100) -> List[Dict]:
        """
        Collect full data for at least *num_items* popular movies.

        For each movie, fetches details, credits, and external IDs, then
        merges them into a single dict. Saves each movie as
        data/raw/tmdb/{movie_id}.json and all movies as
        data/raw/tmdb/all_movies.json.

        Parameters
        ----------
        num_items : int
            Target number of movies to collect (some may be lost to
        deduplication or missing data after processing).

        Returns
        -------
        list of dict
            Combined movie records.
        """
        output_dir = Path("data/raw/tmdb")
        output_dir.mkdir(parents=True, exist_ok=True)

        all_movies: List[Dict] = []
        page = 1

        while len(all_movies) < num_items:
            logger.info(
                "Fetching popular movies page %d (%d collected so far)…",
                page,
                len(all_movies),
            )
            stubs = self.get_popular_movies(page=page)
            if not stubs:
                logger.warning("No results on page %d — stopping early.", page)
                break

            for stub in stubs:
                if len(all_movies) >= num_items:
                    break
                movie_id: int = stub["id"]
                try:
                    details = self.get_movie_details(movie_id)
                    credits = self.get_movie_credits(movie_id)
                    external_ids = self.get_movie_external_ids(movie_id)

                    combined: Dict = {
                        "tmdb_id": movie_id,
                        "title": details.get("title"),
                        "release_date": details.get("release_date"),
                        "runtime": details.get("runtime"),
                        "genres": details.get("genres", []),
                        "budget": details.get("budget"),
                        "revenue": details.get("revenue"),
                        "vote_average": details.get("vote_average"),
                        "vote_count": details.get("vote_count"),
                        "original_language": details.get("original_language"),
                        "production_companies": details.get("production_companies", []),
                        "overview": details.get("overview"),
                        "popularity": details.get("popularity"),
                        "cast": credits["cast"],
                        "crew": credits["crew"],
                        "imdb_id": external_ids.get("imdb_id"),
                    }

                    # Save individual movie file
                    movie_path = output_dir / f"{movie_id}.json"
                    try:
                        with open(movie_path, "w", encoding="utf-8") as f:
                            json.dump(combined, f, indent=2, ensure_ascii=False)
                    except OSError as exc:
                        logger.error("Failed to write %s: %s", movie_path, exc)

                    all_movies.append(combined)
                    logger.info("Collected movie %d: %s", movie_id, combined.get("title"))

                except RuntimeError as exc:
                    logger.error("Skipping movie %d: %s", movie_id, exc)

            page += 1

        # Save combined file
        all_movies_path = output_dir / "all_movies.json"
        try:
            with open(all_movies_path, "w", encoding="utf-8") as f:
                json.dump(all_movies, f, indent=2, ensure_ascii=False)
            logger.info(
                "Saved %d movies to %s", len(all_movies), all_movies_path
            )
        except OSError as exc:
            logger.error("Failed to write all_movies.json: %s", exc)

        return all_movies


# ---------------------------------------------------------------------------
# Module-level wrapper functions (required by spec)
# ---------------------------------------------------------------------------

_collector: Optional[TMDBCollector] = None


def _get_collector() -> TMDBCollector:
    """Return a module-level TMDBCollector, creating it on first call."""
    global _collector
    if _collector is None:
        _collector = TMDBCollector()
    return _collector


def get_popular_movies(page: int = 1) -> List[Dict]:
    """Module-level wrapper for TMDBCollector.get_popular_movies."""
    return _get_collector().get_popular_movies(page)


def get_movie_details(movie_id: int) -> Dict:
    """Module-level wrapper for TMDBCollector.get_movie_details."""
    return _get_collector().get_movie_details(movie_id)


def get_movie_credits(movie_id: int) -> Dict:
    """Module-level wrapper for TMDBCollector.get_movie_credits."""
    return _get_collector().get_movie_credits(movie_id)


def get_movie_external_ids(movie_id: int) -> Dict:
    """Module-level wrapper for TMDBCollector.get_movie_external_ids."""
    return _get_collector().get_movie_external_ids(movie_id)


def collect_all_data(num_items: int = 100) -> List[Dict]:
    """Module-level wrapper for TMDBCollector.collect_all_data."""
    return _get_collector().collect_all_data(num_items)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    movies = collect_all_data(num_items=100)
    print(f"Collected {len(movies)} movies.")

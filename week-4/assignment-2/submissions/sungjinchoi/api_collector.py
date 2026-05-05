import os
import json
import time
import logging
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/api_collector.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class TMDBCollector:
    """Collects movie data from the TMDB API."""

    BASE = "https://api.themoviedb.org/3"
    INTERVAL = 0.25  # 40 req per 10 seconds

    def __init__(self) -> None:
        """Load API key and set up session."""
        key = os.environ.get("TMDB_API_KEY", "")
        if not key:
            raise SystemExit("ERROR: TMDB_API_KEY not set in .env")
        self.key = key
        self.session = requests.Session()
        self._last = 0.0

    def _get(self, path: str, params: Dict | None = None) -> Dict:
        """Make a rate-limited GET request with retry logic."""
        elapsed = time.time() - self._last
        if elapsed < self.INTERVAL:
            time.sleep(self.INTERVAL - elapsed)
        self._last = time.time()

        p = dict(params or {}, api_key=self.key)
        for attempt in range(3):
            try:
                r = self.session.get(f"{self.BASE}/{path}", params=p, timeout=10)
                r.raise_for_status()
                logging.info("GET %s", path)
                return r.json()
            except requests.RequestException as e:
                logging.warning("attempt %d failed for %s: %s", attempt + 1, path, e)
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        return {}

    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Return one page of popular movies."""
        return self._get("movie/popular", {"page": page}).get("results", [])

    def get_movie_details(self, movie_id: int) -> Dict:
        """Return detailed metadata for a movie."""
        return self._get(f"movie/{movie_id}")

    def get_movie_credits(self, movie_id: int) -> Dict:
        """Return cast and crew for a movie."""
        return self._get(f"movie/{movie_id}/credits")

    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        """Collect details and credits for num_items popular movies."""
        movies: List[Dict] = []
        page = 1
        while len(movies) < num_items:
            batch = self.get_popular_movies(page)
            if not batch:
                break
            movies.extend(batch)
            page += 1

        results = []
        for m in movies[:num_items]:
            try:
                details = self.get_movie_details(m["id"])
                credits = self.get_movie_credits(m["id"])
                details["cast"] = credits.get("cast", [])[:5]
                details["crew"] = credits.get("crew", [])[:5]
                results.append(details)
                logging.info("collected %s (id=%d)", details.get("title"), m["id"])
            except requests.RequestException as e:
                logging.error("failed id=%d: %s", m["id"], e)

        return results


def main() -> None:
    os.makedirs("data/raw/tmdb", exist_ok=True)
    collector = TMDBCollector()
    print("Collecting TMDB data...")
    data = collector.collect_all_data(50)
    out = "data/raw/tmdb/movies.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} movies to {out}")


if __name__ == "__main__":
    main()

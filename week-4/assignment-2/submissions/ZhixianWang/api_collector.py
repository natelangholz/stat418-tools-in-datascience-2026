import json
import logging
import os
import time
from typing import Dict, List, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="logs/api_collector.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TMDBCollector:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in environment")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._last_request_time = 0.0
        self._min_interval = 0.25  # 4 req/s, well within 40/10s limit

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _make_request(
        self, endpoint: str, params: Dict = None, retries: int = 3
    ) -> Dict:
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"
        p = {"api_key": self.api_key, **(params or {})}

        for attempt in range(1, retries + 1):
            try:
                resp = self.session.get(url, params=p, timeout=10)
                resp.raise_for_status()
                logger.info("GET %s -> 200", endpoint)
                return resp.json()
            except requests.HTTPError as e:
                status = e.response.status_code if e.response else None
                if status == 429:
                    wait = 10 * attempt
                    logger.warning("Rate limited on %s, waiting %ds", endpoint, wait)
                    time.sleep(wait)
                elif attempt == retries:
                    logger.error("Failed %s after %d attempts: %s", endpoint, retries, e)
                    raise
                else:
                    time.sleep(2 ** attempt)
            except requests.RequestException as e:
                if attempt == retries:
                    logger.error("Request error %s: %s", endpoint, e)
                    raise
                time.sleep(2 ** attempt)
        return {}

    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        data = self._make_request("movie/popular", {"page": page})
        return data.get("results", [])

    def get_movie_details(self, movie_id: int) -> Dict:
        return self._make_request(f"movie/{movie_id}")

    def get_movie_credits(self, movie_id: int) -> Dict:
        return self._make_request(f"movie/{movie_id}/credits")

    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        movies = []
        page = 1
        while len(movies) < num_items:
            batch = self.get_popular_movies(page)
            if not batch:
                break
            movies.extend(batch)
            page += 1

        movies = movies[:num_items]
        enriched = []

        for movie in movies:
            movie_id = movie["id"]
            try:
                details = self.get_movie_details(movie_id)
                credits = self.get_movie_credits(movie_id)

                top_cast = [
                    {"name": m["name"], "character": m.get("character", "")}
                    for m in credits.get("cast", [])[:5]
                ]
                top_crew = [
                    {"name": m["name"], "job": m.get("job", "")}
                    for m in credits.get("crew", [])
                    if m.get("job") in ("Director", "Producer", "Screenplay")
                ][:5]

                record = {
                    "tmdb_id": details.get("id"),
                    "imdb_id": details.get("imdb_id"),
                    "title": details.get("title"),
                    "release_date": details.get("release_date"),
                    "runtime": details.get("runtime"),
                    "genres": [g["name"] for g in details.get("genres", [])],
                    "budget": details.get("budget"),
                    "revenue": details.get("revenue"),
                    "tmdb_rating": details.get("vote_average"),
                    "tmdb_vote_count": details.get("vote_count"),
                    "production_companies": [
                        c["name"] for c in details.get("production_companies", [])
                    ],
                    "original_language": details.get("original_language"),
                    "overview": details.get("overview"),
                    "cast": top_cast,
                    "crew": top_crew,
                }
                enriched.append(record)
                logger.info("Collected: %s (id=%s)", record["title"], movie_id)
            except Exception as e:
                logger.error("Skipping movie %s: %s", movie_id, e)

        return enriched


def save_raw_data(data: List[Dict], output_dir: str = "data/raw/tmdb") -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "movies.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d records to %s", len(data), path)
    print(f"Saved {len(data)} records to {path}")


def main() -> Tuple[List[Dict], str]:
    os.makedirs("logs", exist_ok=True)
    collector = TMDBCollector()
    print("Collecting TMDB data for 50 movies...")
    data = collector.collect_all_data(num_items=50)
    save_raw_data(data)
    return data, "data/raw/tmdb/movies.json"


if __name__ == "__main__":
    main()

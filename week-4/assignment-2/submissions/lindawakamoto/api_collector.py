import requests
import os
import time
from typing import Dict, List
from dotenv import load_dotenv
import logging
import json

load_dotenv()


class TMDBCollector:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 4 requests per second max
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data/raw/tmdb", exist_ok=True)

        logging.basicConfig(
            filename='logs/api_collector.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

# Uses error handling + retry loop
    def _make_request(self, endpoint: str, params: Dict = None, retries: int = 3) -> Dict:
        if params is None:
            params = {}

        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(retries):
            try:
                self._rate_limit()
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()

                logging.info(f"Successfully fetched {endpoint}")
                return response.json()

            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed for {endpoint}: {e}")

                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise
        raise RuntimeError("Unreachable: request retry loop exited unexpectedly")

    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        data = self._make_request('movie/popular', {'page': page})
        return data.get('results', [])

    def get_movie_details(self, movie_id: int) -> Dict:
        return self._make_request(f'movie/{movie_id}')

    def get_movie_credits(self, movie_id: int) -> Dict:
        return self._make_request(f"movie/{movie_id}/credits")

    def _build_clean_item(self, mid: int, details: Dict, credits: Dict) -> Dict:
        return {
            "tmdb_id": mid,
            "title": details.get("title"),
            "release_date": details.get("release_date"),
            "runtime": details.get("runtime"),
            "genres": [g["name"] for g in details.get("genres", [])],
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "rating": details.get("vote_average"),
            "vote_count": details.get("vote_count"),
            "language": details.get("original_language"),
            "production_companies": [
                c["name"] for c in details.get("production_companies", [])
            ][:5],
            "cast": [c["name"] for c in credits.get("cast", [])][:5],
            "crew": [c["name"] for c in credits.get("crew", [])][:5],
            "imdb_id": details.get("imdb_id"),
        }

    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        if num_items < 50:
            logging.warning(f"Requested {num_items}, but minimum is 50. Setting num_items=50.")
            num_items = 50

        results = []
        page = 1

        while len(results) < num_items:
            movies = self.get_popular_movies(page)

            if not movies:
                break

            for m in movies:
                if len(results) >= num_items:
                    break

                mid = m["id"]

                try:
                    details = self.get_movie_details(mid)
                    credits = self.get_movie_credits(mid)

                    # Get just specified details of each movie (for analysis)
                    clean_item = self._build_clean_item(mid, details, credits)
                    results.append(clean_item)

                    # # Also save the raw JSON file
                    # raw_path = f"data/raw/tmdb/raw/{mid}.json"
                    # with open(raw_path, "w", encoding="utf-8") as f:
                    #     json.dump({"details": details, "credits": credits}, f, indent=2)

                    # Save clean analysis-ready JSON
                    with open(f"data/raw/tmdb/{mid}.json", "w", encoding="utf-8") as f:
                        json.dump(clean_item, f, indent=2)

                except Exception as e:
                    logging.error(f"Failed movie {mid}: {e}")
                    continue

            page += 1

        if len(results) < 50:
            logging.error(f"Only collected {len(results)} movies (minimum required: 50)")
            raise ValueError(f"Insufficient data: only {len(results)} movies collected (need at least 50).")

        return results

# Run
if __name__ == "__main__":
    collector = TMDBCollector()
    data = collector.collect_all_data(50)

    print(f"Collected {len(data)} items")
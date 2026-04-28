import requests
import os
import time
import json
from typing import Dict, List
from dotenv import load_dotenv
import logging
from collections import deque

load_dotenv()

class TMDBCollector:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()

        # Rate limiting: 40 requests per 10 seconds
        self.request_times = deque()
        self.rate_limit = 40
        self.window_size = 10  # seconds

        # Logging
        os.makedirs("logs", exist_ok=True)
        logging.basicConfig(
            filename='logs/api_collector.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _rate_limit(self):
        """Sliding window rate limiter"""
        now = time.time()

        # Remove old timestamps
        while self.request_times and now - self.request_times[0] > self.window_size:
            self.request_times.popleft()

        if len(self.request_times) >= self.rate_limit:
            sleep_time = self.window_size - (now - self.request_times[0])
            time.sleep(sleep_time)

        self.request_times.append(time.time())

    def _make_request(self, endpoint: str, params: Dict = None, retries=3) -> Dict:
        """Make API request with retry + logging"""
        self._rate_limit()

        if params is None:
            params = {}

        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=10)

                logging.info(f"REQUEST: {response.url}")

                if response.status_code == 429:
                    # Rate limit hit → backoff
                    wait = 2 ** attempt
                    logging.warning(f"Rate limited. Sleeping {wait}s")
                    time.sleep(wait)
                    continue

                response.raise_for_status()

                return response.json()

            except requests.RequestException as e:
                logging.error(f"Error on {endpoint}: {e}")

                if attempt == retries - 1:
                    raise

                time.sleep(2 ** attempt)

    def _save_json(self, data: Dict, filename: str):
        os.makedirs("data/raw/tmdb", exist_ok=True)
        with open(f"data/raw/tmdb/{filename}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_movie_details(self, movie_id: int) -> Dict:
        """Fetch movie details only"""
        return self._make_request(f'movie/{movie_id}')

    def get_movie_credits(self, movie_id: int) -> Dict:
        """Fetch movie credits only"""
        return self._make_request(f'movie/{movie_id}/credits')

    def collect_full_movie_data(self, pages: int = 5):
        """Pipeline: popular → details → credits → save all in one file (20 movies per page)"""
        all_movies = []
        for page in range(1, pages + 1):
            logging.info(f"Fetching popular movies page {page}/{pages}")
            page_results = self._make_request('movie/popular', {'page': page}).get('results', [])
            all_movies.extend(page_results)

        results = []

        for movie in all_movies:
            movie_id = movie['id']

            details = self.get_movie_details(movie_id)
            credits = self.get_movie_credits(movie_id)

            results.append({
                "movie_id": movie_id,
                "title": movie.get("title"),
                "details": details,
                "credits": credits
            })

        self._save_json(
            {
                "pages_collected": pages,
                "total_movies": len(results),
                "movies": results
            },
            "tmdb_movies_data"
        )

        return results

if __name__ == "__main__":
    collector = TMDBCollector()

    print("Fetching data (5 pages = ~100 movies)...")
    data = collector.collect_full_movie_data(pages=5)

    print(f"Collected {len(data)} movies")
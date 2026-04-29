import requests
import os
import time
import json
import logging
from collections import deque
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename='stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs/api_collector.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TMDBCollector:
    RATE_LIMIT_REQUESTS = 40
    RATE_LIMIT_WINDOW = 10  # seconds

    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not set in environment")
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self._request_timestamps: deque = deque()
        os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw', exist_ok=True)
        os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs', exist_ok=True)

    # ------------------------------------------------------------------
    # Rate limiting: sliding window of 40 requests per 10 seconds
    # ------------------------------------------------------------------

    def _rate_limit(self):
        now = time.time()
        # Drop timestamps older than the window
        while self._request_timestamps and now - self._request_timestamps[0] >= self.RATE_LIMIT_WINDOW:
            self._request_timestamps.popleft()

        if len(self._request_timestamps) >= self.RATE_LIMIT_REQUESTS:
            sleep_for = self.RATE_LIMIT_WINDOW - (now - self._request_timestamps[0])
            if sleep_for > 0:
                logger.info(f"Rate limit reached — sleeping {sleep_for:.2f}s")
                time.sleep(sleep_for)

        self._request_timestamps.append(time.time())

    # ------------------------------------------------------------------
    # Core request with retry logic
    # ------------------------------------------------------------------

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        retries: int = 3,
        backoff: float = 2.0,
    ) -> Dict:
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(1, retries + 1):
            self._rate_limit()
            logger.info(f"REQUEST {endpoint} (attempt {attempt})")
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                logger.info(f"OK {endpoint} — status {response.status_code}")
                return response.json()
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else 'N/A'
                logger.error(f"HTTP {status} on {endpoint}: {e}")
                if status == 429 or (isinstance(status, int) and status >= 500):
                    if attempt < retries:
                        wait = backoff ** attempt
                        logger.info(f"Retrying in {wait}s...")
                        time.sleep(wait)
                        continue
                raise
            except requests.RequestException as e:
                logger.error(f"Request error on {endpoint}: {e}")
                if attempt < retries:
                    wait = backoff ** attempt
                    logger.info(f"Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                raise

        raise RuntimeError(f"All {retries} attempts failed for {endpoint}")

    # ------------------------------------------------------------------
    # Save helpers
    # ------------------------------------------------------------------

    def _save(self, data: Dict | List, filename: str):
        path = os.path.join('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw', filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {path}")

    # ------------------------------------------------------------------
    # Movies
    # ------------------------------------------------------------------

    def get_popular_movies(self, pages: int = 1) -> List[Dict]:
        results = []
        for page in range(1, pages + 1):
            data = self._make_request('movie/popular', {'page': page})
            results.extend(data.get('results', []))
        self._save(results, 'popular_movies.json')
        return results

    def get_movie_details(self, movie_id: int) -> Dict:
        data = self._make_request(f'movie/{movie_id}')
        self._save(data, f'movie_{movie_id}_details.json')
        return data

    def get_movie_credits(self, movie_id: int) -> Dict:
        data = self._make_request(f'movie/{movie_id}/credits')
        self._save(data, f'movie_{movie_id}_credits.json')
        return data

    # ------------------------------------------------------------------
    # TV shows
    # ------------------------------------------------------------------

    def get_popular_shows(self, pages: int = 1) -> List[Dict]:
        results = []
        for page in range(1, pages + 1):
            data = self._make_request('tv/popular', {'page': page})
            results.extend(data.get('results', []))
        self._save(results, 'popular_shows.json')
        return results

    def get_show_details(self, show_id: int) -> Dict:
        data = self._make_request(f'tv/{show_id}')
        self._save(data, f'show_{show_id}_details.json')
        return data

    def get_show_credits(self, show_id: int) -> Dict:
        data = self._make_request(f'tv/{show_id}/credits')
        self._save(data, f'show_{show_id}_credits.json')
        return data

    # ------------------------------------------------------------------
    # Bulk collection
    # ------------------------------------------------------------------

    def collect_movies(self, pages: int = 1) -> List[Dict]:
        movies = self.get_popular_movies(pages=pages)
        collected = []
        for movie in movies:
            mid = movie['id']
            details = self.get_movie_details(mid)
            credits = self.get_movie_credits(mid)
            collected.append({'details': details, 'credits': credits})
        self._save(collected, 'movies_full.json')
        return collected

    def collect_shows(self, pages: int = 1) -> List[Dict]:
        shows = self.get_popular_shows(pages=pages)
        collected = []
        for show in shows:
            sid = show['id']
            details = self.get_show_details(sid)
            credits = self.get_show_credits(sid)
            collected.append({'details': details, 'credits': credits})
        self._save(collected, 'shows_full.json')
        return collected


if __name__ == '__main__':
    collector = TMDBCollector()
    collector.collect_movies(pages=3)
    collector.collect_shows(pages=3)

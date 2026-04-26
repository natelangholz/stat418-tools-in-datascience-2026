import requests
import os
import time
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/api_collector.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TMDBCollector:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found. Create a .env file with your API key.")
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.25

    def _rate_limit(self):
        """Ensure requests stay within TMDB rate limit of 40/10s."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a rate-limited GET request with up to 3 retries."""
        self._rate_limit()
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        for attempt in range(3):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                logging.info(f"OK {endpoint}")
                return response.json()
            except requests.RequestException as e:
                logging.error(f"Attempt {attempt+1} failed for {endpoint}: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Fetch one page of popular movies from TMDB."""
        data = self._make_request('movie/popular', {'page': page})
        return data.get('results', [])

    def get_movie_details(self, movie_id: int) -> Dict:
        """Fetch full details for a single movie by TMDB ID."""
        return self._make_request(f'movie/{movie_id}')

    def get_movie_credits(self, movie_id: int) -> Dict:
        """Fetch cast and crew for a single movie by TMDB ID."""
        return self._make_request(f'movie/{movie_id}/credits')

    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        """Collect detailed data for num_items popular movies including credits."""
        movies = []
        page = 1
        while len(movies) < num_items:
            results = self.get_popular_movies(page)
            if not results:
                break
            movies.extend(results)
            page += 1

        movies = movies[:num_items]
        collected = []

        for i, movie in enumerate(movies):
            movie_id = movie['id']
            print(f"[{i+1}/{num_items}] Fetching: {movie['title']}")
            try:
                details = self.get_movie_details(movie_id)
                credits = self.get_movie_credits(movie_id)
                cast = [c['name'] for c in credits.get('cast', [])[:5]]
                crew = credits.get('crew', [])
                directors = [c['name'] for c in crew if c['job'] == 'Director']

                collected.append({
                    'id': details['id'],
                    'title': details['title'],
                    'release_date': details.get('release_date', ''),
                    'runtime': details.get('runtime'),
                    'genres': [g['name'] for g in details.get('genres', [])],
                    'budget': details.get('budget'),
                    'revenue': details.get('revenue'),
                    'tmdb_rating': details.get('vote_average'),
                    'tmdb_vote_count': details.get('vote_count'),
                    'cast': cast,
                    'directors': directors,
                    'production_companies': [c['name'] for c in details.get('production_companies', [])],
                    'original_language': details.get('original_language'),
                })
            except Exception as e:
                logging.error(f"Failed to collect {movie['title']}: {e}")

        os.makedirs('data/raw/tmdb', exist_ok=True)
        with open('data/raw/tmdb/movies.json', 'w') as f:
            json.dump(collected, f, indent=2)
        print(f"Saved {len(collected)} movies to data/raw/tmdb/movies.json")
        return collected


if __name__ == '__main__':
    collector = TMDBCollector()
    data = collector.collect_all_data(num_items=50)
    print(f"Done. Collected {len(data)} movies.")

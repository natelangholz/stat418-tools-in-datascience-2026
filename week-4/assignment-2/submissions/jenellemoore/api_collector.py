import requests
import os
import time
import json
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
import logging

load_dotenv()

class TMDBCollector:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 4 requests per second max

        Path("logs").mkdir(exist_ok=True)
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        
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
    
    def _make_request(self, endpoint: str, params: Dict = None, retries:int=3) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully fetched {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching {endpoint}: {e}")
            if retries > 0:
                logging.info(f"Retrying {endpoint}. Retries left: {retries}")
                time.sleep(3)
                return self._make_request(endpoint, params, retries - 1)
        
            raise
            
    
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Get popular movies"""
        data = self._make_request('movie/popular', {'page': page})
        return data.get('results', [])
    
    def get_top_rated_movies(self, page: int = 1) -> List[Dict]:
        data = self._make_request("movie/top_rated", {"page": page})
        return data.get("results", [])
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed movie information"""
        return self._make_request(f'movie/{movie_id}')
    
    def get_movie_credits(self, movie_id: int) -> Dict:
        """Get movie credit information"""
        return self._make_request(f'movie/{movie_id}/credits')
    
    def save_json(self, data: Dict, filename: str):
        file_path = Path("data/raw") / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logging.info(f"Saved file: {file_path}")

    def collect_all_data(self, num_items: int = 100) -> List[Dict]:
        """Collect popular/top movies"""
        all_data = []
        letterboxd_movies = []
        seen_movie_ids = []

        movie_page = 1

        while len(all_data) < num_items:
            popular_movies = self.get_popular_movies(page=movie_page)
            top_rated_movies = self.get_top_rated_movies(page=movie_page)

            movies = popular_movies + top_rated_movies

            for movie in movies:
                if len(all_data) >= num_items:
                    break

                movie_id = movie["id"]
                if movie_id in seen_movie_ids:
                    continue

                seen_movie_ids.append(movie_id)

                details = self.get_movie_details(movie_id)
                credits = self.get_movie_credits(movie_id)

                top_cast = credits.get("cast", [])[:5]
                top_crew = credits.get("crew", [])[:5]

                clean_movie_data = {
                    "title": details.get("title"),
                    "release_date": details.get("release_date"),
                    "runtime": details.get("runtime"),
                    "genres": [
                        genre.get("name")
                        for genre in details.get("genres", [])
                    ],
                    "budget": details.get("budget"),
                    "revenue": details.get("revenue"),
                    "tmdb_rating": details.get("vote_average"),
                    "tmdb_vote_count": details.get("vote_count"),
                    "cast_top_5": [
                        {
                            "name": actor.get("name"),
                            "character": actor.get("character")
                        }
                        for actor in top_cast
                    ],
                    "crew_top_5": [
                        {
                            "name": person.get("name"),
                            "job": person.get("job")
                        }
                        for person in top_crew
                    ],
                    "production_companies": [
                        company.get("name")
                        for company in details.get("production_companies", [])
                    ],
                    "original_language": details.get("original_language")
                }

                combined_data = {
                    "type": "movie",
                    "clean_data": clean_movie_data,
                    "popular_summary": movie,
                    "details": details,
                    "credits": credits
                }

                self.save_json(combined_data, f"movie_{movie_id}.json")
                all_data.append(combined_data)

                #movie list for part 2
                letterboxd_movies.append({
                    "title": details.get("title"),
                    "year": details.get("release_date", "")[:4]
                })

            movie_page += 1

        self.save_json(letterboxd_movies, "letterboxd_movies.json")

        return all_data

if __name__ == "__main__":
    collector = TMDBCollector()
    data = collector.collect_all_data(num_items=100)
    print(f"Collected data for {len(data)} movies.")

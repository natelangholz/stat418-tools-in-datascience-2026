
'''
api-collector.py - API integration

1. Authenticates with TMDB API
2. Fetches popular movies/shows
3. Gets detailed information for each item
4. Retrieves cast and crew data
5. Implements rate limiting (40 requests per 10 seconds for TMDB)
6. Handles API errors with retry logic
7. Saves raw API responses to JSON files
8. Logs all API calls with timestamps

Key Functions:
def get_popular_movies(page: int = 1) -> List[Dict]
def get_movie_details(movie_id: int) -> Dict
def get_movie_credits(movie_id: int) -> Dict
def collect_all_data(num_items: int = 50) -> List[Dict]
'''

import requests
import os
import time
from typing import Dict,List
from dotenv import load_dotenv
import logging
import json

load_dotenv()

class TMDBCollector():
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self.last_request_time = 0
        self.main_request_interval = 0.25 # 4 requests per second
        
        os.makedirs('logs', exist_ok=True)
        os.makedirs(os.path.join('data', 'raw', 'tmdb'), exist_ok=True)

        logging.basicConfig(
            filename=os.path.join('logs', 'api_collector.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    def _rate_limit(self):
        """Ensure rate limits are not exceeded"""
        elapsed = time.time() - self.last_request_time # time between current and last request time 
        if elapsed < self.main_request_interval: # if the elapsed time is less than the main request interval (4 requests/sec)
            time.sleep(self.main_request_interval - elapsed) # sleep for the rest of the time until the main request interval time
        self.last_request_time = time.time() # set the last request time to now
    
    def _make_request(self, endpoint: str, params: Dict = None, max_retries: int = 3) -> Dict:
        """Make API request with error handling"""
        self._rate_limit() 

        if params is None:
            params = {}
        params['api_key'] = self.api_key

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status() # checks HTTP status code of a response and raises HTTPError if the status is 4xx or 5xx
                logging.info(f"Successfully fetched {endpoint}") # log info message to logger
                return response.json() 
            except requests.RequestException as e:
                logging.error(f"Error fetching {endpoint}: {e}") # logs the error message
                if attempt < max_retries - 1:
                    time.sleep(2**attempt) #1s, then 2s before final attempt
                else:
                    raise # interrupts program flow to signal error 
    
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Get popular movies"""
        data = self._make_request('movie/popular', {'page': page}) 
        
        # get 'results' key (instead of data['results'] to prevent program from crashing with KeyError)
        # default value of [] if 'results' key
        return data.get('results',[]) 
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed movie information"""
        return self._make_request(f'movie/{movie_id}')
    
    def get_movie_credits(self, movie_id: int) -> Dict:
        """Get movie cast and crew information"""
        return self._make_request(f'movie/{movie_id}/credits')
    
    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        """Collect detailed information and credits for popular movies"""
        movies = []
        page_count = 1

        while len(movies) < num_items:
            popular_movies = self.get_popular_movies(page=page_count)

            if not popular_movies: # break if no popular movies collected 
                break

            for movie in popular_movies:
                if len(movies) >= num_items:
                    break # stop collecting when meet num_items limit

                movie_id = movie.get('id')
                if movie_id is None:
                    continue # stops executing and returns to top of loop if no movie id is collected

                try:
                    movie_details = self.get_movie_details(movie_id=movie_id)
                    movie_creds = self.get_movie_credits(movie_id=movie_id)

                    movie_data = {
                        'name': movie,
                        'details': movie_details,
                        'credits': movie_creds
                    }

                    movies.append(movie_data)
                    logging.info(f'Collected all data for movie ID {movie_id}')

                except requests.RequestException as e:
                    logging.error(f'Error collecting data for movie ID: {movie_id}: {e}')
                    continue

            page_count += 1

        #Save data to JSON file
        filepath = os.path.join('data', 'raw', 'tmdb', 'tmdb_movie_data.json')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(movies, f, indent=4)
            logging.info(f'Saved scraped data to {filepath}')
        except Exception as e:
            logging.error(f'Error saving data to JSON: {e}')  

        return movies

if __name__ == '__main__':                                                                                                                                                                      
    TMDBCollector().collect_all_data(num_items=100)


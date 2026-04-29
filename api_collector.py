import requests
import os
import time
import json
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
        
        logging.basicConfig(
            filename='logs/api_collector.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    # part 5: implements rate limiting (4 requests per second max)
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None, save: bool = False) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        # part 1: authenticates with TMDB API
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}" 
        
        #try:
         #   response = self.session.get(url, params=params, timeout=10)
          #  response.raise_for_status()
           # logging.info(f"Successfully fetched {endpoint}")
            #return response.json()
        #except requests.RequestException as e:
         #   logging.error(f"Error fetching {endpoint}: {e}")
          #  raise
        # part 6: handle api errors with retry logic
        max_retry = 3
        backoff = 1
        for attempt in range(1, max_retry + 1):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # part 7: Saves raw API responses to JSON files if specified
                if save:
                    os.makedirs('data/raw/tmdb', exist_ok=True)
                    with open(f'data/raw/tmdb/{endpoint}.json', 'w') as f:
                        json.dump(data, f)
                # part 8: log api calls with timestamps(success)
                logging.info(f"Successfully fetched {endpoint}")
                return data
            except requests.RequestException as e:
                # part 8: log api calls with timestamps(errors)
                logging.error(f"Error fetching {endpoint} (attempt {attempt + 1}): {e}")
                if attempt < max_retry:
                    time.sleep(backoff * (2 ** (attempt - 1)))  # Exponential backoff
                else:
                    raise
    
    # part 2: fetches popular movies/shows
    def get_popular_media(self, page: int = 1) -> List[Dict]:
        """Get popular movies/shows"""
        movies = self._make_request('movie/popular', {'page': page})
        tv = self._make_request('tv/popular', {'page': page})
        return {'movies': movies.get('results', []),
                'tv': tv.get('results', [])}
    # part 3: gets detailed information about each item
    def get_media_details(self, media_id: int, media_type: str) -> Dict:
        """Get detailed movie/show information"""
        if media_type not in {"movie", "tv"}:
            raise ValueError("media type must be 'movie' or 'tv'")
        return self._make_request(f'{media_type}/{media_id}')
    # part 4: retrieves cast and crew data
    def get_media_credits(self, media_id: int, media_type: str) -> Dict:
        """Get cast and crew information"""
        if media_type not in {"movie", "tv"}:
            raise ValueError("media type must be 'movie' or 'tv'")
        return self._make_request(f'{media_type}/{media_id}/credits')
    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        """Collect data for popular movies and shows"""
        # collector = TMDBCollector()
        all_data = []
        
        # Fetch popular media
        popular_media = collector.get_popular_media(page=1)
        media_items = popular_media['movies'] + popular_media['tv']
        
        for item in media_items[:num_items]:
            media_type = 'movie' if 'title' in item else 'tv'
            media_id = item['id']
            
            # Get details and credits
            details = collector.get_media_details(media_id, media_type)
            credits = collector.get_media_credits(media_id, media_type)
            
            all_data.append({
                'id': media_id,
                'type': media_type,
                'details': details,
                'credits': credits
            })
        
        return all_data
    
    def collect_movie_data(self, num_items: int = 50) -> List[Dict]:
        """Collect data for popular movies"""
        all_data = []
        page = 1

        while len(all_data) < num_items: # first page might not have enough movies
            popular_movies = self._make_request('movie/popular', {'page': page})
            movie_items = popular_movies.get('results', [])

            if not movie_items: # out of pages
                break 

            for item in movie_items:
                if len(all_data) >= num_items: # have enough data
                    break

                media_id = item['id']
                details = self.get_media_details(media_id, 'movie')
                credits = self.get_media_credits(media_id, 'movie')

                all_data.append({
                    'id': media_id,
                    'type': 'movie',
                    'details': details,
                    'credits': credits
                })
            page += 1
        
        return all_data

    


collector = TMDBCollector()
num_media = 50
popular_media = collector.collect_movie_data(num_media)


"""
# test collector

collector = TMDBCollector()
num_media = 50
popular_media = collector.collect_all_data(num_media)
tv = []
for i in popular_media:
    if i['type'] == 'tv':
        tv.append(i)
print(tv[0])
print(popular_media)
print(popular_media['movies'][:1])
print()
print(popular_media['tv'][:1])
print()
print()
popular_movie_details = collector.get_media_details(media_id=popular_media['movies'][0]['id'], media_type='movie')
popular_show_details = collector.get_media_details(media_id=popular_media['tv'][0]['id'], media_type='tv')
print(popular_movie_details)   
print()
print(popular_show_details)
print()
print()
popular_movie_credits = collector.get_media_credits(media_id=popular_media['movies'][0]['id'], media_type='movie')
popular_show_credits = collector.get_media_credits(media_id=popular_media['tv'][0]['id'], media_type='tv')
print(popular_movie_credits)
print()
print(popular_show_credits)
"""




# get data
tmdb_data = []
letterboxd_movies = []
for media in popular_media:
    if media['type'] == 'movie':
        title = media['details']['title']
        release_date = media['details']['release_date']
        release_year = int(media['details']['release_date'][:4])
        runtime = media['details']['runtime']
        genres = []
        for i in range(len(media['details']['genres'])):
            genres.append(media['details']['genres'][i]['name'])
        budget = media['details']['budget']
        revenue = media['details']['revenue']
        vote_average = media['details']['vote_average']
        vote_count = media['details']['vote_count']
        imdb_id = media['details']['imdb_id']
        production_companies = media['details']['production_companies']
        original_language = media['details']['original_language']
        top5_cast = []
        for i in range(min(5, len(media['credits']['cast']))):
            top5_cast.append(media['credits']['cast'][i])
        top5_crew = []
        for i in range(min(5, len(media['credits']['crew']))):
            top5_crew.append(media['credits']['crew'][i])
    else:
        title = media['details']['title']
        release_date = media['details']['first_air_date']
        release_year = int(media['details']['first_air_date'][:4])
        runtime = media['details']['episode_run_time']
        genres = []
        for i in range(len(media['details']['genres'])):
            genres.append(media['details']['genres'][i]['name'])
        budget = None
        revenue = None
        vote_average = media['details']['vote_average']
        vote_count = media['details']['vote_count']
        imdb_id = None
        production_companies = media['details']['production_companies']
        original_language = media['details']['original_language']
        top5_cast = []
        for i in range(min(5, len(media['credits']['cast']))):
            top5_cast.append(media['credits']['cast'][i])
        top5_crew = []
        for i in range(min(5, len(media['credits']['crew']))):
            top5_crew.append(media['credits']['crew'][i])
    data = {
        'id': media['id'],
        'type': media['type'],
        'title': title,
        'release_date': release_date,
        'release_year': release_year,
        'runtime': runtime,
        'genres': genres,
        'budget': budget,
        'revenue': revenue,
        'vote_average': vote_average,
        'vote_count': vote_count,
        'imdb_id': imdb_id,
        'production_companies': production_companies,
        'original_language': original_language,
        'top5_cast': top5_cast,
        'top5_crew': top5_crew
    }
    searches = {
        'id': media['id'],
        'title': title,
        'release_year': release_year,
    }
    tmdb_data.append(data)
    letterboxd_movies.append(searches)


# save data to json
os.makedirs("data/raw/tmdb", exist_ok=True)

with open("data/raw/tmdb/media_data.json", "w", encoding="utf-8") as f:
    json.dump(tmdb_data, f, indent=2, ensure_ascii=False)

with open("data/raw/tmdb/scraper_movies.json", "w", encoding="utf-8") as f:
    json.dump(letterboxd_movies, f, indent=2, ensure_ascii=False)



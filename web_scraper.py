import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, Optional, List
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import os
import json
import random

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        # part 4: uses appropriate User-Agent header
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' # changed because the original User-Agent was part of the blocked
        })
        self.last_request_time = 0
        self.min_request_interval = 2  # 2 seconds minimum between requests
        
        logging.basicConfig(
            filename='logs/web_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        path = urlparse(url).path

        # allow film pages because /film individual pages are not blocked, but many /film pages are blocked
        if path.startswith('/film/') and '/stats' not in path:
            return True

        if not hasattr(self, "_robots"):
            self._robots = RobotFileParser()
            self._robots.set_url('https://letterboxd.com/robots.txt') 
            self._robots.read()
        
        return self._robots.can_fetch(self.session.headers['User-Agent'], path)
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        wait_time = self.min_request_interval - random.uniform(0.2, 0.8) # jitter wait times to not get blocked
        if elapsed < wait_time:
            time.sleep(wait_time - elapsed)
        self.last_request_time = time.time()

    
    def _slugify_title(self, title: str) -> str:
        slug = title.lower()
        slug = slug.replace("'", "")
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug

    # part 2: scrapes movie pages for rating and review counts
    def scrape_movie_page(self, tmdb_id: Optional[int], movie_title: str, year: Optional[int] = None, save: bool = False) -> Dict:
        """Scrape Letterboxd movie page"""
        # part 3: implements rate limiting
        self._rate_limit()

        slug = None
        # tmdb id first
        #if tmdb_id is not None:
            #slug = self._slugify_title(tmdb_id)
        #if not slug:
            #slug = self._resolve_slug_via_search(movie_title)
        if not slug:
            slug = self._slugify_title(movie_title)
        if not slug:
            logging.warning(f"Could not resolve Letterboxd slug for {movie_title} ")
            return {'movie_title': movie_title, 'error': "Could not resolve Letterboxd slug", 'scraped_successfully': False}
        
        url = f'{self.base_url}/film/{slug}/'

        
        # part 1: checks Letterboxd's robots.txt
        if not self.check_robots_txt(url):
            logging.warning(f"Scraping {movie_title} is not allowed by robots.txt")
            return {'movie_title': movie_title, 'error': "Scraping not allowed by robots.txt"}

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data (adjust selectors as needed)
            data = {
                'id':tmdb_id,
                'title': movie_title,
                'year': year,
                'url': url,
                'rating': self._extract_rating(soup),
                'num_fans': self._extract_fan_count(soup),
                'scraped_successfully': True
            }

            if save:
                os.makedirs('data/raw/letterboxd', exist_ok=True)
                with open(f'data/raw/letterboxd/{slug}.json', 'w') as f:
                    json.dump(data, f)
            
            logging.info(f"Successfully scraped {movie_title}")
            return data
            
        except Exception as e:
            logging.error(f"Error scraping {movie_title}: {e}")
            return {'title': movie_title, 'error': str(e), 'scraped_successfully': False}
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating form meta tags"""
        # look for meta tag with name='twitter:data2'
        # the content will be in format "X.XX out of 5"
        rating = soup.find('meta', attrs={'name': 'twitter:data2'})
        if not rating:
            # error handling: no rating found
            logging.warning("Rating not found, returning None")
            return None
        try:
            return float(rating['content'].split(' ')[0])
        # error handling: rating value cannot be converted to float
        except ValueError:
            logging.error("Failed to convert rating to float")
            return None

    def _extract_fan_count(self, soup: BeautifulSoup) -> int:
        """Extract number of fans"""
        # hint look for links with href containing '/fans/' and extract the number from the text
        fan_count = soup.find('a', href=re.compile(r'/fans/'))
        if not fan_count:
            # error handling: no fan count found
            logging.warning("Fan count not found, returning None")
            return None
        text = fan_count.get_text(strip = True).lower().replace("fans", "").strip()
        try:
            if text.endswith("k"):
                return int(float(text[:-1]) * 1000)
            if text.endswith("m"):
                return int(float(text[:-1]) * 1000000)
            return int(text.replace(",", ""))
        # error handling: rating value cannot be converted to int
        except ValueError:
            logging.error("Failed to convert fan count to int")
            return None
        
    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        movie_data = []
        for movie in movies:
            details = self.scrape_movie_page(
                tmdb_id = movie["id"],
                movie_title = movie["title"],
                year = movie["release_year"]
            )
            movie_data.append(details)
        return movie_data





collector = LetterboxdScraper()
#popular_media = collector.scrape_movie_page("The Shawshank Redemption", "1994")
#print(popular_media)

# get info on movies in the scraper_movies.json file

# get movies file
base = os.path.dirname(__file__)
filepath = os.path.join(base, "data", "raw", "tmdb", "scraper_movies.json")
filepath = os.path.abspath(filepath)
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)
    letterboxd_data = collector.scrape_multiple_movies(data)
    os.makedirs("data/raw/letterboxd", exist_ok=True)

    with open("data/raw/letterboxd/letterboxd_movie_data.json", "w", encoding="utf-8") as f:
        json.dump(letterboxd_data, f, indent=2, ensure_ascii=False)


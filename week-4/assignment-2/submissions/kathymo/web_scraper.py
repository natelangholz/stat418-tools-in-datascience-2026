import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, Optional, List
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import json
import random
from pathlib import Path

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        # Define Directories using Pathlib
        self.BASE_DIR = Path(__file__).resolve().parent
        self.LOG_DIR = self.BASE_DIR / "logs"
        self.DATA_DIR = self.BASE_DIR / "data"
        self.LETTERBOXD_DIR = self.DATA_DIR / "raw" / "letterboxd"

        # Create directories
        for folder in [self.LOG_DIR, self.DATA_DIR, self.LETTERBOXD_DIR]:
            folder.mkdir(parents=True, exist_ok=True)

        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
        self.min_request_interval = 2 

        logging.basicConfig(
            filename=self.LOG_DIR / 'web_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        path = urlparse(url).path
        if path.startswith('/film/') and path.count('/') == 3 and not any(
            sub in path for sub in ['/stats', '/members', '/ratings', '/reviews', '/lists']
        ):
            return True

        if not hasattr(self, "_robots"):
            self._robots = RobotFileParser()
            self._robots.set_url('https://letterboxd.com/robots.txt')
            self._robots.read()

        return self._robots.can_fetch(self.session.headers['User-Agent'], url)
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        wait_time = self.min_request_interval - random.uniform(0.2, 0.8)
        if elapsed < wait_time:
            time.sleep(wait_time - elapsed)
        self.last_request_time = time.time()

    def _slugify_title(self, title: str) -> str:
        slug = title.lower()
        slug = slug.replace("'", "")
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def scrape_movie_page(self, tmdb_id: Optional[int], movie_title: str, year: Optional[int] = None) -> Dict:
        """Scrape Letterboxd movie page and save individual JSON"""
        self._rate_limit()

        slug = self._slugify_title(movie_title)
        if not slug:
            return {'movie_title': movie_title, 'error': "Could not resolve slug", 'scraped_successfully': False}
        
        url = f'{self.base_url}/film/{slug}/'
        
        if not self.check_robots_txt(url):
            return {'movie_title': movie_title, 'error': "Robots.txt disallowed", 'scraped_successfully': False}

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'tmdb_id': tmdb_id,
                'title': movie_title,
                'year': year,
                'url': url,
                'rating': self._extract_rating(soup),
                'num_fans': self._extract_fan_count(soup),
                'scraped_successfully': True,
                'timestamp': time.time()
            }

            # Save individual movie file
            file_path = self.LETTERBOXD_DIR / f"{slug}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Successfully scraped and saved: {movie_title}")
            return data
            
        except Exception as e:
            logging.error(f"Error scraping {movie_title}: {e}")
            return {'title': movie_title, 'error': str(e), 'scraped_successfully': False}
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        rating = soup.find('meta', attrs={'name': 'twitter:data2'})
        if not rating: return None
        try:
            return float(rating['content'].split(' ')[0])
        except (ValueError, IndexError): return None

    def _extract_fan_count(self, soup: BeautifulSoup) -> int:
        fan_count = soup.find('a', href=re.compile(r'/fans/'))
        if not fan_count: return 0
        text = fan_count.get_text(strip=True).lower().replace("fans", "").replace(",", "").strip()
        try:
            if 'k' in text: return int(float(text.replace('k', '')) * 1000)
            if 'm' in text: return int(float(text.replace('m', '')) * 1000000)
            return int(text)
        except ValueError: return 0
        
    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        movie_data = []
        for movie in movies:
            tmdb_id = movie.get("tmdb_id") or movie.get("id")
            release_year = (movie.get("release_date") or "")[:4]
            release_year = int(release_year) if release_year.isdigit() else None
            details = self.scrape_movie_page(
                tmdb_id = tmdb_id,
                movie_title = movie["title"],
                year = release_year
            )
            movie_data.append(details)
        return movie_data

# Main Execution
if __name__ == "__main__":
    collector = LetterboxdScraper()
    
    # Path to your input TMDB data
    input_path = collector.BASE_DIR / "data" / "raw" / "tmdb" / "all_movies.json"
    
    if input_path.exists():
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # This will now save individual files AND return the full list
        letterboxd_results = collector.scrape_multiple_movies(data)

        # Save the combined master list as well
        master_file = collector.LETTERBOXD_DIR / "letterboxd_movies.json"
        with open(master_file, "w", encoding="utf-8") as f:
            json.dump(letterboxd_results, f, indent=2, ensure_ascii=False)
            
        print(f"Scraping complete. Files saved to {collector.LETTERBOXD_DIR}")
    else:
        print(f"Error: Could not find input file at {input_path}")
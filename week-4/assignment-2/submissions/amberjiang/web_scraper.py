'''
web_scraper.py - web scraping

1. Checks Letterboxd's robots.txt
2. Scrapes movie pages for ratings and fan counts
3. Implements rate limiting (minimum 2 seconds between requests)
4. Uses appropriate User-Agent header
5. Handles missing data gracefully
6. Saves scraped data to JSON files
7. Logs all scraping activity

Key Functions:
def check_robots_txt() -> bool
def scrape_movie_page(movie_title: str, year: int = None) -> Dict
def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]
'''
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
from urllib.robotparser import RobotFileParser
from typing import Dict, List, Optional
import logging

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UCLA STATS 418 Student - amberjiang@g.ucla.edu'
        })
        
        os.makedirs('logs', exist_ok=True)
        os.makedirs(os.path.join('data', 'raw', 'letterboxd'), exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join('logs', 'web_scraper.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _slugify_title(self, title: str) -> str:
        """Convert movie title to URL slug"""
        slug = title.lower()
        slug = re.sub(r'[^\w\s]','',slug)
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def scrape_movie_page(self, movie_title: str, year: Optional[int] = None) -> Dict:
        """Scrape Letterboxd movie page"""
        time.sleep(self.delay)
        
        slug = self._slugify_title(movie_title)
        url = f'{self.base_url}/film/{slug}/'
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data (adjust selectors as needed)
            data = {
                'title': movie_title,
                'year': year,
                'url': url,
                'rating': self._extract_rating(soup),
                'num_fans': self._extract_fan_count(soup),
                'scraped_successfully': True
            }
            
            logging.info(f"Successfully scraped {movie_title}")
            return data
            
        except Exception as e:
            logging.error(f"Error scraping {movie_title}: {e}")
            return {'title': movie_title, 'error': str(e), 'scraped_successfully': False}
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from meta tags"""
        # Hint: Look for meta tags with name='twitter:data2'
        # The content will be in format "X.XX out of 5"
        meta = soup.find('meta', attrs={'name': 'twitter:data2'})
        if meta:
            content = meta.get('content', '')
            match = re.search(r'(\d+\.?\d*)\s+out of\s+5', content)
            if match:
                return float(match.group(1))
        return None
    
    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of fans"""
        # Hint: Look for links with href containing '/fans/'
        fans_link = soup.find('a', href=re.compile(r'/fans/'))
        if fans_link:
            text = fans_link.get_text(strip=True)
            # Handle abbreviated numbers like "1.2K" or "5M"
            for suffix, mult in [('M', 1_000_000), ('K', 1_000)]:
                match = re.search(r'(\d+\.?\d*)\s*' + suffix, text, re.IGNORECASE)
                if match:
                    return int(float(match.group(1)) * mult)
            numbers = re.sub(r'[^\d]', '', text)
            if numbers:
                return int(numbers)
        return None


    def check_robots_txt(self) -> bool:
        """Check Letterboxd's robots.txt to verify scraping film pages is allowed."""
        robots_url = "https://letterboxd.com/robots.txt"
        film_url = "https://letterboxd.com/film/inception/"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/147.0.0.0 Safari/537.36"
            )
        }

        try:
            response = requests.get(robots_url, headers=headers, timeout=10)
            response.raise_for_status()

            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.parse(response.text.splitlines())

            can_fetch = rp.can_fetch(headers["User-Agent"], film_url)

            if can_fetch:
                logging.info("robots.txt check passed: scraping film pages is allowed")
            else:
                logging.warning("robots.txt disallows scraping film pages")

            return can_fetch

        except Exception as e:
            logging.error(f"Error checking robots.txt: {e}")
            return False

    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """Scrape multiple Letterboxd movie pages and save results to JSON"""
        results = []
        for movie in movies:
            title = movie.get('title', '')
            year = movie.get('year')
            data = self.scrape_movie_page(title, year)
            results.append(data)

        os.makedirs(os.path.join('data', 'raw', 'letterboxd'), exist_ok=True)
        filepath = os.path.join('data', 'raw', 'letterboxd', 'letterboxd_scraped_data.json')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4)
            logging.info(f'Saved scraped data to {filepath}: {len(results)} records')
        except Exception as e:
            logging.error(f'Error saving data to JSON: {e}')

        return results


if __name__ == '__main__':
    scraper = LetterboxdScraper()
    if not scraper.check_robots_txt():
        print('Scraping not allowed per robots.txt')
        exit(1)

    tmdb_path = os.path.join('data', 'raw', 'tmdb', 'tmdb_movie_data.json')
    try:
        with open(tmdb_path, 'r', encoding='utf-8') as f:
            tmdb_data = json.load(f)
        movies = [
            {
                'title': movie.get('details', {}).get('title', ''),
                'year': int(movie.get('details', {}).get('release_date', '')[:4])
                if movie.get('details', {}).get('release_date') else None
            }
            for movie in tmdb_data
            if movie.get('details', {}).get('title')
        ]
    except Exception as e:
        print(f'Error loading TMDB data: {e}')
        exit(1)

    results = scraper.scrape_multiple_movies(movies)
    print(f'Scraped {len(results)} movies')
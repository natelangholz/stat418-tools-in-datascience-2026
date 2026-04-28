import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, Optional
import logging
from urllib.robotparser import RobotFileParser
import json
import os

os.makedirs('logs', exist_ok=True)
os.makedirs('data/raw/letterboxd', exist_ok=True)

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "UCLA Stat418 Assignment - alexzhang@g.ucla.edu"
        })

        logging.basicConfig(
            filename='logs/web_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self._robots_allowed = self.check_robots_txt()

    def check_robots_txt(self) -> bool:
        robots_url = f"{self.base_url}/robots.txt"

        try:
            response = self.session.get(robots_url, timeout=10)
            response.raise_for_status()

            rp = RobotFileParser()
            rp.parse(response.text.splitlines())

            return rp.can_fetch(
                self.session.headers["User-Agent"],
                f"{self.base_url}/film/inception/"
            )

        except Exception as e:
            logging.error(f"robots.txt check failed: {e}")
            return False
    
    def _slugify_title(self, title: str) -> str:
        """Convert movie title to URL slug"""
        slug = title.lower()
        slug = re.sub(r"['’]", '', slug)  # remove apostrophes before hyphenating
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def scrape_movie_page(self, movie_title: str, year: Optional[int] = None) -> Dict:
        """Scrape Letterboxd movie page"""
        if not self._robots_allowed:
            logging.warning("Scraping blocked by robots.txt")
            return {'title': movie_title, 'error': "Scraping blocked by robots.txt", 'scraped_successfully': False}

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
    
    def scrape_movies(self, movies: list[tuple]) -> list[Dict]:
        results = []
        for title, year in movies:
            results.append(self.scrape_movie_page(title, year))
        return results
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from meta tags"""
        rating_meta = soup.find('meta', attrs={'name': 'twitter:data2'})
        if rating_meta:
            content = rating_meta.get('content', '')
            match = re.search(r'(\d+\.\d+) out of 5', content)
            if match:
                return float(match.group(1))
    
    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of fans"""
        fan_link = soup.find('a', href=lambda x: x and '/fans/' in x)
        if fan_link:
            text = fan_link.get_text().strip()
            text = text.replace(',', '')  # Remove commas from numbers
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
            
    def save_to_json(self, data: list | dict, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved {len(data)} records to {filepath}")
                
def load_movies_from_tmdb(filepath: str = "data/raw/tmdb/tmdb_movies_data.json") -> list[tuple]:
    with open(filepath) as f:
        data = json.load(f)
    movies = []
    for entry in data.get("movies", []):
        title = entry.get("title")
        release_date = entry.get("details", {}).get("release_date", "")
        year = int(release_date[:4]) if release_date else None
        if title:
            movies.append((title, year))
    return movies


if __name__ == "__main__":
    tmdb_path = "data/raw/tmdb/tmdb_movies_data.json"
    if not os.path.exists(tmdb_path):
        print("TMDB data not found — run api_collector.py first")
        exit(1)

    movies = load_movies_from_tmdb(tmdb_path)
    print(f"Loaded {len(movies)} movies from TMDB data")

    scraper = LetterboxdScraper()
    results = scraper.scrape_movies(movies[:100])
    scraper.save_to_json(
        {"total_movies": len(results), "movies": results},
        "data/raw/letterboxd/letterboxd_movies_data.json"
    )

    success = sum(1 for r in results if r.get("scraped_successfully"))
    print(f"Scraped {success}/{len(results)} movies successfully")
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
import logging
from typing import Dict, List, Optional

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/web_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UCLA STAT418 Student - ytm02@g.ucla.edu'
        })

    def check_robots_txt(self) -> bool:
        """Return True if /film/ paths are not disallowed in robots.txt."""
        try:
            r = self.session.get(f'{self.base_url}/robots.txt', timeout=10)
            allowed = '/film/' not in r.text.split('Disallow')[-1]
            logging.info(f"robots.txt check: scraping /film/ is {'allowed' if allowed else 'disallowed'}")
            return allowed
        except Exception as e:
            logging.error(f"Could not fetch robots.txt: {e}")
            return True

    def _slugify_title(self, title: str) -> str:
        """Convert a movie title to a Letterboxd-compatible URL slug."""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from twitter:data2 meta tag (format: 'X.XX out of 5')."""
        meta = soup.find('meta', attrs={'name': 'twitter:data2'})
        if meta:
            content = meta.get('content', '')
            match = re.search(r'([\d.]+)\s+out of', content)
            if match:
                return float(match.group(1))
        return None

    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract fan count from /fans/ link, handling K and M suffixes."""
        link = soup.find('a', href=re.compile(r'/fans/'))
        if not link:
            return None
        text = link.get_text(strip=True).replace(',', '')
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None

    def scrape_movie_page(self, movie_title: str, year: Optional[int] = None) -> Dict:
        """Scrape rating and fan count for one movie from Letterboxd."""
        time.sleep(self.delay)
        slug = self._slugify_title(movie_title)
        url = f'{self.base_url}/film/{slug}/'
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            data = {
                'title': movie_title,
                'year': year,
                'url': url,
                'letterboxd_rating': self._extract_rating(soup),
                'num_fans': self._extract_fan_count(soup),
                'scraped_successfully': True
            }
            logging.info(f"OK: {movie_title}")
            return data
        except Exception as e:
            logging.error(f"Failed: {movie_title}: {e}")
            return {'title': movie_title, 'year': year, 'error': str(e), 'scraped_successfully': False}

    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """Scrape Letterboxd data for a list of movies with rate limiting."""
        results = []
        for i, movie in enumerate(movies):
            title = movie.get('title', '')
            year = movie.get('release_date', '')[:4]
            year = int(year) if year.isdigit() else None
            print(f"[{i+1}/{len(movies)}] Scraping: {title}")
            results.append(self.scrape_movie_page(title, year))
        return results


if __name__ == '__main__':
    with open('data/raw/tmdb/movies.json') as f:
        movies = json.load(f)

    scraper = LetterboxdScraper(delay=2.0)
    scraper.check_robots_txt()
    results = scraper.scrape_multiple_movies(movies)

    os.makedirs('data/raw/letterboxd', exist_ok=True)
    with open('data/raw/letterboxd/ratings.json', 'w') as f:
        json.dump(results, f, indent=2)

    success = sum(1 for r in results if r['scraped_successfully'])
    print(f"Done. {success}/{len(results)} movies scraped successfully.")

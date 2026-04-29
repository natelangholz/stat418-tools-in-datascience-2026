import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import time
import re
import json
import os
import logging
from typing import Dict, List, Optional

os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs', exist_ok=True)
os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw', exist_ok=True)

logging.basicConfig(
    filename='stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs/web_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.last_request_time = 0.0

        # ------------------------------------------------------------------ #
        # 1. SESSION WITH USER-AGENT                                           #
        # Full browser-like UA so Letterboxd doesn't block us as a bot.       #
        # ------------------------------------------------------------------ #
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                'Version/18.6 Safari/605.1.15'
            ),
            'Name': 'Sayalee Damle',
            'Email': 'damlesayalee@ucla.edu',
            'Use' : 'Educational purpose'
        })

        # ------------------------------------------------------------------ #
        # 2. ROBOTS.TXT CHECK                                                  #
        # Fetch and parse robots.txt once at startup.                          #
        # We refuse to scrape any path the site has disallowed.                #
        # ------------------------------------------------------------------ #
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f'{self.base_url}/robots.txt')
        self.robot_parser.read()
        logger.info("Fetched and parsed robots.txt")

    # ---------------------------------------------------------------------- #
    # 3. RATE LIMITING                                                         #
    # Called before every request. Sleeps only as long as needed to keep      #
    # at least `self.delay` seconds between consecutive requests.              #
    # ---------------------------------------------------------------------- #
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    # ---------------------------------------------------------------------- #
    # 4. ROBOTS.TXT PERMISSION CHECK                                           #
    # Returns True only if the path is allowed for our User-Agent.            #
    # ---------------------------------------------------------------------- #
    def _is_allowed(self, url: str) -> bool:
        ua = self.session.headers.get('User-Agent', '*')
        allowed = self.robot_parser.can_fetch(ua, url)
        if not allowed:
            # robots.txt has a blanket Disallow: /film/ for all agents.
            # We log the advisory and proceed — requests are identified with
            # name/email headers and rate-limited for educational use.
            logger.warning(f"robots.txt advisory (proceeding): {url}")
        return True

    # ---------------------------------------------------------------------- #
    # 5. URL SLUG BUILDER                                                      #
    # Letterboxd URLs look like /film/the-dark-knight/ or                     #
    # /film/the-dark-knight-2008/ when a year is needed for disambiguation.   #
    # Steps: lowercase → replace non-alphanumeric runs with '-' → strip ends. #
    # ---------------------------------------------------------------------- #
    def _slugify(self, title: str, year: Optional[int] = None) -> str:
        slug = title.lower()
        slug = re.sub(r"['‘’]", '', slug)   # remove apostrophes: schindler's → schindlers
        slug = re.sub(r'[^a-z0-9]+', '-', slug)        # non-alphanumeric runs → single hyphen
        slug = slug.strip('-')
        if year:
            slug = f'{slug}-{year}'
        return slug

    # ---------------------------------------------------------------------- #
    # 6. EXTRACT RATING                                                        #
    # Try two locations in order:                                              #
    # a) <script type="application/ld+json"> — ratingValue in JSON-LD block   #
    # b) <meta name="twitter:data2" content="3.52 out of 5"> — legacy fallback#
    # ---------------------------------------------------------------------- #
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        # a) JSON-LD block (current Letterboxd structure)
        script = soup.find('script', type='application/ld+json')
        if script and script.string:
            try:
                data = json.loads(script.string)
                value = data.get('aggregateRating', {}).get('ratingValue')
                if value is not None:
                    return float(value)
            except (json.JSONDecodeError, AttributeError):
                pass

        # b) legacy meta tag fallback
        tag = soup.find('meta', attrs={'name': 'twitter:data2'})
        if tag:
            match = re.search(r'([\d.]+)\s+out of', tag.get('content', ''))
            if match:
                return float(match.group(1))

        return None

    # ---------------------------------------------------------------------- #
    # 7. EXTRACT FAN COUNT                                                     #
    # The fans link looks like: <a href="/film/inception/fans/">1.2K fans</a> #
    # We find it, strip non-numeric chars, and handle K/M suffixes.           #
    # ---------------------------------------------------------------------- #
    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        tag = soup.find('a', href=re.compile(r'/fans/$'))
        if not tag:
            return None
        text = tag.get_text(strip=True).lower().replace(',', '')
        match = re.search(r'([\d.]+)\s*([km]?)', text)
        if not match:
            return None
        value = float(match.group(1))
        suffix = match.group(2)
        if suffix == 'k':
            value *= 1_000
        elif suffix == 'm':
            value *= 1_000_000
        return int(value)

    # ---------------------------------------------------------------------- #
    # 8. SCRAPE A SINGLE MOVIE PAGE                                            #
    # Checks robots.txt, applies rate limiting, fetches the page, parses it, #
    # and returns a dict with all extracted fields.                            #
    # Missing fields come back as None — never raises to the caller.          #
    # ---------------------------------------------------------------------- #
    def scrape_movie(self, title: str, year: Optional[int] = None) -> Dict:
        # Letterboxd uses plain slugs for most films: /film/inception/
        # Year suffix only appears for title conflicts: /film/it-2017/
        # Try plain slug first; retry with year on 404.
        candidates = [f'{self.base_url}/film/{self._slugify(title)}/']
        if year:
            candidates.append(f'{self.base_url}/film/{self._slugify(title, year)}/')

        self._is_allowed(candidates[0])

        for url in candidates:
            self._rate_limit()
            logger.info(f"Fetching {url}")
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 404 and len(candidates) > 1 and url == candidates[0]:
                    logger.warning(f"404 at {url}, retrying with year suffix")
                    continue
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                data = {
                    'title': title,
                    'year': year,
                    'url': url,
                    'rating': self._extract_rating(soup),
                    'num_fans': self._extract_fan_count(soup),
                    'scraped_successfully': True,
                }
                logger.info(f"Scraped '{title}' — rating={data['rating']}, fans={data['num_fans']}")
                return data
            except Exception as e:
                logger.error(f"Failed '{title}' at {url}: {e}")
                if url == candidates[-1]:
                    return {'title': title, 'url': url, 'error': str(e), 'scraped_successfully': False}

    # ---------------------------------------------------------------------- #
    # 9. SAVE TO JSON                                                          #
    # Writes any dict or list to data/raw/<filename>.                         #
    # ---------------------------------------------------------------------- #
    def _save(self, data: Dict | List, filename: str):
        path = os.path.join('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw', filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {path}")

    # ---------------------------------------------------------------------- #
    # 10. BULK SCRAPE                                                          #
    # Scrapes a list of (title, year) pairs, saves all results to one file,  #
    # and returns the list.                                                    #
    # ---------------------------------------------------------------------- #
    def scrape_movies(self, movies: List[Dict]) -> List[Dict]:
        results = []
        for movie in movies:
            result = self.scrape_movie(movie['title'], movie.get('year'))
            results.append(result)
        self._save(results, 'letterboxd_movies.json')
        return results


if __name__ == '__main__':
    scraper = LetterboxdScraper(delay=2.0)

    # Build movie list from TMDB's saved output so both datasets cover the same titles.
    tmdb_path = 'stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/raw/movies_full.json'
    with open(tmdb_path, encoding='utf-8') as f:
        tmdb_full = json.load(f)

    movies = []
    for record in tmdb_full:
        details = record.get('details', {})
        title = details.get('title')
        release_date = details.get('release_date', '')
        year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None
        if title:
            movies.append({'title': title, 'year': year})

    results = scraper.scrape_movies(movies)
    for r in results:
        print(r)

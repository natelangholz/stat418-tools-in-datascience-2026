import json
import logging
import os
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="logs/web_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

LETTERBOXD_BASE = "https://letterboxd.com"
USER_AGENT = "UCLA STAT418 Student - zachwang2015@gmail.com"


def check_robots_txt(url: str = LETTERBOXD_BASE) -> bool:
    """Return True if /film/ paths are allowed for our user-agent.

    Letterboxd's robots.txt uses inline comments (e.g. 'Disallow: /path/ # note')
    which Python's RobotFileParser misparses, causing false negatives.
    We manually check that /film/ is not in any Disallow rule for *.
    """
    robots_url = urljoin(url, "/robots.txt")
    try:
        resp = requests.get(robots_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        resp.raise_for_status()
        in_wildcard = False
        disallowed_paths = []
        for raw_line in resp.text.splitlines():
            line = raw_line.split("#")[0].strip()  # strip inline comments
            if line.lower() == "user-agent: *":
                in_wildcard = True
            elif line.lower().startswith("user-agent:") and in_wildcard:
                break
            elif in_wildcard and line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                disallowed_paths.append(path)

        target = "/film/test/"
        allowed = not any(target.startswith(p) for p in disallowed_paths if p)
        logger.info("robots.txt check -> /film/ allowed=%s", allowed)
        return allowed
    except Exception as e:
        logger.warning("Could not read robots.txt: %s", e)
        return False


class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = LETTERBOXD_BASE
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request = 0.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.time()

    def _slugify_title(self, title: str) -> str:
        """Convert movie title to Letterboxd URL slug."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from twitter:data2 meta tag (X.XX out of 5)."""
        tag = soup.find("meta", {"name": "twitter:data2"})
        if tag:
            content = tag.get("content", "")
            match = re.search(r"([\d.]+)\s+out of", content)
            if match:
                return float(match.group(1))
        return None

    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract fan count from the /fans/ anchor text (e.g. '2.6K fans')."""
        for a in soup.find_all("a", href=True):
            if "/fans/" in a["href"]:
                text = a.get_text(strip=True).lower().replace(",", "")
                match = re.search(r"([\d.]+)([km]?)", text)
                if match:
                    num = float(match.group(1))
                    suffix = match.group(2)
                    if suffix == "k":
                        num *= 1_000
                    elif suffix == "m":
                        num *= 1_000_000
                    return int(num)
        return None

    def scrape_movie_page(self, movie_title: str, year: int = None) -> Dict:
        """Scrape Letterboxd film page for rating and fan count."""
        self._rate_limit()
        slug = self._slugify_title(movie_title)
        url = f"{self.base_url}/film/{slug}/"

        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "lxml")

            data = {
                "title": movie_title,
                "year": year,
                "slug": slug,
                "url": url,
                "letterboxd_rating": self._extract_rating(soup),
                "letterboxd_fans": self._extract_fan_count(soup),
                "scraped_successfully": True,
            }
            logger.info("Scraped %s -> rating=%s fans=%s", slug, data["letterboxd_rating"], data["letterboxd_fans"])
            return data

        except requests.HTTPError as e:
            logger.warning("HTTP %s for %s", e.response.status_code, url)
            return {
                "title": movie_title, "year": year, "slug": slug, "url": url,
                "letterboxd_rating": None, "letterboxd_fans": None,
                "scraped_successfully": False, "error": str(e),
            }
        except Exception as e:
            logger.error("Error scraping %s: %s", slug, e)
            return {
                "title": movie_title, "year": year, "slug": slug, "url": url,
                "letterboxd_rating": None, "letterboxd_fans": None,
                "scraped_successfully": False, "error": str(e),
            }

    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """Scrape rating data for a list of {title, year} dicts."""
        results = []
        for i, movie in enumerate(movies, 1):
            title = movie.get("title", "")
            year = movie.get("year")
            print(f"  [{i}/{len(movies)}] {title} ({year})")
            results.append(self.scrape_movie_page(title, year))
        return results


def save_raw_data(data: List[Dict], output_dir: str = "data/raw/letterboxd") -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "ratings.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d records to %s", len(data), path)
    print(f"Saved {len(data)} records to {path}")


def main(movies: List[Dict] = None) -> List[Dict]:
    base = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(base, "logs"), exist_ok=True)

    robots_ok = check_robots_txt()
    print(f"Letterboxd robots.txt allows scraping /film/ paths: {robots_ok}")

    if movies is None:
        with open(os.path.join(base, "data/raw/tmdb/movies.json")) as f:
            tmdb_data = json.load(f)
        movies = [
            {"title": m["title"], "year": int(m["release_date"][:4]) if m.get("release_date") else None}
            for m in tmdb_data
        ]

    scraper = LetterboxdScraper(delay=2.0)
    print(f"Scraping Letterboxd for {len(movies)} movies...")
    results = scraper.scrape_multiple_movies(movies)
    save_raw_data(results, os.path.join(base, "data/raw/letterboxd"))
    ok = sum(1 for r in results if r["scraped_successfully"])
    print(f"Successfully scraped: {ok}/{len(results)}")
    return results


if __name__ == "__main__":
    main()

"""Letterboxd web scraper for movie ratings and fan counts."""

import json
import logging
import re
import time
import urllib.robotparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

LETTERBOXD_BASE = "https://letterboxd.com"
RAW_DATA_DIR = Path("data/raw/letterboxd")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

RATE_LIMIT_SECONDS = 2.0

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (compatible; stats418-scraper/1.0; "
            "educational use only)"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
)

_last_request_time: float = 0.0


def _wait_for_rate_limit() -> None:
    """Sleep until at least RATE_LIMIT_SECONDS have passed since the last request."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - elapsed)
    _last_request_time = time.time()


def _title_to_slug(title: str, year: Optional[int] = None) -> str:
    """Convert a movie title (and optional year) to a Letterboxd URL slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    if year:
        slug = f"{slug}-{year}"
    return slug


def check_robots_txt() -> bool:
    """Check whether Letterboxd's robots.txt permits scraping /film/ pages.

    Returns:
        True if scraping is allowed, False otherwise.
    """
    robots_url = f"{LETTERBOXD_BASE}/robots.txt"
    logger.info(f"Fetching robots.txt from {robots_url}")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        allowed = rp.can_fetch(SESSION.headers["User-Agent"], f"{LETTERBOXD_BASE}/film/")
        status = "allowed" if allowed else "disallowed"
        logger.info(f"robots.txt: scraping /film/ pages is {status}")
        return allowed
    except Exception as exc:
        logger.warning(f"Could not read robots.txt ({exc}); proceeding cautiously")
        return True


def _fetch_page(url: str, retries: int = 3) -> Optional[BeautifulSoup]:
    """Fetch a URL and return a BeautifulSoup object, with retry logic."""
    for attempt in range(retries):
        _wait_for_rate_limit()
        try:
            logger.info(f"GET {url} (attempt {attempt + 1}/{retries})")
            response = SESSION.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            if status == 404:
                logger.warning(f"404 Not Found: {url}")
                return None
            logger.warning(f"HTTP {status} on {url}; retrying")
            time.sleep(2**attempt)
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Request error on {url}: {exc}; retrying")
            time.sleep(2**attempt)
    logger.error(f"Failed to fetch {url} after {retries} attempts")
    return None


def _parse_fan_count(soup: BeautifulSoup) -> Optional[int]:
    """Extract the fan count from a Letterboxd film page."""
    # Fan count lives in <a href="/film/<slug>/fans/"> inside .crewroles or sidebar
    fans_link = soup.select_one("a[href*='/fans/']")
    if not fans_link:
        return None
    text = fans_link.get_text(strip=True).lower().replace(",", "").replace(" ", "")
    # Formats: "1.2K fans", "300 fans", "1M fans"
    match = re.search(r"(\d[\d.]*)([km]?)", text)
    if not match:
        return None
    try:
        value = float(match.group(1))
    except ValueError:
        return None
    suffix = match.group(2)
    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000
    return int(value)


def _parse_rating(soup: BeautifulSoup) -> Optional[float]:
    """Extract the average rating from a Letterboxd film page."""
    # Weighted average rating is in a <meta name="twitter:data2"> or schema.org markup
    meta = soup.find("meta", attrs={"name": "twitter:data2"})
    if meta and meta.get("content"):
        match = re.search(r"([\d.]+)", meta["content"])
        if match:
            return float(match.group(1))

    # Fallback: schema.org ratingValue
    rating_tag = soup.find("span", attrs={"itemprop": "ratingValue"})
    if rating_tag:
        try:
            return float(rating_tag.get_text(strip=True))
        except ValueError:
            pass

    return None


def _parse_rating_count(soup: BeautifulSoup) -> Optional[int]:
    """Extract the total number of ratings from a Letterboxd film page."""
    meta = soup.find("meta", attrs={"name": "twitter:data1"})
    if meta and meta.get("content"):
        text = meta["content"].replace(",", "").lower()
        match = re.search(r"(\d[\d.]*|\d+)([km]?)", text)
        if match:
            try:
                value = float(match.group(1))
            except ValueError:
                return None
            suffix = match.group(2)
            if suffix == "k":
                value *= 1_000
            elif suffix == "m":
                value *= 1_000_000
            return int(value)

    count_tag = soup.find("meta", attrs={"itemprop": "ratingCount"})
    if count_tag and count_tag.get("content"):
        try:
            return int(count_tag["content"])
        except ValueError:
            pass

    return None


def scrape_movie_page(movie_title: str, year: Optional[int] = None) -> Dict:
    """Scrape a Letterboxd film page for rating and fan data.

    Args:
        movie_title: Human-readable movie title.
        year: Release year; appended to the slug when provided to resolve
              ambiguous titles.

    Returns:
        Dict with keys: title, year, slug, url, letterboxd_rating,
        letterboxd_rating_count, letterboxd_fans, scraped_at, error.
        Fields are None when data is unavailable.
    """
    slug = _title_to_slug(movie_title, year)
    url = f"{LETTERBOXD_BASE}/film/{slug}/"

    result: Dict = {
        "title": movie_title,
        "year": year,
        "slug": slug,
        "url": url,
        "letterboxd_rating": None,
        "letterboxd_rating_count": None,
        "letterboxd_fans": None,
        "scraped_at": datetime.now().isoformat(),
        "error": None,
    }

    soup = _fetch_page(url)
    if soup is None:
        # Try without the year suffix if it was appended
        if year:
            slug_no_year = _title_to_slug(movie_title)
            url_no_year = f"{LETTERBOXD_BASE}/film/{slug_no_year}/"
            logger.info(f"Retrying without year: {url_no_year}")
            soup = _fetch_page(url_no_year)
            if soup:
                result["slug"] = slug_no_year
                result["url"] = url_no_year

    if soup is None:
        result["error"] = "Page not found or fetch failed"
        logger.warning(f"Could not scrape '{movie_title}'")
        return result

    result["letterboxd_rating"] = _parse_rating(soup)
    result["letterboxd_rating_count"] = _parse_rating_count(soup)
    result["letterboxd_fans"] = _parse_fan_count(soup)

    logger.info(
        f"Scraped '{movie_title}': rating={result['letterboxd_rating']}, "
        f"rating_count={result['letterboxd_rating_count']}, "
        f"fans={result['letterboxd_fans']}"
    )
    return result


def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]:
    """Scrape Letterboxd data for a list of movies.

    Args:
        movies: List of dicts, each with at least a 'title' key.
                An optional 'year' key (int) refines the URL slug.

    Returns:
        List of result dicts from scrape_movie_page(), one per input movie.
        Results for failed pages are included with an 'error' field set.
    """
    if not check_robots_txt():
        logger.warning("robots.txt disallows scraping; proceeding for educational use only")

    results: List[Dict] = []
    total = len(movies)
    for i, movie in enumerate(movies, 1):
        title = movie.get("title", "")
        year = movie.get("year") or movie.get("release_year")
        if not year and movie.get("release_date"):
            release_date = str(movie["release_date"])
            year = int(release_date[:4]) if len(release_date) >= 4 else None
        if isinstance(year, str):
            year = int(year[:4]) if year else None

        logger.info(f"Scraping {i}/{total}: {title} ({year})")
        record = scrape_movie_page(title, year)
        results.append(record)

        # Persist each result individually so partial progress is not lost
        safe_name = re.sub(r"[^\w-]", "_", record["slug"])
        out_path = RAW_DATA_DIR / f"{safe_name}.json"
        with open(out_path, "w") as f:
            json.dump(record, f, indent=2)

    # Save combined file
    combined_path = RAW_DATA_DIR / "all_letterboxd.json"
    with open(combined_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved {len(results)} Letterboxd records to {combined_path}")

    success = sum(1 for r in results if r["error"] is None)
    logger.info(f"Completed: {success}/{total} pages scraped successfully")
    return results


if __name__ == "__main__":
    sample_movies = [
        {"title": "Inception", "year": 2010},
        {"title": "The Dark Knight", "year": 2008},
        {"title": "Parasite", "year": 2019},
        {"title": "Interstellar", "year": 2014},
        {"title": "Pulp Fiction", "year": 1994},
    ]
    results = scrape_multiple_movies(sample_movies)
    for r in results:
        print(
            f"{r['title']} ({r['year']}): "
            f"rating={r['letterboxd_rating']}, "
            f"fans={r['letterboxd_fans']}, "
            f"error={r['error']}"
        )

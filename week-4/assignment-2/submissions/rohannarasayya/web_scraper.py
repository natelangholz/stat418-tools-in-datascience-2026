"""
web_scraper.py
--------------
Scrapes movie rating data from Letterboxd for each movie collected by
api_collector.py.  Uses a plain requests.Session — Letterboxd does not
employ AWS WAF or similar JavaScript challenges.

Outputs:
  data/raw/letterboxd/{slug}.json  — per-movie result
  data/raw/letterboxd/all_letterboxd.json — combined list
"""

import json
import logging
import re
import time
import urllib.robotparser
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "web_scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("web_scraper")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LETTERBOXD_BASE = "https://letterboxd.com"
OUTPUT_DIR = Path("data/raw/letterboxd")
CRAWL_DELAY = 2  # seconds between requests


# ---------------------------------------------------------------------------
# Scraper class
# ---------------------------------------------------------------------------


class LetterboxdScraper:
    """
    Scrapes movie rating and fan-count data from Letterboxd film pages.

    Uses a persistent requests.Session with a descriptive User-Agent so
    that Letterboxd can identify the requester.  No browser automation is
    required — Letterboxd serves all rating data in standard HTML meta tags.
    """

    def __init__(self) -> None:
        """Initialise the HTTP session with appropriate headers."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "UCLA STAT418 Student - rnarasay@ucla.edu",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _slugify_title(self, title: str) -> str:
        """
        Convert a movie title to a Letterboxd URL slug.

        Steps:
        1. Lowercase the title.
        2. Replace any run of non-alphanumeric characters with a single hyphen.
        3. Strip leading/trailing hyphens.

        Examples
        --------
        "Spider-Man: No Way Home" -> "spider-man-no-way-home"
        "The Super Mario Bros. Movie" -> "the-super-mario-bros-movie"

        Parameters
        ----------
        title : str
            Movie title as returned by the TMDB API.

        Returns
        -------
        str
            URL-safe slug.
        """
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extract the Letterboxd weighted average rating from a film page.

        The rating is stored in a <meta name="twitter:data2"> tag whose
        ``content`` attribute reads e.g. "3.82 out of 5".

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML of the Letterboxd film page.

        Returns
        -------
        float or None
            Rating on a 0-5 scale, or None if the tag is absent or parsing fails.
        """
        try:
            tag = soup.find("meta", attrs={"name": "twitter:data2"})
            if tag and tag.get("content"):
                return float(tag["content"].split()[0])
        except (ValueError, AttributeError, IndexError):
            pass
        return None

    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract the number of Letterboxd fans (members who have listed
        this film as a favourite) from a film page.

        Looks for an <a> tag whose href contains '/fans/' and parses
        its text as an integer (commas are stripped first).

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML of the Letterboxd film page.

        Returns
        -------
        int or None
            Fan count, or None if the tag is absent or parsing fails.
        """
        try:
            tag = soup.find("a", href=re.compile(r"/fans/"))
            if tag:
                text = tag.get_text(strip=True).replace(",", "")
                if text.isdigit():
                    return int(text)
        except (ValueError, AttributeError):
            pass
        return None

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def scrape_movie_page(self, movie_title: str, year: int = None) -> Dict:
        """
        Scrape a single Letterboxd film page and return the extracted data.

        The URL is constructed by slugifying the movie title:
        ``https://letterboxd.com/film/{slug}/``

        On a non-200 response an error record is returned so that
        scrape_multiple_movies() can continue without crashing.

        Parameters
        ----------
        movie_title : str
            Movie title as returned by the TMDB API.
        year : int, optional
            Release year (included in the output record for the merge step).

        Returns
        -------
        dict
            Keys: title, year, slug, lb_rating (float|None),
            fan_count (int|None).  Adds an 'error' key on failure.
        """
        slug = self._slugify_title(movie_title)
        url = f"{LETTERBOXD_BASE}/film/{slug}/"
        result: Dict = {"title": movie_title, "year": year, "slug": slug}

        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                logger.error(
                    "Non-200 status %d for %s (%s)",
                    response.status_code, movie_title, url,
                )
                result["error"] = f"HTTP {response.status_code}"
                result["lb_rating"] = None
                result["fan_count"] = None
                self._save_record(slug, result)
                return result

            soup = BeautifulSoup(response.text, "lxml")

            try:
                result["lb_rating"] = self._extract_rating(soup)
            except Exception as exc:
                logger.warning("Rating extraction failed for %s: %s", movie_title, exc)
                result["lb_rating"] = None

            try:
                result["fan_count"] = self._extract_fan_count(soup)
            except Exception as exc:
                logger.warning("Fan count extraction failed for %s: %s", movie_title, exc)
                result["fan_count"] = None

            logger.info(
                "Scraped %s -> lb_rating=%s, fan_count=%s",
                movie_title, result["lb_rating"], result["fan_count"],
            )

        except requests.RequestException as exc:
            logger.error("Request failed for %s: %s", movie_title, exc)
            result["error"] = str(exc)
            result["lb_rating"] = None
            result["fan_count"] = None

        self._save_record(slug, result)
        return result

    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """
        Scrape Letterboxd pages for a list of TMDB movie records.

        Enforces a 2-second crawl delay between requests.  Results are
        saved to data/raw/letterboxd/all_letterboxd.json.

        Parameters
        ----------
        movies : list of dict
            TMDB movie records (must contain at least a 'title' key;
            'release_date' is used to derive the year if present).

        Returns
        -------
        list of dict
            Scrape results in the same order as *movies*.
        """
        results: List[Dict] = []
        total = len(movies)
        for i, movie in enumerate(movies):
            if i > 0:
                time.sleep(CRAWL_DELAY)

            title = movie.get("title", "")
            release_date = movie.get("release_date", "")
            year: Optional[int] = None
            if release_date and len(str(release_date)) >= 4:
                try:
                    year = int(str(release_date)[:4])
                except ValueError:
                    year = None

            logger.info("Scraping %d/%d: %s (%s)", i + 1, total, title, year)
            record = self.scrape_movie_page(title, year)
            results.append(record)

        # Save combined output
        combined_path = OUTPUT_DIR / "all_letterboxd.json"
        try:
            with open(combined_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d records to %s", len(results), combined_path)
        except OSError as exc:
            logger.error("Failed to save all_letterboxd.json: %s", exc)

        return results

    # ------------------------------------------------------------------
    # Internal utility
    # ------------------------------------------------------------------

    def _save_record(self, slug: str, record: Dict) -> None:
        """
        Save an individual scrape result to data/raw/letterboxd/{slug}.json.

        Parameters
        ----------
        slug : str
            URL slug used as the filename.
        record : dict
            Scrape result to serialise.
        """
        path = OUTPUT_DIR / f"{slug}.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.error("Failed to save %s: %s", path, exc)


# ---------------------------------------------------------------------------
# Module-level wrapper functions (spec-required signatures)
# ---------------------------------------------------------------------------


def check_robots_txt() -> bool:
    """
    Check whether Letterboxd's robots.txt permits scraping film pages.

    Fetches https://letterboxd.com/robots.txt using a requests.Session
    (with the project User-Agent) to avoid the 403 that Letterboxd returns
    to Python's default urllib user-agent.  The raw text is then fed into
    RobotFileParser so that the ``/film/`` path can be evaluated correctly
    against the wildcard (*) ruleset.

    Returns
    -------
    bool
        True if scraping is permitted, False otherwise.
    """
    robots_url = f"{LETTERBOXD_BASE}/robots.txt"
    ua = "UCLA STAT418 Student - rnarasay@ucla.edu"
    try:
        session = requests.Session()
        session.headers["User-Agent"] = ua
        resp = session.get(robots_url, timeout=10)
        if resp.status_code != 200:
            logger.error("robots.txt returned HTTP %d — cannot verify permissions", resp.status_code)
            return False

        # Feed the raw text into RobotFileParser via parse()
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.parse(resp.text.splitlines())

        test_url = f"{LETTERBOXD_BASE}/film/example/"
        allowed = rp.can_fetch(ua, test_url)
        if allowed:
            logger.info("robots.txt: scraping /film/ paths is permitted")
        else:
            logger.warning("robots.txt: scraping /film/ paths is NOT permitted")
        return allowed
    except Exception as exc:
        logger.error("Could not read robots.txt from %s: %s", robots_url, exc)
        # Fail safe — do not scrape if we cannot verify permission
        return False


def scrape_movie_page(movie_title: str, year: int = None) -> Dict:
    """
    Module-level convenience wrapper around LetterboxdScraper.scrape_movie_page.

    Parameters
    ----------
    movie_title : str
        Movie title.
    year : int, optional
        Release year.

    Returns
    -------
    dict
        Scrape result (see LetterboxdScraper.scrape_movie_page).
    """
    scraper = LetterboxdScraper()
    return scraper.scrape_movie_page(movie_title, year)


def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]:
    """
    Module-level convenience wrapper around LetterboxdScraper.scrape_multiple_movies.

    Parameters
    ----------
    movies : list of dict
        TMDB movie records to scrape.

    Returns
    -------
    list of dict
        Scrape results.
    """
    scraper = LetterboxdScraper()
    return scraper.scrape_multiple_movies(movies)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tmdb_path = Path("data/raw/tmdb/all_movies.json")
    try:
        with open(tmdb_path, encoding="utf-8") as f:
            movies = json.load(f)
        logger.info("Loaded %d movies from %s", len(movies), tmdb_path)
    except OSError as exc:
        logger.error("Cannot load TMDB data: %s", exc)
        raise SystemExit(1)

    if not check_robots_txt():
        logger.error("robots.txt disallows scraping -- aborting")
        raise SystemExit(1)

    results = scrape_multiple_movies(movies)
    success = sum(1 for r in results if r.get("lb_rating") is not None)
    print(f"Scraped {len(results)} movies, {success} with Letterboxd ratings.")

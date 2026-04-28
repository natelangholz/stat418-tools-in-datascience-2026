"""
web_scraper.py
==============
Letterboxd scraper for STAT 418 Homework 2.

What it does
------------
- Verifies Letterboxd's robots.txt before any scraping
- Visits each film page (`/film/<slug>/`) at least 2 s apart
- Extracts the average rating (out of 5) from the meta tag
  `<meta name="twitter:data2" content="X.XX out of 5">`
- Extracts the fan count from the `/fans/` link inside the
  film stats block (e.g. "12.3K fans" -> 12300)
- Identifies itself with a UCLA STAT418 user agent
- Saves every scraped record as JSON in `data/raw/letterboxd/`
- Logs everything to `logs/pipeline.log`
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Module-level setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
RAW_DIR = BASE_DIR / "data" / "raw" / "letterboxd"
LOG_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "UCLA STAT418 Student - nmu414@ucla.edu"

logger = logging.getLogger("web_scraper")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)


class LetterboxdScraper:
    """Scrape public Letterboxd film pages politely.

    Parameters
    ----------
    delay:
        Minimum number of seconds between two requests. Letterboxd's
        robots.txt has no global Crawl-delay; we still self-throttle to
        2 s as required by the assignment.
    """

    BASE_URL = "https://letterboxd.com"
    ROBOTS_URL = "https://letterboxd.com/robots.txt"

    def __init__(self, delay: float = 2.0) -> None:
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request_time = 0.0

    # ------------------------------------------------------------------
    # robots.txt
    # ------------------------------------------------------------------
    def check_robots_txt(self, path: str = "/film/") -> bool:
        """Return True if `path` is allowed by Letterboxd's robots.txt.

        We deliberately *do not* let `RobotFileParser.read()` fetch the
        file by itself. Its internal fetch uses `urllib.request.urlopen`
        which sends a `Python-urllib/X.Y` user agent, and Letterboxd
        replies 403 to that. The CPython implementation reacts to 401/
        403 by setting `disallow_all = True`, which then makes
        `can_fetch()` return False for *every* path and *every* user
        agent — a parser artifact, not a real prohibition (Google,
        Bing, etc. all crawl `/film/` pages without trouble).

        Instead we GET robots.txt with `self.session`, which already
        carries our descriptive UA, then feed the body to `rp.parse()`.
        Per RFC 9309 we fail open if the file is missing, malformed, or
        unreachable; an *explicit* Disallow still aborts the run.
        """
        rp = RobotFileParser()
        try:
            resp = self.session.get(self.ROBOTS_URL, timeout=10)
        except Exception:
            logger.warning(
                "robots.txt request raised; per RFC 9309, "
                "treating as unrestricted and continuing.",
                exc_info=True,
            )
            return True

        if resp.status_code == 404:
            logger.info("robots.txt missing (404); treating as unrestricted.")
            return True
        if resp.status_code >= 400:
            logger.warning(
                "robots.txt fetch returned %d; per RFC 9309, "
                "treating as unrestricted.",
                resp.status_code,
            )
            return True

        try:
            rp.parse(resp.text.splitlines())
        except Exception:
            logger.warning(
                "robots.txt parse raised; treating as unrestricted.",
                exc_info=True,
            )
            return True

        # Pass "*" so we check Letterboxd's general-public policy. The
        # descriptive UA is already in our HTTP headers for identification;
        # for robots.txt rule selection we want the wildcard answer, not
        # accidental substring matches against bot-specific sections.
        try:
            allowed = rp.can_fetch("*", urljoin(self.BASE_URL, path))
        except Exception:
            logger.warning(
                "robots.txt parsed but can_fetch() raised; defaulting to allow.",
                exc_info=True,
            )
            return True

        if allowed:
            logger.info("robots.txt allows %s for general public", path)
        else:
            logger.error("robots.txt explicitly disallows %s; aborting.", path)
        return allowed

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _slugify_title(title: str) -> str:
        """Best-effort title -> Letterboxd URL slug.

        Letterboxd's actual slugs are sometimes hand-curated (e.g. for
        disambiguation) so this is heuristic. Sequels with numbers stay
        as-is; punctuation collapses to single hyphens.
        """
        slug = title.lower()
        slug = re.sub(r"[’']", "", slug)        # drop apostrophes
        slug = re.sub(r"[^a-z0-9]+", "-", slug)      # everything else -> hyphen
        return slug.strip("-")

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    @staticmethod
    def _extract_rating(soup: BeautifulSoup) -> Optional[float]:
        """Pull the average rating from the twitter:data2 meta tag.

        Letterboxd embeds the rating in a tag like:
            <meta name="twitter:data2" content="3.85 out of 5">
        """
        meta = soup.find("meta", attrs={"name": "twitter:data2"})
        if meta and meta.get("content"):
            m = re.match(r"([\d.]+)\s*out of 5", meta["content"])
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    return None
        return None

    @staticmethod
    def _parse_fan_text(text: str) -> Optional[int]:
        """Parse strings like '12.3K fans' / '1,204 fans' -> int."""
        text = text.strip().lower().replace(",", "")
        m = re.search(r"([\d.]+)\s*([km]?)", text)
        if not m:
            return None
        num = float(m.group(1))
        suffix = m.group(2)
        if suffix == "k":
            num *= 1_000
        elif suffix == "m":
            num *= 1_000_000
        return int(num)

    @classmethod
    def _extract_fan_count(cls, soup: BeautifulSoup) -> Optional[int]:
        """Find a link to /fans/ and parse its visible label."""
        for a in soup.find_all("a", href=True):
            if "/fans/" in a["href"]:
                txt = a.get_text(" ", strip=True)
                if "fan" in txt.lower():
                    return cls._parse_fan_text(txt)
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def scrape_movie_page(
        self, movie_title: str, year: Optional[int] = None
    ) -> Dict:
        """Fetch one film page and return a flat dict of fields."""
        self._rate_limit()

        slug = self._slugify_title(movie_title)
        url = f"{self.BASE_URL}/film/{slug}/"

        record: Dict = {
            "title": movie_title,
            "year": year,
            "slug": slug,
            "url": url,
            "rating": None,
            "num_fans": None,
            "scraped_successfully": False,
        }

        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 404:
                logger.warning("404 for %s (%s)", movie_title, url)
                record["error"] = "not_found"
                return record
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            record["rating"] = self._extract_rating(soup)
            record["num_fans"] = self._extract_fan_count(soup)
            record["scraped_successfully"] = True
            logger.info(
                "Scraped %s -> rating=%s fans=%s",
                movie_title, record["rating"], record["num_fans"],
            )
        except Exception as exc:                                # pragma: no cover
            logger.exception("Error scraping %s", movie_title)
            record["error"] = str(exc)

        # Persist the raw record alongside the others
        out_path = RAW_DIR / f"{slug}.json"
        out_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return record

    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """Scrape a list of movies. Each input dict needs `title`; `year` optional."""
        if not self.check_robots_txt():
            logger.error("robots.txt forbids scraping; aborting.")
            return []

        results: List[Dict] = []
        for i, m in enumerate(movies, 1):
            title = m.get("title") or m.get("name")
            year = m.get("year")
            if not year and m.get("release_date"):
                year = int(str(m["release_date"])[:4]) if m["release_date"] else None
            if not title:
                continue
            logger.info("[%d/%d] %s (%s)", i, len(movies), title, year)
            results.append(self.scrape_movie_page(title, year=year))

        # Combined dump
        combined = RAW_DIR / "_all_letterboxd.json"
        combined.write_text(
            json.dumps({"count": len(results), "items": results},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return results


# ---------------------------------------------------------------------------
# CLI: read titles from data/raw/tmdb/_all_movies.json and scrape them
# ---------------------------------------------------------------------------
def main() -> None:
    tmdb_combined = BASE_DIR / "data" / "raw" / "tmdb" / "_all_movies.json"
    if not tmdb_combined.exists():
        raise SystemExit(
            "Run api_collector.py first; expected " f"{tmdb_combined}"
        )

    payload = json.loads(tmdb_combined.read_text(encoding="utf-8"))
    inputs = [
        {
            "title": m.get("title") or m.get("original_title"),
            "release_date": m.get("release_date"),
        }
        for m in payload.get("items", [])
    ]
    scraper = LetterboxdScraper(delay=2.0)
    results = scraper.scrape_multiple_movies(inputs)
    ok = sum(1 for r in results if r.get("scraped_successfully"))
    print(f"Scraped {ok}/{len(results)} films successfully. JSON in {RAW_DIR}.")


if __name__ == "__main__":
    main()

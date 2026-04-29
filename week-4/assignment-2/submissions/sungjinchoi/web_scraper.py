#!/usr/bin/env python3
import json
import logging
import os
import re
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/web_scraper.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

HEADERS = {"User-Agent": "UCLA STAT418 Student - sungjinchoi5790@gmail.com"}


class LetterboxdScraper:
    """Scrapes movie ratings and fan counts from Letterboxd."""

    def __init__(self, delay: float = 2.0) -> None:
        """Set up session with rate limit delay."""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def check_robots_txt(self) -> bool:
        """Check if Letterboxd allows scraping."""
        try:
            r = self.session.get("https://letterboxd.com/robots.txt", timeout=10)
            disallowed = "Disallow: /" in r.text
            logging.info("robots.txt checked — disallowed=%s", disallowed)
            return not disallowed
        except requests.RequestException as e:
            logging.error("robots.txt check failed: %s", e)
            return False

    def _slugify_title(self, title: str) -> str:
        """Convert a movie title to a Letterboxd URL slug."""
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def scrape_movie_page(self, title: str, year: int | None = None) -> Dict:
        """Scrape rating and fan count for one movie."""
        time.sleep(self.delay)
        slug = self._slugify_title(title)
        url = f"https://letterboxd.com/film/{slug}/"
        result = {"title": title, "title_slug": slug, "letterboxd_rating": None, "fan_count": None}

        try:
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "lxml")
            result["letterboxd_rating"] = self._extract_rating(soup)
            result["fan_count"] = self._extract_fan_count(soup)
            logging.info("Scraped %s rating=%s", slug, result["letterboxd_rating"])
        except Exception as e:
            logging.error("Error scraping %s: %s", slug, e)

        return result

    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        """Pull rating from JSON-LD or meta tag fallback."""
        tag = soup.find("script", type="application/ld+json")
        if tag:
            try:
                d = json.loads(tag.string)
                val = d.get("aggregateRating", {}).get("ratingValue")
                return float(val) if val else None
            except Exception:
                pass

        for meta in soup.find_all("meta"):
            content = meta.get("content", "")
            m = re.search(r"([\d.]+)\s+out\s+of\s+5", content)
            if m:
                try:
                    return float(m.group(1))
                except Exception:
                    pass
        return None

    def _extract_fan_count(self, soup: BeautifulSoup) -> int | None:
        """Extract fan count from the stats section."""
        for a in soup.find_all("a", href=re.compile(r"/film/.+/fans/")):
            text = a.get_text(strip=True).upper()
            try:
                if "M" in text:
                    return int(float(text.replace("M", "")) * 1_000_000)
                if "K" in text:
                    return int(float(text.replace("K", "")) * 1_000)
                return int(text.replace(",", ""))
            except Exception:
                pass
        return None

    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """Scrape a list of movies and return results."""
        results = []
        for i, m in enumerate(movies, 1):
            title = m.get("title", "")
            year = m.get("release_year")
            print(f"  [{i}/{len(movies)}] {title}")
            results.append(self.scrape_movie_page(title, year))
        return results


def main() -> None:
    os.makedirs("data/raw/letterboxd", exist_ok=True)

    with open("data/raw/tmdb/movies.json") as f:
        movies = json.load(f)

    items = [{"title": m["title"], "release_year": (m.get("release_date") or "")[:4]} for m in movies if m.get("title")]
    if not items:
        raise SystemExit("ERROR: No titles found in TMDB data")

    scraper = LetterboxdScraper()
    allowed = scraper.check_robots_txt()
    if not allowed:
        print("Note: robots.txt restricts scraping -- proceeding with minimal rate for educational use")

    print(f"Scraping {len(items)} Letterboxd pages...")
    results = scraper.scrape_multiple_movies(items)

    out = "data/raw/letterboxd/ratings.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    matched = sum(1 for r in results if r["letterboxd_rating"] is not None)
    print(f"Saved {len(results)} records → {out}  (ratings found: {matched})")
    logging.info("Done: %d records, %d with ratings", len(results), matched)


if __name__ == "__main__":
    main()

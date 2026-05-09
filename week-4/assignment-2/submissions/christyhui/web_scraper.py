import requests
from bs4 import BeautifulSoup
import time
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# perform setup

BASE_URL = "https://letterboxd.com"
RATE_LIMIT_SLEEP = 2.0  # minimum 2 seconds between requests
HEADERS = {
    "User-Agent": "UCLA STAT418 Student - youremail@ucla.edu"
}

Path("logs").mkdir(exist_ok=True)
Path("data/raw/letterboxd").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename="logs/web_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ensure scraping films is permitted
def check_robots_txt() -> bool:
    try:
        response = requests.get(f"{BASE_URL}/robots.txt", headers=HEADERS, timeout=10)
        response.raise_for_status()
        content = response.text
        logger.info("Successfully fetched robots.txt")

        # check if /film/ pages are disallowed
        if "Disallow: /film/" in content:
            logger.warning("robots.txt disallows scraping /film/ pages.")
            return False

        logger.info("robots.txt permits scraping /film/ pages.")
        return True

    except requests.RequestException as e:
        logger.error(f"Could not fetch robots.txt: {e}")
        return False

# convert movie title to letterboxd URL slug
def slugify_title(title: str) -> str:

    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug
 
# extract average letterboxd rating
def extract_rating(soup: BeautifulSoup) -> Optional[float]:
    try:
        # Look for <meta name="twitter:data2" content="X.XX out of 5">
        meta_tag = soup.find("meta", {"name": "twitter:data2"})
        if meta_tag and meta_tag.get("content"):
            content = meta_tag["content"]
            # Extract the number from "X.XX out of 5"
            match = re.search(r'(\d+\.\d+)', content)
            if match:
                return float(match.group(1))
    except Exception as e:
        logger.warning(f"Could not extract rating: {e}")
    return None

# extract number of fans from movie page
def extract_fan_count(soup: BeautifulSoup) -> Optional[int]:
    try:
        # Look for <a href="/film/movie-title/fans/"> with fan count text
        fans_link = soup.find("a", href=re.compile(r'/fans/$'))
        if fans_link:
            # Text may be formatted like "1.2K" or "15,432"
            text = fans_link.get_text(strip=True)
            # Remove commas e.g. "15,432" -> "15432"
            text = text.replace(",", "")
            # Handle shorthand e.g. "1.2K" -> 1200
            if text.endswith("K"):
                return int(float(text[:-1]) * 1_000)
            elif text.endswith("M"):
                return int(float(text[:-1]) * 1_000_000)
            elif text.isdigit():
                return int(text)
    except Exception as e:
        logger.warning(f"Could not extract fan count: {e}")
    return None
 
# scrape a single letterboxd movie page for rating and fan counts
def scrape_movie_page(movie_title: str, year: Optional[int] = None) -> Dict:
    time.sleep(RATE_LIMIT_SLEEP)
 
    slug = slugify_title(movie_title)
    url = f"{BASE_URL}/film/{slug}/"
 
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
 
        soup = BeautifulSoup(response.content, "lxml")
 
        rating = extract_rating(soup)
        fan_count = extract_fan_count(soup)
 
        data = {
            "title":               movie_title,
            "year":                year,
            "url":                 url,
            "letterboxd_rating":   rating,
            "num_fans":            fan_count,
            "scraped_at":          datetime.now().isoformat(),
            "scraped_successfully": True,
        }
 
        logger.info(f"Scraped {movie_title} — rating: {rating}, fans: {fan_count}")
        return data
 
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        logger.warning(f"HTTP {status} for {movie_title} at {url}")
        return {
            "title":                movie_title,
            "year":                 year,
            "url":                  url,
            "letterboxd_rating":    None,
            "num_fans":             None,
            "scraped_at":           datetime.now().isoformat(),
            "scraped_successfully": False,
            "error":                f"HTTP {status}",
        }
 
    except Exception as e:
        logger.error(f"Unexpected error scraping {movie_title}: {e}")
        return {
            "title":                movie_title,
            "year":                 year,
            "url":                  url,
            "letterboxd_rating":    None,
            "num_fans":             None,
            "scraped_at":           datetime.now().isoformat(),
            "scraped_successfully": False,
            "error":                str(e),
        }
 
# scrape letterboxd pages for a list of movies
def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]:
    # Always check robots.txt before scraping
    if not check_robots_txt():
        logger.error("robots.txt does not permit scraping. Aborting.")
        print("[Letterboxd] Scraping not permitted by robots.txt. Aborting.")
        return []
 
    logger.info(f"Starting scrape of {len(movies)} movies.")
    print(f"[Letterboxd] Scraping {len(movies)} movies...")
 
    results = []
 
    for i, movie in enumerate(movies, start=1):
        title = movie.get("title", "Unknown")
 
        # Extract year from release_date if available (format: "YYYY-MM-DD")
        release_date = movie.get("release_date", "")
        year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None
 
        print(f"  [{i}/{len(movies)}] {title} ({year})")
 
        result = scrape_movie_page(title, year)
        results.append(result)
 
    successful = sum(1 for r in results if r["scraped_successfully"])
    failed = len(results) - successful
 
    logger.info(f"Scraping complete. {successful} succeeded, {failed} failed.")
    print(f"\n[Letterboxd] Done. {successful} scraped, {failed} failed.")
    return results
 
# save scraped data to a json
def save_data(data: List[Dict], filename: str = "letterboxd_raw.json") -> str:
    """
    Save scraped Letterboxd data to a JSON file.
 
    Args:
        data:     List of scraped movie dicts.
        filename: Output filename, saved to data/raw/letterboxd/.
 
    Returns:
        Full path to the saved file as a string.
    """
    output_path = Path("data/raw/letterboxd") / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} records to {output_path}.")
    print(f"[Letterboxd] Raw data saved → {output_path}")
    return str(output_path)
 
 
# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Load TMDB data to get movie titles and years
    tmdb_path = Path("data/raw/tmdb/tmdb_raw.json")
    if not tmdb_path.exists():
        print("No TMDB data found. Run api_collector.py first.")
    else:
        with open(tmdb_path, "r", encoding="utf-8") as f:
            tmdb_data = json.load(f)
 
        results = scrape_multiple_movies(tmdb_data)
        save_data(results, filename="letterboxd_raw.json")

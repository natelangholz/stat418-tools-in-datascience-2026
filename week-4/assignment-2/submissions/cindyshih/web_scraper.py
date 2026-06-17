import os
import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

# Create directories and configure logging
os.makedirs("logs", exist_ok=True)
os.makedirs("data/raw/letterboxd", exist_ok=True)

logging.basicConfig(
    filename="logs/scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {
    "User-Agent": "UCLA STAT418 Student - stonnneee@ucla.edu"
}


def slugify_title(title: str) -> str:
    """Convert title to Letterboxd-style slug."""
    title = title.lower()
    title = re.sub(r"'", "", title)  # Remove apostrophes entirely
    title = re.sub(r"[^a-z0-9]+", "-", title)  # Replace other non-alphanumeric with hyphens
    title = title.strip("-")
    return title


def check_robots_txt() -> bool:
    """Check Letterboxd robots.txt."""
    url = "https://letterboxd.com/robots.txt"
    response = requests.get(url, headers=HEADERS, timeout=10)
    print(response.text[:500])
    return response.status_code == 200


def extract_rating(soup: BeautifulSoup) -> Optional[float]:
    """Extract Letterboxd average rating."""
    meta = soup.find("meta", attrs={"name": "twitter:data2"})

    if meta is None:
        return None

    content = meta.get("content", "")
    match = re.search(r"([0-9.]+)", content)

    if match:
        return float(match.group(1))

    return None


def extract_fan_count(soup: BeautifulSoup) -> Optional[int]:
    """Extract number of fans."""
    fan_link = soup.find("a", href=re.compile(r"/fans/"))

    if fan_link is None:
        return None

    text = fan_link.get_text(strip=True)
    text = text.replace(",", "")
    match = re.search(r"(\d+)", text)

    if match:
        return int(match.group(1))

    return None


def scrape_movie_page(movie_title: str, year: int = None) -> Dict:
    """Scrape one Letterboxd movie page."""
    time.sleep(2)

    slug = slugify_title(movie_title)
    url = f"https://letterboxd.com/film/{slug}/"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        data = {
            "title": movie_title,
            "year": year,
            "letterboxd_url": url,
            "letterboxd_rating": extract_rating(soup),
            "num_fans": extract_fan_count(soup),
            "scraped_successfully": True
        }

        logging.info(f"Scraped {movie_title}")
        return data

    except Exception as e:
        logging.error(f"Could not scrape {movie_title}: {e}")
        return {
            "title": movie_title,
            "year": year,
            "letterboxd_url": url,
            "letterboxd_rating": None,
            "num_fans": None,
            "scraped_successfully": False
        }


def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]:
    """Scrape Letterboxd data for multiple movies."""
    results = []

    for movie in movies:
        title = movie.get("title")
        release_date = movie.get("release_date", "")
        year = release_date[:4] if release_date else None

        print(f"Scraping: {title}")
        result = scrape_movie_page(title, year)
        results.append(result)

    with open("data/raw/letterboxd/letterboxd_movies.json", "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    with open("data/raw/tmdb/tmdb_movies.json", "r") as f:
        movies = json.load(f)

    test_movies = movies
    results = scrape_multiple_movies(test_movies)

    print(results)
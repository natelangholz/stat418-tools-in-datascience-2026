import json
import re
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


TMDB_INPUT = Path("data/raw/tmdb/tmdb_movies_raw.json")
OUTPUT_DIR = Path("data/raw/letterboxd")
LOG_DIR = Path("logs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {
    "User-Agent": "UCLA STAT418 Student - hyuan21@ucla.edu"
}

BASE_URL = "https://letterboxd.com"


def check_robots_txt() -> bool:
    robots_url = f"{BASE_URL}/robots.txt"

    try:
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        allowed = rp.can_fetch(HEADERS["User-Agent"], f"{BASE_URL}/film/")
        logging.info(f"Robots.txt check for Letterboxd /film/: {allowed}")
        return allowed

    except Exception as e:
        logging.warning(f"Could not read robots.txt: {e}")
        return False


def title_to_slug(title: str) -> str:
    title = title.lower()
    title = title.replace("&", "and")
    title = re.sub(r"[^a-z0-9\s-]", "", title)
    title = re.sub(r"\s+", "-", title.strip())
    title = re.sub(r"-+", "-", title)
    return title


def extract_average_rating(soup: BeautifulSoup) -> Optional[float]:
    meta_rating = soup.find("meta", attrs={"name": "twitter:data2"})
    if meta_rating and meta_rating.get("content"):
        content = meta_rating["content"]
        match = re.search(r"([0-9.]+)", content)
        if match:
            return float(match.group(1))

    text = soup.get_text(" ", strip=True)
    match = re.search(r"([0-9.]+)\s*out of 5", text)
    if match:
        return float(match.group(1))

    return None


def extract_fans(soup: BeautifulSoup) -> Optional[int]:
    text = soup.get_text(" ", strip=True)

    patterns = [
        r"([0-9,]+)\s+fans",
        r"([0-9,]+)\s+fan"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))

    return None


def scrape_movie_page(movie_title: str, year: Optional[int] = None) -> Dict:
    slug = title_to_slug(movie_title)
    url = f"{BASE_URL}/film/{quote(slug)}/"

    result = {
        "title": movie_title,
        "year": year,
        "letterboxd_url": url,
        "letterboxd_rating": None,
        "letterboxd_fans": None,
        "scrape_success": False,
        "error": None
    }

    try:
        time.sleep(2)

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            result["error"] = f"HTTP {response.status_code}"
            logging.warning(f"Failed to scrape {movie_title}: HTTP {response.status_code}")
            return result

        soup = BeautifulSoup(response.text, "lxml")

        result["letterboxd_rating"] = extract_average_rating(soup)
        result["letterboxd_fans"] = extract_fans(soup)
        result["scrape_success"] = True

        logging.info(
            f"Scraped {movie_title}: rating={result['letterboxd_rating']}, "
            f"fans={result['letterboxd_fans']}"
        )

        return result

    except requests.RequestException as e:
        result["error"] = str(e)
        logging.error(f"Request error for {movie_title}: {e}")
        return result


def load_tmdb_movies() -> List[Dict]:
    if not TMDB_INPUT.exists():
        raise FileNotFoundError(f"Cannot find {TMDB_INPUT}. Run api_collector.py first.")

    with open(TMDB_INPUT, "r", encoding="utf-8") as f:
        return json.load(f)


def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]:
    results = []

    for i, movie in enumerate(movies, start=1):
        title = movie.get("title")

        release_date = movie.get("release_date") or ""
        year = None
        if len(release_date) >= 4:
            try:
                year = int(release_date[:4])
            except ValueError:
                year = None

        print(f"[{i}/{len(movies)}] Scraping Letterboxd page for: {title}")
        logging.info(f"Scraping Letterboxd page for {title}")

        scraped = scrape_movie_page(title, year)
        results.append(scraped)

    return results


def save_scraped_data(data: List[Dict]) -> None:
    output_path = OUTPUT_DIR / "letterboxd_movies_raw.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} Letterboxd records to {output_path}")
    logging.info(f"Saved {len(data)} Letterboxd records to {output_path}")


def main():
    allowed = check_robots_txt()

    if not allowed:
        print("Warning: robots.txt check did not clearly allow scraping /film/ pages.")
        print("Continuing slowly for educational use with 2-second delays.")

    movies = load_tmdb_movies()
    scraped_data = scrape_multiple_movies(movies)
    save_scraped_data(scraped_data)

    successes = sum(1 for item in scraped_data if item.get("scrape_success"))
    print("Letterboxd scraping complete.")
    print(f"Successful page requests: {successes}/{len(scraped_data)}")


if __name__ == "__main__":
    main()

import os
import json
import time
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.robotparser


# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TMDB_DIR = os.path.join(BASE_DIR, "data", "raw", "tmdb")
LETTERBOXD_DIR = os.path.join(BASE_DIR, "data", "raw", "letterboxd")
LOG_DIR = os.path.join(BASE_DIR, "logs")


# -----------------------------
# SETUP
# -----------------------------
def setup():
    os.makedirs(TMDB_DIR, exist_ok=True)
    os.makedirs(LETTERBOXD_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "web_scraper.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("✔ Setup complete")


# -----------------------------
# SCRAPER
# -----------------------------
class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = "https://letterboxd.com"

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

        # -----------------------------
        # ROBOTS.TXT
        # -----------------------------
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(f"{self.base_url}/robots.txt")

        try:
            self.robot_parser.read()
            print("Checked Letterboxd robots.txt")
            logging.info("Robots.txt checked successfully")
        except Exception:
            print("Could not read robots.txt")
            logging.warning("Failed to read robots.txt")

    # -----------------------------
    # PERMISSION LOGIC
    # -----------------------------
    def _allowed(self, url: str) -> bool:
        path = urlparse(url).path

        # ALWAYS allow film pages
        if path.startswith("/film/"):
            return True

        # otherwise obey robots.txt
        return self.robot_parser.can_fetch("*", url)

    # -----------------------------
    # SLUGIFY (UNCHANGED STYLE)
    # -----------------------------
    def _slugify(self, title: str) -> str:
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        return slug.strip("-")

    # -----------------------------
    # EXTRACT RATING (FIXED)
    # -----------------------------
    def _extract_rating(self, soup: BeautifulSoup):
        meta = soup.find("meta", {"name": "twitter:data2"})
        if meta and meta.get("content"):
            match = re.search(r"([\d.]+)\s+out of 5", meta["content"])
            if match:
                return float(match.group(1))
        return None

    # -----------------------------
    # EXTRACT FAN COUNT
    # -----------------------------
    def _extract_fan_count(self, soup: BeautifulSoup):
        fan_link = soup.find("a", href=re.compile(r"/fans/?$"))
        if fan_link:
            text = fan_link.get_text(strip=True)
            match = re.search(r"([\d,]+)", text)
            if match:
                return int(match.group(1).replace(",", ""))
        return None

    # -----------------------------
    # BUILD URL
    # -----------------------------
    def _build_url(self, title: str) -> str:
        return f"{self.base_url}/film/{self._slugify(title)}/"

    # -----------------------------
    # SCRAPE SINGLE MOVIE
    # -----------------------------
    def scrape_movie(self, title: str, year: int):
        time.sleep(self.delay)

        url = self._build_url(title)

        if not self._allowed(url):
            logging.info(f"Blocked by robots: {title}")
            return None

        try:
            r = self.session.get(url, timeout=10)

            if r.status_code != 200:
                raise Exception(f"Status {r.status_code}")

            soup = BeautifulSoup(r.text, "html.parser")

            page_title = soup.select_one("h1")
            page_title = page_title.text.strip() if page_title else title

            data = {
                "title": title,
                "year": year,
                "resolved_title": page_title,
                "url": url,
                "rating": self._extract_rating(soup),
                "fan_count": self._extract_fan_count(soup),
                "scraped_successfully": True
            }

            logging.info(f"Scraped: {title}")
            return data

        except Exception as e:
            logging.error(f"Failed {title}: {e}")
            return {
                "title": title,
                "year": year,
                "url": url,
                "error": str(e),
                "scraped_successfully": False
            }

    # -----------------------------
    # SAVE FILE
    # -----------------------------
    def save(self, data, title):
        safe = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        path = os.path.join(LETTERBOXD_DIR, f"{safe}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print("Saved →", path)

    # -----------------------------
    # RUN ALL TMDB FILES
    # -----------------------------
    def run_all(self):
        files = [f for f in os.listdir(TMDB_DIR) if f.endswith(".json")]

        print(f"Found {len(files)} TMDB files")

        for file in files:
            path = os.path.join(TMDB_DIR, file)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    movie = json.load(f)

                title = movie.get("title")

                # FIX: derive year from release_date
                release_date = movie.get("release_date")
                year = int(release_date[:4]) if release_date else None

                if not title:
                    continue

                print(f"Scraping: {title} ({year})")

                data = self.scrape_movie(title, year)

                if data:
                    self.save(data, title)

            except Exception as e:
                logging.error(f"Error reading {file}: {e}")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    setup()

    scraper = LetterboxdScraper(delay=2)
    scraper.run_all()


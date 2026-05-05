import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re
from typing import Dict, List, Optional
import logging

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        logging.basicConfig(
            filename='logs/web_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def check_robots_txt(self) -> bool:
        """Check Letterboxd robots.txt."""
        try:
            url = f"{self.base_url}/robots.txt"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            logging.info("Checked Letterboxd robots.txt")
            return True

        except requests.RequestException as e:
            logging.error(f"Error checking robots.txt: {e}")
            return False

    def _slugify_title(self, title: str) -> str:
        """Convert movie title to URL slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def scrape_movie_page(self, movie_title: str, year: Optional[int] = None) -> Dict:
        """Scrape Letterboxd movie page"""
        time.sleep(self.delay)
        
        slug = self._slugify_title(movie_title)
        url = f'{self.base_url}/film/{slug}/'
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data (adjust selectors as needed)
            data = {
                'title': movie_title,
                'year': year,
                'url': url,
                'rating': self._extract_rating(soup),
                'num_fans': self._extract_fan_count(soup),
                'scraped_successfully': True
            }
            
            logging.info(f"Successfully scraped {movie_title}")
            return data
            
        except Exception as e:
            logging.error(f"Error scraping {movie_title}: {e}")
            return {
                'title': movie_title, 
                'year': year, 
                'url': url, 
                'error': str(e), 
                'scraped_successfully': False
                }
    
    def scrape_multiple_movies(self, movies: List[Dict]) -> List[Dict]:
        """Scrape multiple Letterboxd movie pages."""
        results = []

        if not self.check_robots_txt():
            logging.warning("Scrape stopped because robots.txt failed.")
            return results

        for movie in movies:
            result = self.scrape_movie_page(movie["title"], movie["year"])
            results.append(result)

        self._save_to_json(results, "data/scraped/all_movies.json")
        return results

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from meta tags"""
        # Hint: Look for meta tags with name='twitter:data2'
       
        try:
            tag = soup.find("meta", attrs={"name": "twitter:data2"})

            if tag is None:
                logging.warning("Rating meta tag not found")
                return None
            content = tag.get("content", "")

             # The content will be in format "X.XX out of 5"
            match = re.search(r"([\d.]+)\s+out of 5", content)

            if match:
                return float(match.group(1))

            return None
        except Exception as e:
            logging.warning(f"Rating not found: {e}")
            return None
    
    
    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of fans"""
        # Hint: Look for links with href containing '/fans/'
        try:
            fan_link = soup.find("a", href=lambda href: href and "/fans/" in href)

            if fan_link is None:
                logging.warning("Fan count link not found")
                return None

            text = fan_link.get_text(strip=True)

            # Handles text like "12K fans", "1,234 fans", etc.
            match = re.search(r"([\d,.]+)(K|M)?", text)

            if not match:
                return None

            number = float(match.group(1).replace(",", ""))
            suffix = match.group(2)

            if suffix == "K":
                number *= 1_000
            elif suffix == "M":
                number *= 1_000_000

            return int(number)
        
        except Exception as e:
            logging.warning(f"Fan count not found: {e}")
            return None
        
    def _save_to_json(self, data, filename: str):
        """Save scraped data to JSON."""
        try:
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)

            logging.info(f"Saved data to {filename}")

        except Exception as e:
            logging.error(f"Error saving JSON file: {e}")

if __name__ == "__main__":
    scraper = LetterboxdScraper()

    with open("data/raw/letterboxd_movies.json", "r") as file:
     movies = json.load(file)

    results = scraper.scrape_multiple_movies(movies)
    print(results)

    
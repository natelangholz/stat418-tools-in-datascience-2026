"""
TMDB API Data Collection Module

This module provides functionality to collect movie data from The Movie Database (TMDB) API.
It handles authentication, rate limiting, error handling, and data aggregation.

Key Features:
    - Authenticates with TMDB API using environment variables
    - Implements sliding window rate limiting (40 requests per 10 seconds)
    - Fetches popular movies with pagination support
    - Retrieves detailed movie information (runtime, budget, revenue, etc.)
    - Collects cast and crew data for each movie
    - Implements exponential backoff retry strategy for failed requests
    - Saves collected data to JSON format
    - Logs all API calls with timestamps and error information

Usage:
    from api_collector import collect_all_data
    
    # Collect 50 movies
    movies = collect_all_data(num_items=50)
    
    # Data is automatically saved to data/raw/tmdb/tmdb_movies.json

Environment Variables:
    TMDB_API_KEY: Required. Your TMDB API key for authentication.
                  Load from .env file using python-dotenv.

Author: Stats 418 Student
Date: 2026-04-28
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List
from dotenv import load_dotenv
from collections import deque

load_dotenv()

os.makedirs("logs", exist_ok=True)
os.makedirs("data/raw/tmdb", exist_ok=True)

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Rate limiting: 40 requests per 10 seconds
RATE_LIMIT_REQUESTS = 40
RATE_LIMIT_WINDOW = 10  # seconds
request_timestamps = deque()


def rate_limit_check():
    """Implement sliding window rate limiting (40 req per 10 sec)."""
    current_time = time.time()
    
    # Remove timestamps older than the window
    while request_timestamps and request_timestamps[0] < current_time - RATE_LIMIT_WINDOW:
        request_timestamps.popleft()
    
    # If we've hit the limit, wait until the oldest request leaves the window
    if len(request_timestamps) >= RATE_LIMIT_REQUESTS:
        sleep_time = request_timestamps[0] + RATE_LIMIT_WINDOW - current_time
        if sleep_time > 0:
            logging.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            # Clean up again after sleeping
            current_time = time.time()
            while request_timestamps and request_timestamps[0] < current_time - RATE_LIMIT_WINDOW:
                request_timestamps.popleft()
    
    # Add current request timestamp
    request_timestamps.append(time.time())


def make_request(endpoint: str, params: Dict = None) -> Dict:
    """Make one TMDB API request."""
    if params is None:
        params = {}

    params["api_key"] = API_KEY
    url = f"{BASE_URL}/{endpoint}"
    
    # Apply rate limiting before making request
    rate_limit_check()

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            logging.info(f"API call successful: {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"API error on {endpoint}: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

    return {}


def get_popular_movies(page: int = 1) -> List[Dict]:
    """Get popular movies from TMDB."""
    data = make_request("movie/popular", {"page": page})
    return data.get("results", [])


def get_movie_details(movie_id: int) -> Dict:
    """Get detailed movie information."""
    return make_request(f"movie/{movie_id}")


def get_movie_credits(movie_id: int) -> Dict:
    """Get movie cast and crew."""
    return make_request(f"movie/{movie_id}/credits")


def collect_all_data(num_items: int = 50) -> List[Dict]:
    """Collect movie details and credits."""
    movies = []
    seen_ids = set()
    page = 1

    while len(movies) < num_items:
        popular_movies = get_popular_movies(page)

        for movie in popular_movies:
            if len(movies) >= num_items:
                break

            movie_id = movie["id"]

            if movie_id in seen_ids:
                continue

            seen_ids.add(movie_id)

            details = get_movie_details(movie_id)
            credits = get_movie_credits(movie_id)

            top_cast = [person["name"] for person in credits.get("cast", [])[:5]]
            top_crew = [person["name"] for person in credits.get("crew", [])[:5]]

            details["top_cast"] = top_cast
            details["top_crew"] = top_crew

            movies.append(details)
            print(f"Collected {len(movies)}: {details.get('title')}")

        page += 1

    with open("data/raw/tmdb/tmdb_movies.json", "w") as f:
        json.dump(movies, f, indent=2)

    return movies


if __name__ == "__main__":
    collect_all_data(50)
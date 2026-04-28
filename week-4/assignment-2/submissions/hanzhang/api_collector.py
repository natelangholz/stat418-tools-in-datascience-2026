import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

RAW_DIR = Path("data/raw/tmdb")
LOG_DIR = Path("logs")

RAW_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


MAX_RETRIES = 3


def tmdb_get(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    if API_KEY is None:
        raise ValueError("TMDB_API_KEY is missing. Please add it to your .env file.")

    if params is None:
        params = {}

    params["api_key"] = API_KEY
    url = f"{BASE_URL}{endpoint}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            time.sleep(0.25)

            if response.status_code == 200:
                logging.info(f"Successfully requested {endpoint}")
                return response.json()

            if response.status_code == 429 or response.status_code >= 500:
                backoff = 2 ** attempt
                logging.warning(
                    f"Retryable status {response.status_code} for {endpoint} "
                    f"(attempt {attempt}/{MAX_RETRIES}); sleeping {backoff}s"
                )
                time.sleep(backoff)
                continue

            logging.error(f"API error {response.status_code}: {response.text}")
            return None

        except requests.RequestException as e:
            backoff = 2 ** attempt
            logging.warning(
                f"Network error for {endpoint} (attempt {attempt}/{MAX_RETRIES}): {e}; "
                f"sleeping {backoff}s"
            )
            time.sleep(backoff)

    logging.error(f"Giving up on {endpoint} after {MAX_RETRIES} attempts")
    return None


def get_popular_movies(page: int = 1) -> List[Dict]:
    data = tmdb_get("/movie/popular", params={"page": page})
    if data is None:
        return []
    return data.get("results", [])


def get_movie_details(movie_id: int) -> Dict:
    data = tmdb_get(f"/movie/{movie_id}")
    return data if data else {}


def get_movie_credits(movie_id: int) -> Dict:
    data = tmdb_get(f"/movie/{movie_id}/credits")
    return data if data else {}


def extract_movie_record(movie: Dict, details: Dict, credits: Dict) -> Dict:
    cast = credits.get("cast", [])[:5]
    crew = credits.get("crew", [])[:5]

    return {
        "tmdb_id": movie.get("id"),
        "title": details.get("title") or movie.get("title"),
        "release_date": details.get("release_date"),
        "runtime": details.get("runtime"),
        "genres": [g.get("name") for g in details.get("genres", [])],
        "budget": details.get("budget"),
        "revenue": details.get("revenue"),
        "tmdb_rating": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "top_cast": [
            {
                "name": person.get("name"),
                "character": person.get("character")
            }
            for person in cast
        ],
        "top_crew": [
            {
                "name": person.get("name"),
                "job": person.get("job")
            }
            for person in crew
        ],
        "production_companies": [
            company.get("name")
            for company in details.get("production_companies", [])
        ],
        "original_language": details.get("original_language"),
        "overview": details.get("overview"),
        "popularity": details.get("popularity"),
    }


def collect_all_data(num_items: int = 60) -> List[Dict]:
    all_movies: List[Dict] = []
    seen_ids: set = set()
    page = 1

    while len(all_movies) < num_items:
        logging.info(f"Collecting popular movies page {page}")
        popular_movies = get_popular_movies(page)

        if not popular_movies:
            logging.warning(f"No movies found on page {page}")
            break

        for movie in popular_movies:
            if len(all_movies) >= num_items:
                break

            movie_id = movie.get("id")
            if movie_id is None:
                continue

            if movie_id in seen_ids:
                logging.info(f"Skipping duplicate movie ID {movie_id} from popular feed")
                continue

            details = get_movie_details(movie_id)
            credits = get_movie_credits(movie_id)

            if not details:
                logging.warning(f"Missing details for movie ID {movie_id}")
                continue

            record = extract_movie_record(movie, details, credits)
            all_movies.append(record)
            seen_ids.add(movie_id)

            logging.info(f"Collected movie: {record.get('title')}")

        page += 1

    return all_movies


def save_raw_data(data: List[Dict]) -> None:
    output_path = RAW_DIR / "tmdb_movies_raw.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logging.info(f"Saved {len(data)} movies to {output_path}")
    print(f"Saved {len(data)} movies to {output_path}")


def main() -> None:
    movies = collect_all_data(num_items=60)
    save_raw_data(movies)

    print("TMDB collection complete.")
    print(f"Total movies collected: {len(movies)}")


if __name__ == "__main__":
    main()

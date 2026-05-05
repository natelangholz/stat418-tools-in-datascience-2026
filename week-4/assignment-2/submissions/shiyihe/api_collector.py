import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TMDB_API_KEY")
url = "https://api.themoviedb.org/3/movie/popular"

os.makedirs("data/raw/tmdb", exist_ok=True)

movies = []

if api_key is None:
    print("No API key found. Check .env file.")
else:
    for page in range(1, 6):
        params = {
            "api_key": api_key,
            "language": "en-US",
            "page": page
        }

        r = requests.get(url, params=params)
        data = r.json()

        movies.extend(data["results"])
        print("finished page", page)

        time.sleep(0.2)

    with open("data/raw/tmdb/tmdb_popular_movies.json", "w") as f:
        json.dump(movies, f, indent=2)

    print("saved", len(movies), "movies")

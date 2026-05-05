import os
import json
import pandas as pd

os.makedirs("data/processed", exist_ok=True)

with open("data/raw/tmdb/tmdb_popular_movies.json") as f:
    tmdb = json.load(f)

with open("data/raw/imdb/imdb_movies.json") as f:
    imdb = json.load(f)

tmdb_df = pd.DataFrame(tmdb)
imdb_df = pd.DataFrame(imdb)

tmdb_clean = tmdb_df[[
    "title", "release_date", "vote_average", "vote_count", "popularity"
]].copy()

tmdb_clean["year"] = pd.to_datetime(
    tmdb_clean["release_date"], errors="coerce"
).dt.year

imdb_clean = imdb_df.rename(columns={
    "name": "title",
    "score": "imdb_score"
})

merged = pd.merge(
    tmdb_clean,
    imdb_clean,
    on=["title", "year"],
    how="inner"
)

tmdb_clean.to_csv("data/processed/tmdb_clean.csv", index=False)
imdb_clean.to_csv("data/processed/imdb_clean.csv", index=False)
merged.to_csv("data/processed/movies_merged.csv", index=False)

print("tmdb rows:", len(tmdb_clean))
print("imdb rows:", len(imdb_clean))
print("merged rows:", len(merged))

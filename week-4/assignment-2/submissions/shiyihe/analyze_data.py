import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("data/analysis", exist_ok=True)

tmdb = pd.read_csv("data/processed/tmdb_clean.csv")
imdb = pd.read_csv("data/processed/imdb_clean.csv")

print("TMDB average rating:", tmdb["vote_average"].mean())
print("IMDB average rating:", imdb["imdb_score"].mean())

top_tmdb = tmdb.sort_values("vote_average", ascending=False).head(10)
top_imdb = imdb.sort_values("imdb_score", ascending=False).head(10)

top_tmdb.to_csv("data/analysis/top_tmdb_movies.csv", index=False)
top_imdb.to_csv("data/analysis/top_imdb_movies.csv", index=False)

plt.figure(figsize=(8, 5))
tmdb["vote_average"].hist(bins=10)
plt.title("TMDB Rating Distribution")
plt.xlabel("Vote Average")
plt.ylabel("Number of Movies")
plt.tight_layout()
plt.savefig("data/analysis/tmdb_rating_distribution.png")
plt.close()

plt.figure(figsize=(8, 5))
imdb["imdb_score"].hist(bins=10)
plt.title("IMDB Rating Distribution")
plt.xlabel("IMDB Score")
plt.ylabel("Number of Movies")
plt.tight_layout()
plt.savefig("data/analysis/imdb_rating_distribution.png")
plt.close()

print("analysis files saved")

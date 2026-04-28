import os
import json
import requests
import pandas as pd

os.makedirs("data/raw/imdb", exist_ok=True)

url = "https://raw.githubusercontent.com/danielgrijalva/movie-stats/master/movies.csv"

r = requests.get(url, verify=False)   # 关键：跳过SSL验证
data = r.content

with open("temp.csv", "wb") as f:
    f.write(data)

df = pd.read_csv("temp.csv")

movies = df[["name", "score", "genre", "year"]].head(100)

movies.to_json("data/raw/imdb/imdb_movies.json", orient="records", indent=2)

print("saved", len(movies), "movies")

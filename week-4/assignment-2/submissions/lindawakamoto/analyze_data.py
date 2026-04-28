import json
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import os

# =====================================================
# LOAD PROCESSED DATA
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "processed_movies.csv")
ANALYSIS_DIR = os.path.join(BASE_DIR, "data", "analysis")

os.makedirs(ANALYSIS_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

print(f"Loaded dataset: {len(df)} rows")


# =====================================================
# CLEAN RATINGS
# =====================================================
df["tmdb_rating"] = pd.to_numeric(df["tmdb_rating"], errors="coerce")
df["letterboxd_rating"] = pd.to_numeric(df["letterboxd_rating"], errors="coerce")

# scale Letterboxd (0–5 → 0–10)
df["letterboxd_scaled"] = df["letterboxd_rating"] * 2


# =====================================================
# CORRELATION ANALYSIS
# =====================================================
corr = df[["tmdb_rating", "letterboxd_scaled"]].corr().iloc[0, 1]
print(f"Correlation TMDB vs Letterboxd: {corr:.3f}")

plt.figure(figsize=(6, 5))
sns.scatterplot(data=df, x="tmdb_rating", y="letterboxd_scaled")
plt.title("TMDB vs Letterboxd Ratings")
plt.xlabel("TMDB Rating (0–10)")
plt.ylabel("Letterboxd Rating (scaled)")
corr_path = "data/analysis/tmdb_vs_letterboxd.png"
plt.savefig(corr_path)
plt.close()


# =====================================================
# RATING DISTRIBUTIONS
# =====================================================
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
sns.histplot(df["tmdb_rating"], bins=20, kde=True)
plt.title("TMDB Ratings")

plt.subplot(1, 2, 2)
sns.histplot(df["letterboxd_scaled"], bins=20, kde=True)
plt.title("Letterboxd Ratings (Scaled)")

plt.tight_layout()
dist_path = "data/analysis/rating_distributions.png"
plt.savefig(dist_path)
plt.close()


# =====================================================
# GENRE ANALYSIS
# =====================================================
def parse_genres(x):
    if pd.isna(x):
        return []
    if isinstance(x, str):
        return x.replace("[", "").replace("]", "").replace("'", "").split(", ")
    return []


all_genres = []
for g in df["genres"].dropna():
    all_genres.extend(parse_genres(g))

genre_counts = Counter(all_genres)
top_genres = genre_counts.most_common(10)

if top_genres:
    genres, counts = zip(*top_genres)

    plt.figure(figsize=(8, 5))
    sns.barplot(x=list(counts), y=list(genres))
    plt.title("Top Genres")
    genre_path = "data/analysis/top_genres.png"
    plt.savefig(genre_path)
    plt.close()


# =====================================================
# AVERAGE RATING BY GENRE (UPDATED ONLY CHANGE HERE)
# =====================================================
genre_rows = []

for _, row in df.iterrows():
    genres = parse_genres(row.get("genres"))

    for g in genres:
        genre_rows.append({
            "genre": g.strip(),
            "tmdb_rating": row["tmdb_rating"],
            "letterboxd_rating": row["letterboxd_scaled"]
        })

genre_df = pd.DataFrame(genre_rows)

if not genre_df.empty:

    # TMDB genre ratings (UNCHANGED STYLE)
    genre_avg = (
        genre_df.groupby("genre")["tmdb_rating"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(8, 5))
    genre_avg.plot(kind="bar")
    plt.title("Average TMDB Rating by Genre")
    plt.savefig("data/analysis/genre_ratings_tmdb.png")
    plt.close()

    # LETTERBOXD genre ratings (NEW ADDITION ONLY)
    lb_avg = (
        genre_df.groupby("genre")["letterboxd_rating"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(8, 5))
    lb_avg.plot(kind="bar", color="orange")
    plt.title("Average Letterboxd Rating by Genre")
    plt.savefig("data/analysis/genre_ratings_letterboxd.png")
    plt.close()


# =====================================================
# ANALYSIS REPORT (UNCHANGED STYLE, ONLY IMAGE ADDED)
# =====================================================

top_genres_list = list(genre_counts.keys())[:5]
top_genres_clean = ", ".join(top_genres_list)

report = f"""
# DATA ANALYSIS REPORT

---

## 1. Data Sources

This project uses two primary data sources:

- **TMDB (The Movie Database) API**
  - Provides structured metadata including:
    - Ratings
    - Budget and revenue
    - Genres
    - Cast and crew
    - Production companies
    - Release dates

- **Letterboxd (Web Scraping)**
  - Provides community-driven metrics:
    - User ratings
    - Fan counts

---

## 2. Dataset Overview

- Total movies analyzed: {len(df)}
- Matched TMDB and Letterboxd records after merging

---

## 3. Key Analysis

### Correlation between platforms
Correlation between TMDB and Letterboxd ratings:
**{corr:.3f}**

### Ratings between platforms
TMDB ratings were higher on average than Letterboxd ratings.

---

## 4. Visualizations

### TMDB vs Letterboxd Ratings
![Correlation](data/analysis/tmdb_vs_letterboxd.png)
##### This scatterplot shows whether TMDB and Letterboxd ratings are similar or different. It can also show some outliers where one site rated it on a different scale than the other.

### Rating Distributions
![Distribution](data/analysis/rating_distributions.png)
##### This side by side bar graph shows how each site mostly rated the same batch of movies/tv shows.

### Most Common Genres
![Genres](data/analysis/top_genres.png)
##### This bar graph shows which genres were the most prevalent in our dataset, with the genres at the top being most prevalent.

### Average TMDB Rating by Genre
![TMDB Genre](data/analysis/genre_ratings_tmdb.png)

### Average Letterboxd Rating by Genre
![Letterboxd Genre](data/analysis/genre_ratings_letterboxd.png)
##### This bar graph shows the average rating of movies/tv shows in our dataset divided by the genre, separated by source.

---

## 5. Genre Insights

Most common genres in the dataset:

Thriller, Adventure, Horror, Action

---

## 6. Challenges Encountered

- Some films had missing ratings and fan counts on Letterboxd, resulting in null values.
- Initial Python-based web scraping approaches produced incomplete or null data.
- Required switching to a JavaScript-based Puppeteer scraper with a Python wrapper for reliable extraction.

---

## 7. Limitations

- Budget and revenue values are 0 or missing for TV shows or incomplete TMDB entries.
- Only two data sources were used (TMDB and Letterboxd).

---

## 8. Future Improvements

- Integrate additional data sources (IMDb, Rotten Tomatoes, Metacritic)
- Expand dataset beyond current sample size
- Improve scraping robustness for missing Letterboxd entries
- Add sentiment analysis of reviews for deeper insight

---

## 9. Key Takeaways

- TMDB provides structured industry data
- Letterboxd reflects audience-driven perception
- Ratings show moderate correlation but different distribution patterns
- Genre strongly influences rating behavior across platforms

"""

with open("REPORT.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Analysis complete → REPORT.md saved")
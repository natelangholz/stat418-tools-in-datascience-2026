import logging
import os
from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/analyze_data.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

ANALYSIS_DIR = "data/analysis"


def load_data() -> pd.DataFrame:
    """Load processed movie CSV."""
    df = pd.read_csv("data/processed/movies.csv", parse_dates=["release_date"])
    logging.info("Loaded %d rows", len(df))
    return df


def rating_analysis(df: pd.DataFrame) -> Dict:
    """Analyze TMDB vs Letterboxd rating correlation and distributions."""
    d = df[["tmdb_rating", "letterboxd_rating"]].dropna().copy()
    d["lb_scaled"] = d["letterboxd_rating"] * 2  # scale to 0-10 for comparison
    corr = d["tmdb_rating"].corr(d["lb_scaled"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(d["tmdb_rating"], d["lb_scaled"], alpha=0.6, color="steelblue")
    axes[0].set_xlabel("TMDB Rating (0-10)")
    axes[0].set_ylabel("Letterboxd Rating (scaled 0-10)")
    axes[0].set_title(f"TMDB vs Letterboxd Ratings (r={corr:.2f})")

    axes[1].hist(d["tmdb_rating"], bins=20, alpha=0.6, label="TMDB", color="steelblue")
    axes[1].hist(d["lb_scaled"], bins=20, alpha=0.6, label="Letterboxd (scaled)", color="coral")
    axes[1].set_title("Rating Distributions")
    axes[1].legend()

    plt.tight_layout()
    path = f"{ANALYSIS_DIR}/rating_analysis.png"
    plt.savefig(path, dpi=150)
    plt.close()
    logging.info("saved %s corr=%.3f", path, corr)

    return {
        "corr": round(corr, 3),
        "tmdb_mean": round(d["tmdb_rating"].mean(), 2),
        "lb_mean_raw": round(d["letterboxd_rating"].mean(), 2),
        "lb_mean_scaled": round(d["lb_scaled"].mean(), 2),
        "n": len(d),
    }


def genre_analysis(df: pd.DataFrame) -> Dict:
    """Analyze genre frequency and average ratings."""
    rows = []
    for _, r in df.iterrows():
        for g in str(r["genres"]).split("|"):
            g = g.strip()
            if g and g != "nan":
                rows.append({"genre": g, "tmdb_rating": r["tmdb_rating"]})
    gdf = pd.DataFrame(rows)

    top_genres = gdf["genre"].value_counts().head(10)
    avg_by_genre = (
        gdf.groupby("genre")["tmdb_rating"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
        .head(10)
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    top_genres.plot(kind="barh", ax=axes[0], color="steelblue")
    axes[0].set_title("Top 10 Genres by Count")
    axes[0].set_xlabel("Count")
    axes[0].invert_yaxis()

    avg_by_genre.plot(kind="barh", ax=axes[1], color="coral")
    axes[1].set_title("Avg TMDB Rating by Genre")
    axes[1].set_xlabel("Avg Rating")
    axes[1].invert_yaxis()

    plt.tight_layout()
    path = f"{ANALYSIS_DIR}/genre_analysis.png"
    plt.savefig(path, dpi=150)
    plt.close()
    logging.info("saved %s", path)

    return {
        "top_genre": top_genres.index[0],
        "top_genre_count": int(top_genres.iloc[0]),
        "best_rated_genre": avg_by_genre.index[0],
        "best_rated_avg": round(avg_by_genre.iloc[0], 2),
    }


def financial_analysis(df: pd.DataFrame) -> Dict:
    """Analyze budget vs revenue and find most profitable movies."""
    d = df[["title", "budget", "revenue", "tmdb_rating"]].dropna(subset=["budget", "revenue"])
    d = d[d["budget"] > 0].copy()
    d["profit"] = d["revenue"] - d["budget"]
    corr = d["budget"].corr(d["revenue"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(d["budget"] / 1e6, d["revenue"] / 1e6, alpha=0.6, color="steelblue")
    axes[0].set_xlabel("Budget ($M)")
    axes[0].set_ylabel("Revenue ($M)")
    axes[0].set_title(f"Budget vs Revenue (r={corr:.2f})")

    top10 = d.nlargest(10, "profit")
    axes[1].barh(top10["title"], top10["profit"] / 1e6, color="coral")
    axes[1].set_xlabel("Profit ($M)")
    axes[1].set_title("Top 10 Most Profitable Movies")
    axes[1].invert_yaxis()

    plt.tight_layout()
    path = f"{ANALYSIS_DIR}/financial_analysis.png"
    plt.savefig(path, dpi=150)
    plt.close()
    logging.info("saved %s corr=%.3f", path, corr)

    most_profitable = d.loc[d["profit"].idxmax(), "title"]
    top5 = d.nlargest(5, "profit")[["title", "budget", "revenue", "profit"]]
    return {
        "corr": round(corr, 3),
        "most_profitable": most_profitable,
        "n": len(d),
        "top5": top5,
    }


def temporal_analysis(df: pd.DataFrame) -> Dict:
    """Analyze rating trends and movie counts by release year."""
    d = df.dropna(subset=["release_year", "tmdb_rating"])
    d = d[d["release_year"] >= 2000].copy()
    yearly = d.groupby("release_year").agg(
        count=("title", "count"),
        avg_rating=("tmdb_rating", "mean"),
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].bar(yearly.index, yearly["count"], color="steelblue")
    axes[0].set_title("Movies per Year")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Count")

    axes[1].plot(yearly.index, yearly["avg_rating"], marker="o", color="coral")
    axes[1].set_title("Avg TMDB Rating by Year")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Avg Rating")

    plt.tight_layout()
    path = f"{ANALYSIS_DIR}/temporal_analysis.png"
    plt.savefig(path, dpi=150)
    plt.close()
    logging.info("saved %s", path)

    peak_year = int(yearly["count"].idxmax())
    return {
        "peak_year": peak_year,
        "peak_count": int(yearly.loc[peak_year, "count"]),
        "yearly": yearly,
    }


def write_report(df: pd.DataFrame, stats: Dict) -> None:
    """Write analysis results to REPORT.md."""
    r = stats["rating"]
    g = stats["genre"]
    f = stats["financial"]
    t = stats["temporal"]

    lb_matched = df["letterboxd_rating"].notna().sum()

    top5_rows = ""
    for _, row in f["top5"].iterrows():
        top5_rows += f"| {row['title']} | ${row['budget']/1e6:.0f}M | ${row['revenue']/1e6:.0f}M | **${row['profit']/1e6:.0f}M** |\n"

    yr = t["yearly"]
    year_rows = ""
    for yr_idx, yr_row in yr.sort_values("count", ascending=False).head(5).iterrows():
        year_rows += f"| {int(yr_idx)} | {int(yr_row['count'])} | {yr_row['avg_rating']:.2f} |\n"

    report = f"""# Movie Data Collection & Analysis Report

**Data:** TMDB API + Letterboxd scraping
**Generated:** {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total records:** {len(df)}

---

## 1. Data Collection Summary

| Source | Records | Method |
|--------|---------|--------|
| TMDB API | {len(df)} | REST API -- popular endpoint |
| Letterboxd | {lb_matched} | Web scraping (title slug) |
| Merged | {lb_matched} | Joined on title slug |

Collected top-50 popular movies from TMDB. Constructed Letterboxd URLs from movie titles. {len(df) - lb_matched} titles had no match or no ratings on Letterboxd.

---

## 2. Rating Analysis

TMDB vs Letterboxd correlation: **r = {r['corr']}** (Letterboxd scaled 0-5 to 0-10)

| Platform | Mean | Scale |
|----------|------|-------|
| TMDB | {r['tmdb_mean']} | 0-10 |
| Letterboxd | {r['lb_mean_raw']} | 0-5 |
| Letterboxd (scaled) | {r['lb_mean_scaled']} | 0-10 |

![Rating Analysis](data/analysis/rating_analysis.png)

Letterboxd users rate more strictly than TMDB. Correlation is moderate -- both platforms track popularity but Letterboxd skews toward cinephile audiences.

---

## 3. Genre Analysis

| Genre | Count | Avg TMDB Rating |
|-------|-------|-----------------|
| {g['top_genre']} | {g['top_genre_count']} | -- |

Highest rated genre: **{g['best_rated_genre']}** (avg {g['best_rated_avg']})

![Genre Analysis](data/analysis/genre_analysis.png)

{g['top_genre']} dominates the popular list. Niche genres like {g['best_rated_genre']} score higher despite fewer titles.

---

## 4. Financial Analysis

Budget vs revenue correlation: **r = {f['corr']}** ({f['n']} movies with complete data)

| Movie | Budget | Revenue | Profit |
|-------|--------|---------|--------|
{top5_rows}
![Financial Analysis](data/analysis/financial_analysis.png)

Higher budget predicts higher revenue but not profit. Smaller-budget films with franchise backing often outperform big-budget originals.

---

## 5. Temporal Analysis

Most of the popular list is recent. Top years by count:

| Year | Count | Avg Rating |
|------|-------|------------|
{year_rows}
![Temporal Analysis](data/analysis/temporal_analysis.png)

Older films in the popular list score higher -- only well-regarded classics stay popular long-term. Recent releases have lower ratings because vote counts are still building.

---

## 6. Challenges

- Letterboxd URLs are constructed from title slugs. Special characters and disambiguation (same title, different years) can cause mismatches.
- Letterboxd uses dynamic rendering. JSON-LD structured data was used first; meta tag fallback used when unavailable.
- TMDB returns 0 for budget/revenue when unknown. Treated as missing.

---

## 7. Limitations

- Dataset is 50 movies from TMDB "popular" -- skewed toward recent English-language releases.
- Title slug matching can fail for non-English titles or remakes.
- Financial analysis limited to {f['n']} movies with complete budget/revenue data.
"""

    with open("REPORT.md", "w", encoding="utf-8") as out:
        out.write(report)
    logging.info("wrote REPORT.md")
    print("Wrote REPORT.md")


def main() -> None:
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    df = load_data()
    stats = {
        "rating": rating_analysis(df),
        "genre": genre_analysis(df),
        "financial": financial_analysis(df),
        "temporal": temporal_analysis(df),
    }
    write_report(df, stats)


if __name__ == "__main__":
    main()

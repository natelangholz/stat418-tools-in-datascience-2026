import json
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List

# setup
PROCESSED_PATH = Path("data/processed/movies_processed.json")
ANALYSIS_DIR   = Path("data/analysis")
Path("logs").mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename="logs/analyze_data.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# set plot style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# load processed movies dataset frmo json
def load_processed_data() -> pd.DataFrame:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Processed data not found at {PROCESSED_PATH}. Run data_processor.py first."
        )

    with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = df["release_date"].dt.year

    logger.info(f"Loaded processed dataset with {len(df)} records.")
    print(f"[Analysis] Loaded {len(df)} movies.")
    return df

# analyze and visualize correlation between TMDB and letterboxd ratings
def analyze_rating_correlation(df: pd.DataFrame) -> None:
    # Drop rows missing either rating
    rating_df = df.dropna(subset=["tmdb_rating", "letterboxd_rating"]).copy()

    # Normalize TMDB rating to 0-5 scale to match Letterboxd
    rating_df["tmdb_rating_normalized"] = rating_df["tmdb_rating"] / 2

    correlation = rating_df["tmdb_rating_normalized"].corr(rating_df["letterboxd_rating"])
    logger.info(f"Rating correlation (normalized): {correlation:.3f}")
    print(f"[Analysis] TMDB vs Letterboxd rating correlation: {correlation:.3f}")

    # Scatter plot
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=rating_df,
        x="tmdb_rating_normalized",
        y="letterboxd_rating",
        alpha=0.7,
        ax=ax
    )
    # Add a diagonal reference line (perfect correlation)
    min_val = min(rating_df["tmdb_rating_normalized"].min(), rating_df["letterboxd_rating"].min())
    max_val = max(rating_df["tmdb_rating_normalized"].max(), rating_df["letterboxd_rating"].max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", label="Perfect correlation")

    ax.set_title(f"TMDB vs Letterboxd Ratings (r = {correlation:.2f})")
    ax.set_xlabel("TMDB Rating (normalized to 0-5)")
    ax.set_ylabel("Letterboxd Rating (0-5)")
    ax.legend()

    path = ANALYSIS_DIR / "rating_correlation.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved rating correlation plot to {path}.")
    print(f"[Analysis] Saved → {path}")

    # Rating distribution comparison
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.histplot(rating_df["tmdb_rating"], bins=15, ax=axes[0], color="steelblue")
    axes[0].set_title("TMDB Rating Distribution (0-10)")
    axes[0].set_xlabel("Rating")

    sns.histplot(rating_df["letterboxd_rating"], bins=15, ax=axes[1], color="coral")
    axes[1].set_title("Letterboxd Rating Distribution (0-5)")
    axes[1].set_xlabel("Rating")

    path = ANALYSIS_DIR / "rating_distributions.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved rating distributions plot to {path}.")
    print(f"[Analysis] Saved → {path}")

# analyze most common genres and average ratings per genre
def analyze_genres(df: pd.DataFrame) -> None:
    # Explode genres list into individual rows
    genre_df = df.dropna(subset=["genres"]).copy()
    genre_df = genre_df.explode("genres")
    genre_df = genre_df.rename(columns={"genres": "genre"})
    genre_df = genre_df[genre_df["genre"].notna() & (genre_df["genre"] != "")]

    # Most common genres
    genre_counts = genre_df["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

    fig, ax = plt.subplots()
    sns.barplot(data=genre_counts.head(10), x="count", y="genre", hue="genre", palette="viridis", legend=False, ax=ax)
    ax.set_title("Top 10 Most Common Genres")
    ax.set_xlabel("Number of Movies")
    ax.set_ylabel("Genre")

    path = ANALYSIS_DIR / "genre_counts.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved genre counts plot to {path}.")
    print(f"[Analysis] Saved → {path}")

    # Average TMDB rating by genre
    avg_ratings = (
        genre_df.dropna(subset=["tmdb_rating"])
        .groupby("genre")["tmdb_rating"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots()
    sns.barplot(data=avg_ratings.head(10), x="tmdb_rating", y="genre", palette="coolwarm", ax=ax)
    ax.set_title("Average TMDB Rating by Genre (Top 10)")
    ax.set_xlabel("Average TMDB Rating")
    ax.set_ylabel("Genre")

    path = ANALYSIS_DIR / "genre_avg_ratings.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved genre avg ratings plot to {path}.")
    print(f"[Analysis] Saved → {path}")

# analyze budget vs revenue to identify most profitable movies
def analyze_financials(df: pd.DataFrame) -> None:
    fin_df = df.dropna(subset=["budget", "revenue"]).copy()
    fin_df = fin_df[(fin_df["budget"] > 0) & (fin_df["revenue"] > 0)]
    fin_df["profit"] = fin_df["revenue"] - fin_df["budget"]
    fin_df["roi"]    = (fin_df["profit"] / fin_df["budget"]) * 100

    logger.info(f"Financial analysis on {len(fin_df)} movies with budget and revenue data.")
    print(f"[Analysis] Financial analysis: {len(fin_df)} movies with budget + revenue data.")

    # Budget vs revenue scatter
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=fin_df,
        x="budget",
        y="revenue",
        hue="tmdb_rating",
        palette="YlOrRd",
        size="tmdb_rating",
        sizes=(40, 200),
        alpha=0.8,
        ax=ax
    )
    # Add break-even line
    max_val = max(fin_df["budget"].max(), fin_df["revenue"].max())
    ax.plot([0, max_val], [0, max_val], "r--", label="Break-even")

    ax.set_title("Budget vs Revenue")
    ax.set_xlabel("Budget (USD)")
    ax.set_ylabel("Revenue (USD)")
    ax.legend(title="TMDB Rating", bbox_to_anchor=(1.05, 1), loc="upper left")

    path = ANALYSIS_DIR / "budget_vs_revenue.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved budget vs revenue plot to {path}.")
    print(f"[Analysis] Saved → {path}")

    # Top 10 most profitable movies
    top_profitable = fin_df.nlargest(10, "profit")[["title", "budget", "revenue", "profit"]]
    logger.info(f"Top profitable movies:\n{top_profitable.to_string()}")
    print("\n[Analysis] Top 10 Most Profitable Movies:")
    print(top_profitable.to_string(index=False))

# analyze rating trends and movie counts over time
def analyze_temporal(df: pd.DataFrame) -> None:
    temporal_df = df.dropna(subset=["year", "tmdb_rating"]).copy()
    temporal_df["year"] = temporal_df["year"].astype(int)

    yearly = (
        temporal_df.groupby("year")
        .agg(
            avg_tmdb_rating=("tmdb_rating", "mean"),
            avg_letterboxd_rating=("letterboxd_rating", "mean"),
            movie_count=("title", "count")
        )
        .reset_index()
    )

    # Rating trends over time
    fig, ax = plt.subplots()
    sns.lineplot(data=yearly, x="year", y="avg_tmdb_rating", label="TMDB (0-10)", marker="o", ax=ax)

    # Normalize letterboxd to 0-10 for same axis
    yearly["avg_letterboxd_normalized"] = yearly["avg_letterboxd_rating"] * 2
    sns.lineplot(data=yearly, x="year", y="avg_letterboxd_normalized", label="Letterboxd (normalized to 0-10)", marker="s", ax=ax)

    ax.set_title("Average Rating Trends Over Time")
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Average Rating")
    ax.legend()

    path = ANALYSIS_DIR / "rating_trends_over_time.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved rating trends plot to {path}.")
    print(f"[Analysis] Saved → {path}")

    # Movie count by year
    fig, ax = plt.subplots()
    sns.barplot(data=yearly, x="year", y="movie_count", color="steelblue", ax=ax)
    ax.set_title("Number of Movies by Release Year")
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Movies")
    plt.xticks(rotation=45)

    path = ANALYSIS_DIR / "movies_by_year.png"
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved movies by year plot to {path}.")
    print(f"[Analysis] Saved → {path}")

    # Most productive year
    most_productive = yearly.loc[yearly["movie_count"].idxmax()]
    logger.info(f"Most productive year: {int(most_productive['year'])} with {int(most_productive['movie_count'])} movies.")
    print(f"\n[Analysis] Most productive year: {int(most_productive['year'])} ({int(most_productive['movie_count'])} movies)")

# generate plain text summary report
def generate_summary_report(df: pd.DataFrame) -> None:
    report_path = ANALYSIS_DIR / "summary_report.txt"

    fin_df = df.dropna(subset=["budget", "revenue"]).copy()
    fin_df = fin_df[(fin_df["budget"] > 0) & (fin_df["revenue"] > 0)]
    fin_df["profit"] = fin_df["revenue"] - fin_df["budget"]

    rating_df = df.dropna(subset=["tmdb_rating", "letterboxd_rating"]).copy()
    rating_df["tmdb_normalized"] = rating_df["tmdb_rating"] / 2
    correlation = rating_df["tmdb_normalized"].corr(rating_df["letterboxd_rating"])

    genre_df = df.dropna(subset=["genres"]).explode("genres").rename(columns={"genres": "genre"})
    top_genre = genre_df["genre"].value_counts().idxmax()

    lines = [
        "=" * 60,
        "MOVIE DATA ANALYSIS — SUMMARY REPORT",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "DATASET",
        f"  Total movies analyzed:       {len(df)}",
        f"  Date range:                  {df['release_date'].min().year} – {df['release_date'].max().year}",
        "",
        "RATING CORRELATION",
        f"  TMDB vs Letterboxd (r):      {correlation:.3f}",
        f"  Avg TMDB rating:             {df['tmdb_rating'].mean():.2f} / 10",
        f"  Avg Letterboxd rating:       {df['letterboxd_rating'].mean():.2f} / 5",
        "",
        "GENRES",
        f"  Most common genre:           {top_genre}",
        "",
        "FINANCIALS",
        f"  Movies with financial data:  {len(fin_df)}",
    ]

    if len(fin_df) > 0:
        most_profitable = fin_df.loc[fin_df["profit"].idxmax()]
        lines += [
            f"  Most profitable movie:       {most_profitable['title']}",
            f"  Profit:                      ${most_profitable['profit']:,.0f}",
        ]

    lines += [
        "",
        "VISUALIZATIONS SAVED",
        "  - rating_correlation.png",
        "  - rating_distributions.png",
        "  - genre_counts.png",
        "  - genre_avg_ratings.png",
        "  - budget_vs_revenue.png",
        "  - rating_trends_over_time.png",
        "  - movies_by_year.png",
        "",
        "=" * 60,
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Summary report saved to {report_path}.")
    print(f"[Analysis] Summary report saved → {report_path}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_processed_data()

    print("\n── Rating Correlation ───────────────────────────────────")
    analyze_rating_correlation(df)

    print("\n── Genre Analysis ───────────────────────────────────────")
    analyze_genres(df)

    print("\n── Financial Analysis ───────────────────────────────────")
    analyze_financials(df)

    print("\n── Temporal Analysis ────────────────────────────────────")
    analyze_temporal(df)

    print("\n── Summary Report ───────────────────────────────────────")
    generate_summary_report(df)

    print("\n[Analysis] All done! Check data/analysis/ for outputs.")
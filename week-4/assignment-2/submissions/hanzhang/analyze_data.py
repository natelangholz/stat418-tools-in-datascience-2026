import logging
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("data/processed/movies_processed.csv")
OUTPUT_DIR = Path("data/analysis")
LOG_DIR = Path("logs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Processed data file not found.")
    df = pd.read_csv(DATA_PATH)
    logging.info(f"Loaded dataset with shape {df.shape}")
    return df


def plot_rating_comparison(df: pd.DataFrame) -> None:
    clean_df = df.dropna(subset=["tmdb_rating", "letterboxd_rating"])
    plt.figure()
    plt.scatter(clean_df["tmdb_rating"], clean_df["letterboxd_rating"] * 2)
    plt.xlabel("TMDB Rating (0-10)")
    plt.ylabel("Letterboxd Rating (converted to 0-10)")
    plt.title("TMDB vs Letterboxd Rating Comparison")
    output_path = OUTPUT_DIR / "rating_comparison.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print("Saved:", output_path)
    logging.info("Saved rating comparison plot")


def plot_genre_counts(df: pd.DataFrame) -> None:
    genre_series = df["genres_text"].dropna()
    all_genres = []
    for genres in genre_series:
        for g in genres.split(","):
            g = g.strip()
            if g:
                all_genres.append(g)
    genre_counts = pd.Series(all_genres).value_counts().head(10)
    plt.figure()
    genre_counts.plot(kind="bar")
    plt.xlabel("Genre")
    plt.ylabel("Count")
    plt.title("Top 10 Most Common Genres")
    output_path = OUTPUT_DIR / "genre_counts.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print("Saved:", output_path)
    logging.info("Saved genre counts plot")


def plot_top_profit_movies(df: pd.DataFrame) -> None:
    profit_df = df.dropna(subset=["profit"])
    top_movies = profit_df.sort_values(by="profit", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(top_movies["title"], top_movies["profit"])
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Movie")
    plt.ylabel("Profit (USD)")
    plt.title("Top 10 Movies by Profit")
    output_path = OUTPUT_DIR / "top_profit_movies.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print("Saved:", output_path)
    logging.info("Saved top profit movies plot")


def compute_rating_correlation(df: pd.DataFrame) -> Dict[str, float]:
    pair = df[["tmdb_rating", "letterboxd_rating_10"]].dropna()
    pearson = pair.corr(method="pearson").iloc[0, 1]
    spearman = pair.corr(method="spearman").iloc[0, 1]
    return {
        "n": float(len(pair)),
        "pearson": float(pearson),
        "spearman": float(spearman),
        "mean_tmdb": float(pair["tmdb_rating"].mean()),
        "mean_letterboxd_10": float(pair["letterboxd_rating_10"].mean()),
    }


def compute_genre_avg_ratings(df: pd.DataFrame) -> pd.DataFrame:
    exploded = (
        df.assign(genre=df["genres_text"].fillna("").str.split(","))
          .explode("genre")
    )
    exploded["genre"] = exploded["genre"].str.strip()
    exploded = exploded[exploded["genre"] != ""]
    summary = (
        exploded.groupby("genre")
                .agg(
                    n=("tmdb_id", "count"),
                    mean_tmdb=("tmdb_rating", "mean"),
                    mean_letterboxd_10=("letterboxd_rating_10", "mean"),
                )
                .sort_values("n", ascending=False)
    )
    return summary


def compute_budget_revenue_correlation(df: pd.DataFrame) -> Dict[str, float]:
    sub = df[["budget", "revenue"]].dropna()
    sub = sub[(sub["budget"] > 0) & (sub["revenue"] > 0)]
    if len(sub) < 2:
        return {"n": float(len(sub)), "pearson": float("nan"), "log_pearson": float("nan")}
    pearson = sub.corr(method="pearson").iloc[0, 1]
    log_sub = sub.apply(np.log)
    log_pearson = log_sub.corr(method="pearson").iloc[0, 1]
    return {
        "n": float(len(sub)),
        "pearson": float(pearson),
        "log_pearson": float(log_pearson),
    }


def generate_summary(df: pd.DataFrame) -> None:
    summary_path = OUTPUT_DIR / "analysis_summary.txt"

    avg_tmdb = df["tmdb_rating"].mean()
    avg_letterboxd = df["letterboxd_rating"].mean()

    most_common_genre = (
        df["genres_text"]
        .str.split(",")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .idxmax()
    )

    total_movies = len(df)
    rating_corr = compute_rating_correlation(df)
    budget_corr = compute_budget_revenue_correlation(df)
    genre_summary = compute_genre_avg_ratings(df)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Movie Data Analysis Summary\n")
        f.write("---------------------------\n\n")
        f.write(f"Total movies analyzed: {total_movies}\n")
        f.write(f"Average TMDB rating: {avg_tmdb:.2f}\n")
        f.write(f"Average Letterboxd rating (0-5): {avg_letterboxd:.2f}\n")
        f.write(f"Most common genre: {most_common_genre}\n\n")

        f.write("Rating correlation (TMDB vs Letterboxd, both 0-10):\n")
        f.write(f"  n = {int(rating_corr['n'])}\n")
        f.write(f"  Pearson  r = {rating_corr['pearson']:.3f}\n")
        f.write(f"  Spearman r = {rating_corr['spearman']:.3f}\n")
        f.write(f"  Mean TMDB        = {rating_corr['mean_tmdb']:.2f}\n")
        f.write(f"  Mean Letterboxd  = {rating_corr['mean_letterboxd_10']:.2f}\n\n")

        f.write("Budget vs Revenue correlation (positive both):\n")
        f.write(f"  n = {int(budget_corr['n'])}\n")
        f.write(f"  Pearson r (raw)  = {budget_corr['pearson']:.3f}\n")
        f.write(f"  Pearson r (log)  = {budget_corr['log_pearson']:.3f}\n\n")

        f.write("Average ratings by genre (genres with n>=3 only):\n")
        sub = genre_summary[genre_summary["n"] >= 3]
        for genre, row in sub.iterrows():
            f.write(
                f"  {genre:20s}  n={int(row['n']):3d}  "
                f"TMDB={row['mean_tmdb']:.2f}  "
                f"LB(0-10)={row['mean_letterboxd_10']:.2f}\n"
            )

    print("Saved:", summary_path)
    logging.info("Saved analysis summary")


def main() -> None:
    df = load_data()
    plot_rating_comparison(df)
    plot_genre_counts(df)
    plot_top_profit_movies(df)
    generate_summary(df)
    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()

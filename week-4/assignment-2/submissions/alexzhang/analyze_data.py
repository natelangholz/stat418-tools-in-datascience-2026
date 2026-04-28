import os
import logging
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple

os.makedirs("logs", exist_ok=True)
os.makedirs("data/analysis", exist_ok=True)
logging.basicConfig(
    filename="logs/analyze_data.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
sns.set_theme(style="whitegrid")


def load_processed_data(path: str = "data/processed/movies.csv") -> pd.DataFrame:
    """Load the processed movies CSV into a DataFrame."""
    df = pd.read_csv(path, parse_dates=["release_date"])
    logging.info(f"Loaded {len(df)} rows from {path}")
    return df


def rating_analysis(df: pd.DataFrame) -> Tuple[str, float]:
    """Scatter + regression of TMDB vs Letterboxd ratings; returns insight string and correlation."""
    rated = df.dropna(subset=["vote_average", "letterboxd_rating"]).copy()
    # Normalise Letterboxd 0-5 → 0-10 to match TMDB scale
    rated["lb_scaled"] = rated["letterboxd_rating"] * 2

    corr = rated["vote_average"].corr(rated["lb_scaled"])
    logging.info(f"Rating correlation (TMDB vs LB*2): {corr:.3f}")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(data=rated, x="vote_average", y="lb_scaled", ax=ax,
                scatter_kws={"alpha": 0.6}, line_kws={"color": "tomato"})
    ax.set_title(f"TMDB Rating vs Letterboxd Rating (r = {corr:.2f})")
    ax.set_xlabel("TMDB Rating (0–10)")
    ax.set_ylabel("Letterboxd Rating × 2 (0–10)")
    path = "data/analysis/rating_correlation.png"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    logging.info(f"Saved {path}")

    insight = f"TMDB and Letterboxd ratings have a Pearson correlation of {corr:.2f} (n={len(rated)})."
    return insight, corr


def genre_analysis(df: pd.DataFrame) -> str:
    """Bar charts of top genres by count and by mean TMDB rating; returns insight string."""
    genre_df = df[df["genres"].notna() & (df["genres"] != "")].copy()
    genre_df = genre_df.assign(genre=genre_df["genres"].str.split("|")).explode("genre")
    genre_df["genre"] = genre_df["genre"].str.strip()

    counts = genre_df["genre"].value_counts().head(10)
    mean_ratings = (
        genre_df.groupby("genre")["vote_average"]
        .mean()
        .reindex(counts.index)
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    counts.plot(kind="bar", ax=axes[0], color="steelblue")
    axes[0].set_title("Top 10 Genres by Count")
    axes[0].set_xlabel("Genre")
    axes[0].set_ylabel("Number of Movies")
    axes[0].tick_params(axis="x", rotation=45)

    mean_ratings.sort_values(ascending=False).plot(kind="bar", ax=axes[1], color="seagreen")
    axes[1].set_title("Mean TMDB Rating by Genre (Top 10)")
    axes[1].set_xlabel("Genre")
    axes[1].set_ylabel("Mean TMDB Rating")
    axes[1].tick_params(axis="x", rotation=45)

    fig.tight_layout()
    path = "data/analysis/genre_analysis.png"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    logging.info(f"Saved {path}")

    top_genre = counts.index[0]
    insight = f"The most common genre is '{top_genre}' ({counts.iloc[0]} films). Top-rated genre: '{mean_ratings.idxmax()}' (avg {mean_ratings.max():.2f})."
    return insight


def financial_analysis(df: pd.DataFrame) -> str:
    """Budget vs revenue scatter with top-5 profitable films annotated; returns insight string."""
    fin = df[(df["budget"] > 0) & (df["revenue"] > 0)].copy()
    if fin.empty:
        logging.warning("No films with known budget and revenue — skipping financial analysis")
        return "No films with known budget and revenue data."
    fin["roi"] = (fin["revenue"] - fin["budget"]) / fin["budget"]
    top5 = fin.nlargest(5, "roi")

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(fin["budget"] / 1e6, fin["revenue"] / 1e6, alpha=0.6, color="steelblue", label="All films")
    ax.scatter(top5["budget"] / 1e6, top5["revenue"] / 1e6, color="tomato", zorder=5, label="Top 5 ROI")

    for _, row in top5.iterrows():
        ax.annotate(
            row["title"],
            (row["budget"] / 1e6, row["revenue"] / 1e6),
            textcoords="offset points", xytext=(5, 5), fontsize=8,
        )

    ax.set_title("Budget vs Revenue")
    ax.set_xlabel("Budget ($ millions)")
    ax.set_ylabel("Revenue ($ millions)")
    ax.legend()
    path = "data/analysis/financial_analysis.png"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    logging.info(f"Saved {path}")

    best = top5.iloc[0]
    insight = (
        f"Among {len(fin)} films with known budget/revenue, the highest ROI is "
        f"'{best['title']}' at {best['roi']:.1f}x. "
        f"Budget-revenue Pearson r = {fin['budget'].corr(fin['revenue']):.2f}."
    )
    return insight


def temporal_analysis(df: pd.DataFrame) -> str:
    """Line chart of mean TMDB rating by release year; returns insight string."""
    tmp = df.dropna(subset=["release_date", "vote_average"]).copy()
    tmp["year"] = tmp["release_date"].dt.year
    by_year = tmp.groupby("year")["vote_average"].mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    by_year.plot(ax=ax, marker="o", color="darkorange")
    ax.set_title("Mean TMDB Rating by Release Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Rating")
    path = "data/analysis/temporal_analysis.png"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    logging.info(f"Saved {path}")

    best_year = by_year.idxmax()
    insight = f"Best-rated release year in dataset: {best_year} (avg {by_year[best_year]:.2f})."
    return insight


def save_report(lines: list[str], path: str = "data/analysis/report.txt") -> None:
    """Write the summary report to a text file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logging.info(f"Saved report: {path}")


if __name__ == "__main__":
    df = load_processed_data()

    report_lines = [
        "=" * 60,
        "MOVIE DATA PIPELINE — ANALYSIS REPORT",
        "=" * 60,
        f"Total movies in dataset: {len(df)}",
        f"Date range: {df['release_date'].min().date() if df['release_date'].notna().any() else 'N/A'} – {df['release_date'].max().date() if df['release_date'].notna().any() else 'N/A'}",
        f"Movies with Letterboxd ratings: {df['letterboxd_rating'].notna().sum()}",
        "",
        "1. RATING ANALYSIS",
        "-" * 40,
    ]

    rating_insight, corr = rating_analysis(df)
    report_lines.append(rating_insight)
    report_lines.append("  → data/analysis/rating_correlation.png")
    report_lines.append("")

    report_lines += ["2. GENRE ANALYSIS", "-" * 40]
    genre_insight = genre_analysis(df)
    report_lines.append(genre_insight)
    report_lines.append("  → data/analysis/genre_analysis.png")
    report_lines.append("")

    report_lines += ["3. FINANCIAL ANALYSIS", "-" * 40]
    fin_insight = financial_analysis(df)
    report_lines.append(fin_insight)
    report_lines.append("  → data/analysis/financial_analysis.png")
    report_lines.append("")

    report_lines += ["4. TEMPORAL ANALYSIS", "-" * 40]
    temp_insight = temporal_analysis(df)
    report_lines.append(temp_insight)
    report_lines.append("  → data/analysis/temporal_analysis.png")
    report_lines.append("")

    report_lines.append("=" * 60)

    for line in report_lines:
        print(line)

    save_report(report_lines)

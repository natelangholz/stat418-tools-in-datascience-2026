"""
analyze_data.py
===============
Generate the analysis section of the homework deliverable.

What this script produces (under `data/analysis/`):

* `summary.json`            -- top-level statistics in a machine-readable form
* `summary.md`              -- the same numbers wrapped in narrative markdown
* `fig_rating_correlation.png`   -- TMDB vs Letterboxd rating scatter
* `fig_rating_distribution.png`  -- side-by-side rating histograms
* `fig_genre_counts.png`         -- bar chart of most common genres
* `fig_genre_avg_rating.png`     -- average TMDB rating by genre
* `fig_budget_revenue.png`       -- budget vs revenue with a regression line
* `fig_year_trend.png`           -- average rating over release year

We pick three questions from the assignment to answer in detail:

1. Rating analysis (correlation + distribution between TMDB and Letterboxd)
2. Genre analysis (most common, mean rating by genre)
3. Financial analysis (budget vs revenue, top earners)

A temporal trend chart is added as a fourth bonus visualization.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

import matplotlib

matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"
LOG_DIR = BASE_DIR / "logs"
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("analyze_data")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)

sns.set_theme(style="whitegrid", context="talk")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_dataframe() -> pd.DataFrame:
    csv_path = PROCESSED_DIR / "movies.csv"
    if not csv_path.exists():
        raise SystemExit(
            f"{csv_path} not found. Run data_processor.py first."
        )
    df = pd.read_csv(csv_path)
    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    # Re-explode the comma-joined columns back into Python lists
    for col in ("genres", "production_companies", "cast", "crew_top"):
        if col in df.columns:
            df[col] = df[col].fillna("").apply(
                lambda s: [t.strip() for t in s.split(",") if t.strip()]
            )
    logger.info("Loaded %d rows for analysis", len(df))
    return df


# ---------------------------------------------------------------------------
# Plot 1: TMDB vs Letterboxd rating correlation
# ---------------------------------------------------------------------------
def plot_rating_correlation(df: pd.DataFrame) -> Dict:
    sub = df.dropna(subset=["tmdb_rating", "letterboxd_rating"]).copy()
    if sub.empty:
        logger.warning("No overlap between TMDB and Letterboxd ratings.")
        return {"n": 0, "pearson": None}

    # TMDB is on a 0-10 scale, Letterboxd is 0-5. Rescale Letterboxd
    # so the eye-balled comparison is fair.
    sub["letterboxd_rating_x2"] = sub["letterboxd_rating"] * 2
    pearson = sub["tmdb_rating"].corr(sub["letterboxd_rating_x2"])

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        data=sub, x="tmdb_rating", y="letterboxd_rating_x2",
        ax=ax, scatter_kws={"alpha": 0.7}
    )
    ax.set_xlabel("TMDB rating (0-10)")
    ax.set_ylabel("Letterboxd rating x 2 (0-10)")
    ax.set_title(f"TMDB vs Letterboxd ratings (r={pearson:.2f}, n={len(sub)})")
    fig.tight_layout()
    out = ANALYSIS_DIR / "fig_rating_correlation.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved %s", out)
    return {"n": int(len(sub)), "pearson": float(pearson)}


def plot_rating_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    if df["tmdb_rating"].notna().any():
        sns.histplot(df["tmdb_rating"].dropna(), bins=20, ax=axes[0], color="#3b82f6")
    axes[0].set_title("TMDB rating (0-10)")
    axes[0].set_xlabel("Rating")

    if df["letterboxd_rating"].notna().any():
        sns.histplot(df["letterboxd_rating"].dropna(), bins=20, ax=axes[1], color="#f59e0b")
    axes[1].set_title("Letterboxd rating (0-5)")
    axes[1].set_xlabel("Rating")

    fig.tight_layout()
    out = ANALYSIS_DIR / "fig_rating_distribution.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved %s", out)


# ---------------------------------------------------------------------------
# Plot 2: Genre analysis
# ---------------------------------------------------------------------------
def analyze_genres(df: pd.DataFrame) -> Dict:
    exploded = df.explode("genres").dropna(subset=["genres"])
    exploded = exploded[exploded["genres"] != ""]
    if exploded.empty:
        return {"top_genres": [], "avg_rating_by_genre": []}

    top = exploded["genres"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top.values, y=top.index, hue=top.index,
                palette="viridis", legend=False, ax=ax)
    ax.set_xlabel("Number of movies")
    ax.set_ylabel("")
    ax.set_title("Most common genres")
    fig.tight_layout()
    out = ANALYSIS_DIR / "fig_genre_counts.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved %s", out)

    avg = (
        exploded.dropna(subset=["tmdb_rating"])
        .groupby("genres")["tmdb_rating"]
        .agg(["mean", "count"])
        .query("count >= 2")
        .sort_values("mean", ascending=False)
    )
    if not avg.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=avg["mean"], y=avg.index, hue=avg.index,
                    palette="mako", legend=False, ax=ax)
        ax.set_xlabel("Average TMDB rating")
        ax.set_ylabel("")
        ax.set_title("Average TMDB rating by genre")
        fig.tight_layout()
        out = ANALYSIS_DIR / "fig_genre_avg_rating.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        logger.info("Saved %s", out)

    return {
        "top_genres": [{"genre": g, "count": int(c)} for g, c in top.items()],
        "avg_rating_by_genre": [
            {"genre": g, "mean_rating": float(r["mean"]), "n": int(r["count"])}
            for g, r in avg.iterrows()
        ],
    }


# ---------------------------------------------------------------------------
# Plot 3: Budget vs revenue
# ---------------------------------------------------------------------------
def analyze_finance(df: pd.DataFrame) -> Dict:
    sub = df.dropna(subset=["budget", "revenue"])
    sub = sub[(sub["budget"] > 0) & (sub["revenue"] > 0)]
    if sub.empty:
        logger.warning("No financial data available.")
        return {"n": 0}

    pearson = sub["budget"].corr(sub["revenue"])

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.regplot(
        data=sub, x="budget", y="revenue", ax=ax,
        scatter_kws={"alpha": 0.7}
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Budget (USD, log scale)")
    ax.set_ylabel("Revenue (USD, log scale)")
    ax.set_title(f"Budget vs revenue (r={pearson:.2f}, n={len(sub)})")
    fig.tight_layout()
    out = ANALYSIS_DIR / "fig_budget_revenue.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved %s", out)

    top_profit = (
        sub.assign(profit=sub["revenue"] - sub["budget"])
        .sort_values("profit", ascending=False)
        .head(10)[["title", "budget", "revenue", "profit"]]
    )
    return {
        "n": int(len(sub)),
        "pearson": float(pearson),
        "top_profitable": top_profit.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# Plot 4 (bonus): year trend
# ---------------------------------------------------------------------------
def plot_year_trend(df: pd.DataFrame) -> None:
    sub = df.dropna(subset=["year", "tmdb_rating"])
    if sub.empty:
        return
    grp = sub.groupby("year")["tmdb_rating"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=grp, x="year", y="tmdb_rating", marker="o", ax=ax)
    ax.set_title("Average TMDB rating by release year")
    ax.set_ylabel("Average rating")
    ax.set_xlabel("Year")
    fig.tight_layout()
    out = ANALYSIS_DIR / "fig_year_trend.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved %s", out)


# ---------------------------------------------------------------------------
# Summary writer
# ---------------------------------------------------------------------------
def write_summary(df: pd.DataFrame, parts: Dict) -> None:
    summary = {
        "n_movies": int(len(df)),
        "n_with_tmdb_rating": int(df["tmdb_rating"].notna().sum()),
        "n_with_letterboxd_rating": int(df["letterboxd_rating"].notna().sum()),
        "rating": parts.get("rating"),
        "genres": parts.get("genres"),
        "finance": parts.get("finance"),
    }
    (ANALYSIS_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    # Markdown narrative version
    md = ["# Analysis summary", ""]
    md.append(f"- Movies analysed: **{summary['n_movies']}**")
    md.append(f"- With TMDB rating: {summary['n_with_tmdb_rating']}")
    md.append(f"- With Letterboxd rating: {summary['n_with_letterboxd_rating']}")
    md.append("")
    if summary["rating"] and summary["rating"].get("pearson") is not None:
        md.append(
            f"- Pearson correlation (TMDB vs Letterboxd*2): "
            f"**{summary['rating']['pearson']:.2f}** "
            f"(n={summary['rating']['n']})"
        )
    if summary["genres"] and summary["genres"]["top_genres"]:
        md.append("")
        md.append("## Top genres")
        for g in summary["genres"]["top_genres"][:5]:
            md.append(f"- {g['genre']}: {g['count']} films")
    if summary["finance"] and summary["finance"].get("pearson") is not None:
        md.append("")
        md.append(
            f"- Budget/revenue correlation: "
            f"**{summary['finance']['pearson']:.2f}** "
            f"(n={summary['finance']['n']})"
        )
        md.append("")
        md.append("## Most profitable in sample")
        for row in summary["finance"]["top_profitable"][:5]:
            md.append(
                f"- {row['title']}: profit "
                f"${row['profit']:,.0f}"
            )
    (ANALYSIS_DIR / "summary.md").write_text("\n".join(md), encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    df = load_dataframe()

    rating = plot_rating_correlation(df)
    plot_rating_distribution(df)
    genres = analyze_genres(df)
    finance = analyze_finance(df)
    plot_year_trend(df)

    write_summary(df, {"rating": rating, "genres": genres, "finance": finance})
    print(f"Analysis complete. Outputs in {ANALYSIS_DIR}.")


if __name__ == "__main__":
    main()

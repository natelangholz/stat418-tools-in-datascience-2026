"""
Exploratory analysis: ratings, genres, and financials with figures saved to disk.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from data_processor import clean_data, load_merged_table, load_raw_data, merge_data, save_processed_data

BASE_DIR = Path(__file__).resolve().parent
ANALYSIS = BASE_DIR / "data" / "analysis"
LOG_PATH = BASE_DIR / "logs" / "pipeline.log"

logger = logging.getLogger("analysis")
if not logger.handlers:
    _fmt = logging.Formatter("%(asctime)sZ - %(name)s - %(levelname)s - %(message)s")
    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fh.setFormatter(_fmt)
    _sh = logging.StreamHandler()
    _sh.setFormatter(_fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(_fh)
    logger.addHandler(_sh)
    logger.propagate = False

sns.set_theme(style="whitegrid", context="talk")


def _fig_save(fig: Figure, name: str) -> Path:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    p = ANALYSIS / f"{name}.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure %s", p)
    return p


def rating_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Correlation and distributions for TMDB vs IMDb ratings when both present."""
    sub = df.dropna(subset=["tmdb_vote_average", "imdb_rating"])
    if len(sub) < 2:
        return {
            "tmdb_imdb_correlation": None,
            "note": "Not enough rows with both TMDB and IMDb ratings for correlation",
        }
    c = sub["tmdb_vote_average"].corr(sub["imdb_rating"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    ax0, ax1 = axes
    sub["tmdb_vote_average"].hist(bins=15, ax=ax0, color="steelblue", edgecolor="white")
    ax0.set_title("TMDB vote average")
    sub["imdb_rating"].hist(bins=15, ax=ax1, color="coral", edgecolor="white")
    ax1.set_title("IMDb user rating")
    _fig_save(fig, "1_rating_distributions")
    fig2, ax = plt.subplots(figsize=(6, 5))
    sns.scatterplot(data=sub, x="tmdb_vote_average", y="imdb_rating", ax=ax, alpha=0.7)
    ax.set_title("TMDB vs IMDb ratings\n(scaled differently; IMDb often 0–10)")
    _fig_save(fig2, "2_tmdb_vs_imdb_scatter")
    return {
        "tmdb_imdb_correlation_pearson": float(c) if not np.isnan(c) else None,
        "n_pairs": int(len(sub)),
    }


def genre_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Count genres (pipe-separated) and mean TMDB / IMDb by genre when available."""
    if "genres_str" not in df.columns:
        return {"error": "genres_str missing — run data_processor on merged data first"}
    rows: List[Tuple[str, str, float, float]] = []
    for _, r in df.iterrows():
        gs = str(r.get("genres_str", "") or "")
        if not gs or gs == "nan":
            continue
        for g in re_split_genres(gs):
            rows.append(
                (
                    g,
                    str(r.get("title", "")),
                    float(r["tmdb_vote_average"])
                    if pd.notna(r.get("tmdb_vote_average"))
                    else float("nan"),
                    float(r["imdb_rating"])
                    if pd.notna(r.get("imdb_rating"))
                    else float("nan"),
                )
            )
    if not rows:
        return {"error": "No genre tags parsed"}
    gdf = pd.DataFrame(rows, columns=["genre", "title", "tmdb", "imdb"])
    counts = gdf["genre"].value_counts().head(20)
    means = gdf.groupby("genre").agg(
        tmdb_m=("tmdb", "mean"),
        imdb_m=("imdb", "mean"),
        n=("genre", "count"),
    )
    means = means.sort_values("n", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(10, 5))
    counts.sort_values(ascending=True).plot.barh(color="seagreen", ax=ax)
    ax.set_title("Most common genres (top 20, tags may multi-count titles)")
    _fig_save(fig, "3_top_genre_counts")
    return {
        "most_common_genres": counts.to_dict(),
        "top_genre_rows": int(len(gdf)),
    }


def re_split_genres(s: str) -> List[str]:
    """Split on | or , for genre string."""
    parts = re.split(r"[|,]", s)
    return [p.strip() for p in parts if p and p.strip()]


def financial_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Budget vs revenue and a simple 'profit' ranking when fields exist."""
    need = [c for c in ("budget", "revenue") if c in df.columns]
    if len(need) < 2:
        return {"note": "No budget/revenue on enough rows; skipping financial plots"}
    sub = df[df["budget"].fillna(0) + df["revenue"].fillna(0) > 0].copy()
    if len(sub) < 2:
        return {"note": "Insufficient financial data"}
    sub["profit"] = sub["revenue"].fillna(0) - sub["budget"].fillna(0)
    br = sub.dropna(subset=["budget", "revenue"])
    c = br["budget"].corr(br["revenue"]) if len(br) > 1 else float("nan")
    fig, ax = plt.subplots(figsize=(6, 5))
    valid = (br["budget"] > 0) & (br["revenue"] > 0)
    sns.scatterplot(data=br.loc[valid], x="budget", y="revenue", ax=ax, alpha=0.65)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Log-scale budget vs revenue (where both > 0)")
    _fig_save(fig, "4_budget_vs_revenue")
    top = sub.nlargest(5, "profit", keep="all")[["title", "budget", "revenue", "profit"]]
    return {
        "budget_revenue_correlation": None if c != c else float(c),
        "most_profitable_sample": top.to_dict(orient="records"),
    }


def temporal_sample(df: pd.DataFrame) -> Dict[str, Any]:
    """Year-level counts and mean TMDB rating (optional fourth insight)."""
    if "release_year" not in df.columns and "release_date" in df.columns:
        d = clean_data(df.copy())
    else:
        d = df
    if "release_year" not in d.columns or d["release_year"].isna().all():
        return {}
    yc = d.groupby("release_year", dropna=True).size()
    ymean = d.groupby("release_year", dropna=True)["tmdb_vote_average"].mean()
    if len(yc) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        yc.sort_index().plot(ax=ax, color="navy", marker="o")
        ax.set_title("Titles in dataset by release year (TMDB popular may skew recent)")
        _fig_save(fig, "5_titles_per_year")
    return {
        "years_covered": [float(yc.index.min()), float(yc.index.max())] if len(yc) else None,
    }


def build_summary(
    rating: Dict[str, Any],
    genre: Dict[str, Any],
    fin: Dict[str, Any],
    temporal: Dict[str, Any],
) -> None:
    """Write a machine-readable summary for REPORT cross-reference."""
    out = {
        "rating": rating,
        "genre": genre,
        "financial": fin,
        "temporal": temporal,
    }
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    jpath = ANALYSIS / "analysis_summary.json"
    with jpath.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    logger.info("Wrote %s", jpath)


def run_from_processed(csv_path: Optional[Path] = None) -> None:
    p = csv_path or (BASE_DIR / "data" / "processed" / "movies_merged.csv")
    if not p.exists():
        tmdb, imdb = load_raw_data()
        m = merge_data(tmdb, imdb)
        m = clean_data(m)
        save_processed_data(m, str(BASE_DIR / "data" / "processed"))
    df = load_merged_table(p)
    if df.empty:
        logger.error("No merged data to analyze. Run the pipeline with seed or API first.")
        return
    r = rating_analysis(df)
    g = genre_analysis(df)
    f = financial_analysis(df)
    t = temporal_sample(df)
    build_summary(r, g, f, t)


if __name__ == "__main__":
    run_from_processed()

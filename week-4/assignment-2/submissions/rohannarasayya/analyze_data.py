"""
analyze_data.py
---------------
Produces three visualisations and a summary report from the processed
movie dataset.

Outputs:
  data/analysis/rating_correlation.png
  data/analysis/rating_by_genre.png
  data/analysis/budget_vs_revenue.png
  data/analysis/summary_report.txt
"""

import ast
import logging
from pathlib import Path
from typing import Dict

import matplotlib
matplotlib.use("Agg")  # headless backend — no display required
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from adjustText import adjust_text
from scipy import stats

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "analyze_data.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("analyze_data")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROCESSED_CSV = Path("data/processed/movies.csv")
ANALYSIS_DIR = Path("data/analysis")

# ---------------------------------------------------------------------------
# Required functions
# ---------------------------------------------------------------------------


def load_processed_data() -> pd.DataFrame:
    """
    Load the processed movies CSV and restore list-type columns.

    Parses the 'genres', 'cast', 'crew', and 'production_companies'
    columns from their string representation back to Python lists.

    Returns
    -------
    pd.DataFrame
        Processed movie dataset ready for analysis.
    """
    try:
        df = pd.read_csv(PROCESSED_CSV, encoding="utf-8")
        logger.info("Loaded %d rows from %s", len(df), PROCESSED_CSV)
    except OSError as exc:
        logger.error("Cannot load processed data: %s", exc)
        raise

    # Re-parse list columns stored as strings in CSV
    list_cols = ["genres", "cast", "crew", "production_companies"]
    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].apply(_safe_parse_list)

    # Ensure numeric types
    for col in ("vote_average", "lb_rating", "fan_count", "budget", "revenue"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    return df


def analyze_ratings(df: pd.DataFrame) -> Dict:
    """
    Compute the Pearson correlation between TMDB and Letterboxd ratings and
    produce a scatter plot saved to data/analysis/rating_correlation.png.

    Plot features:
    - Points colored by primary genre with a legend.
    - Point size proportional to TMDB vote_count (sqrt-normalised).
    - Movie titles annotated for any point more than 0.8 Letterboxd rating
      points away from the OLS trend line.

    Only rows where both ratings are non-null are included.

    Parameters
    ----------
    df : pd.DataFrame
        Processed movie dataframe.

    Returns
    -------
    dict
        Keys: 'pearson_r', 'p_value', 'n_movies'.
    """
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    needed = ["title", "vote_average", "lb_rating", "genres", "vote_count"]
    subset = df[[c for c in needed if c in df.columns]].copy()
    subset = subset.dropna(subset=["vote_average", "lb_rating"])
    # Exclude movies with vote_average == 0: these have no TMDB votes recorded,
    # not an actual rating, and would stretch the x-axis with misleading whitespace.
    subset = subset[subset["vote_average"] > 0]
    subset["primary_genre"] = subset["genres"].apply(_primary_genre)
    subset["vote_count"] = pd.to_numeric(subset.get("vote_count", 0), errors="coerce").fillna(0)
    n = len(subset)
    logger.info("Rating correlation: %d movies with both ratings (vote_average > 0)", n)

    if n < 2:
        logger.warning("Not enough data for rating correlation plot -- saving placeholder")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel("TMDB Vote Average")
        ax.set_ylabel("Letterboxd Rating (0-5)")
        ax.set_title("TMDB vs Letterboxd Rating (insufficient data)")
        ax.text(0.5, 0.5, "No movies with both TMDB and Letterboxd ratings",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        plt.tight_layout()
        out_path = ANALYSIS_DIR / "rating_correlation.png"
        try:
            fig.savefig(out_path, dpi=150)
            logger.info("Saved placeholder %s", out_path)
        except OSError as exc:
            logger.error("Failed to save rating_correlation.png: %s", exc)
        plt.close(fig)
        return {"pearson_r": None, "p_value": None, "n_movies": n}

    r, p = stats.pearsonr(subset["vote_average"], subset["lb_rating"])

    # --- Build per-point color and size arrays ---
    palette = _genre_palette(df)
    colors = [palette.get(g, palette.get("Unknown", (0.5, 0.5, 0.5))) for g in subset["primary_genre"]]

    # sqrt-normalise vote_count -> [30, 250] marker area
    vc = np.sqrt(subset["vote_count"].clip(lower=1).values)
    vc_min, vc_max = vc.min(), vc.max()
    if vc_max > vc_min:
        sizes = 30 + (vc - vc_min) / (vc_max - vc_min) * 220
    else:
        sizes = np.full(len(vc), 80)

    # --- Fit trend line (OLS) ---
    x_vals = subset["vote_average"].values
    y_vals = subset["lb_rating"].values
    m, b = np.polyfit(x_vals, y_vals, 1)
    predicted = m * x_vals + b
    residuals = y_vals - predicted

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.scatter(
        x_vals, y_vals,
        c=colors, s=sizes,
        alpha=0.75, edgecolors="white", linewidths=0.4,
        zorder=3,
    )

    # Trend line
    x_range = np.linspace(x_vals.min(), x_vals.max(), 200)
    ax.plot(x_range, m * x_range + b, color="crimson", linewidth=1.8,
            linestyle="--", label=f"Trend line (r={r:.3f})", zorder=2)

    # Tighten x-axis: start at min non-zero vote_average minus 0.5
    ax.set_xlim(x_vals.min() - 0.5, x_vals.max() + 0.5)

    # --- Annotate outliers (|residual| > 0.8 on the 0-5 Letterboxd scale)
    #     using adjustText so labels don't overlap each other or data points ---
    subset_reset = subset.reset_index(drop=True)
    annotation_texts = []
    for i, row in subset_reset.iterrows():
        if abs(residuals[i]) > 0.8:
            t = ax.text(
                x_vals[i], y_vals[i],
                row["title"],
                fontsize=8,
                color="black",
                zorder=5,
            )
            annotation_texts.append(t)

    if annotation_texts:
        adjust_text(
            annotation_texts,
            x=x_vals,
            y=y_vals,
            ax=ax,
            arrowprops=dict(arrowstyle="-", lw=0.5, color="grey", shrinkA=5),
            expand_points=(1.5, 1.5),
            expand_text=(1.3, 1.3),
            force_points=(0.4, 0.4),
            force_text=(0.4, 0.4),
        )

    # --- Genre legend (color patches) ---
    import matplotlib.patches as mpatches
    present_genres = sorted(subset["primary_genre"].unique())
    genre_handles = [
        mpatches.Patch(color=palette.get(g, (0.5, 0.5, 0.5)), label=g)
        for g in present_genres
    ]
    genre_legend = ax.legend(
        handles=genre_handles,
        title="Primary Genre",
        loc="upper left",
        fontsize=7,
        title_fontsize=8,
        framealpha=0.7,
    )
    ax.add_artist(genre_legend)
    # Trend line entry in a separate legend
    ax.legend(loc="lower right", fontsize=8)

    ax.set_xlabel("TMDB Vote Average", fontsize=11)
    ax.set_ylabel("Letterboxd Rating (0-5)", fontsize=11)
    ax.set_title(f"TMDB vs Letterboxd Rating  (Pearson r = {r:.3f}, n={n})", fontsize=12)
    plt.tight_layout()

    out_path = ANALYSIS_DIR / "rating_correlation.png"
    try:
        fig.savefig(out_path, dpi=150)
        logger.info("Saved %s", out_path)
    except OSError as exc:
        logger.error("Failed to save rating_correlation.png: %s", exc)
    plt.close(fig)

    return {"pearson_r": round(r, 4), "p_value": round(p, 6), "n_movies": n}


def analyze_genres(df: pd.DataFrame) -> Dict:
    """
    Compute average Letterboxd rating per genre and produce a bar chart
    saved to data/analysis/rating_by_genre.png.

    Movies with multiple genres are counted once per genre (explode).

    Parameters
    ----------
    df : pd.DataFrame
        Processed movie dataframe.

    Returns
    -------
    dict
        Keys: 'genre_ratings' (dict of genre -> avg rating),
              'most_common_genre' (str).
    """
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    # Work with rows that have at least one genre
    genre_df = df[["title", "genres", "lb_rating"]].copy()
    genre_df = genre_df[genre_df["genres"].apply(lambda x: isinstance(x, list) and len(x) > 0)]

    # Explode so each genre gets its own row
    genre_df = genre_df.explode("genres").rename(columns={"genres": "genre"})
    genre_df["genre"] = genre_df["genre"].astype(str).str.strip()

    # Most common genre (all movies, not just those with lb_rating)
    most_common = genre_df["genre"].value_counts().idxmax() if not genre_df.empty else "N/A"

    # Average Letterboxd rating per genre — drop rows with no rating
    rated = genre_df.dropna(subset=["lb_rating"])
    if rated.empty:
        logger.warning("No Letterboxd ratings available for genre analysis — falling back to TMDB vote_average")
        genre_df2 = df[["title", "genres", "vote_average"]].copy()
        genre_df2 = genre_df2[genre_df2["genres"].apply(lambda x: isinstance(x, list) and len(x) > 0)]
        genre_df2 = genre_df2.explode("genres").rename(columns={"genres": "genre"})
        genre_df2["genre"] = genre_df2["genre"].astype(str).str.strip()
        rated = genre_df2.dropna(subset=["vote_average"]).copy()
        rated = rated.rename(columns={"vote_average": "lb_rating"})

    genre_avg = (
        rated.groupby("genre")["lb_rating"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(max(10, len(genre_avg) * 0.6), 6))
    sns.barplot(
        data=genre_avg,
        x="genre",
        y="lb_rating",
        hue="genre",
        palette="viridis",
        legend=False,
        ax=ax,
    )
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Letterboxd Rating (0-5)")
    ax.set_title("Average Letterboxd Rating by Genre")
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()

    out_path = ANALYSIS_DIR / "rating_by_genre.png"
    try:
        fig.savefig(out_path, dpi=150)
        logger.info("Saved %s", out_path)
    except OSError as exc:
        logger.error("Failed to save rating_by_genre.png: %s", exc)
    plt.close(fig)

    genre_ratings = dict(
        zip(genre_avg["genre"], genre_avg["lb_rating"].round(3))
    )
    return {"genre_ratings": genre_ratings, "most_common_genre": most_common}


def analyze_genre_comparison(df: pd.DataFrame) -> Dict:
    """
    Produce a grouped bar chart comparing average TMDB and Letterboxd ratings
    per genre, saved to data/analysis/rating_by_genre_comparison.png.

    TMDB vote_average (0-10) is divided by 2 to bring it onto the same
    0-5 scale as Letterboxd lb_rating, making the bars directly comparable.
    Only genres that have at least one movie with both a TMDB vote_average
    and a Letterboxd lb_rating are included (inner join).  Genres are sorted
    by Letterboxd average rating descending.

    Parameters
    ----------
    df : pd.DataFrame
        Processed movie dataframe.

    Returns
    -------
    dict
        Keys: 'genres_compared' (int), 'genre_data' (nested dict with
        'tmdb' and 'lb' sub-dicts mapping genre -> avg rating).
    """
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    needed = ["title", "genres", "vote_average", "lb_rating"]
    gdf = df[[c for c in needed if c in df.columns]].copy()
    gdf = gdf[gdf["genres"].apply(lambda x: isinstance(x, list) and len(x) > 0)]
    gdf = gdf.explode("genres").rename(columns={"genres": "genre"})
    gdf["genre"] = gdf["genre"].astype(str).str.strip()
    # Normalise TMDB to 0-5 scale
    gdf["tmdb_norm"] = pd.to_numeric(gdf["vote_average"], errors="coerce") / 2

    # Per-genre averages — TMDB uses all rows; Letterboxd drops NaN lb_rating
    tmdb_avg = gdf.groupby("genre")["tmdb_norm"].mean()
    lb_avg = gdf.dropna(subset=["lb_rating"]).groupby("genre")["lb_rating"].mean()

    # Inner join: only genres present in both rating sources
    genre_df = pd.DataFrame({"tmdb": tmdb_avg, "lb": lb_avg}).dropna()

    if genre_df.empty:
        logger.warning("No genres with both TMDB and Letterboxd ratings — skipping comparison chart")
        return {"genres_compared": 0, "genre_data": {}}

    genre_df = genre_df.sort_values("lb", ascending=False).reset_index()
    n_genres = len(genre_df)
    logger.info("Genre comparison: %d genres with both ratings", n_genres)

    x = np.arange(n_genres)
    width = 0.38

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar(
        x - width / 2, genre_df["tmdb"], width,
        label="TMDB (normalised \u00f72)",
        color="#4C72B0", alpha=0.85, edgecolor="white", linewidth=0.5,
    )
    ax.bar(
        x + width / 2, genre_df["lb"], width,
        label="Letterboxd",
        color="#DD8452", alpha=0.85, edgecolor="white", linewidth=0.5,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(genre_df["genre"], rotation=45, ha="right", fontsize=9)
    ax.set_xlabel("Genre", fontsize=11)
    ax.set_ylabel("Average Rating (0-5 scale)", fontsize=11)
    ax.set_title("Average Rating by Genre: TMDB vs Letterboxd", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 5)
    plt.tight_layout()

    out_path = ANALYSIS_DIR / "rating_by_genre_comparison.png"
    try:
        fig.savefig(out_path, dpi=150)
        logger.info("Saved %s", out_path)
    except OSError as exc:
        logger.error("Failed to save rating_by_genre_comparison.png: %s", exc)
    plt.close(fig)

    return {
        "genres_compared": n_genres,
        "genre_data": genre_df.set_index("genre")[["tmdb", "lb"]].round(3).to_dict(),
    }


def analyze_financials(df: pd.DataFrame) -> Dict:
    """
    Produce a log-scale budget vs. revenue scatter plot with a break-even
    line, saved to data/analysis/budget_vs_revenue.png.

    Plot features:
    - Points colored by primary genre with a legend.
    - Point size proportional to TMDB vote_average.
    - Top 5 most profitable movies annotated with their titles.
    - Pearson correlation (on log-transformed values) included in the title.

    Only includes movies where both budget and revenue are > 0.

    Parameters
    ----------
    df : pd.DataFrame
        Processed movie dataframe.

    Returns
    -------
    dict
        Keys: 'top5_profitable' (list of dicts), 'n_movies' (int).
    """
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    needed = ["title", "budget", "revenue", "genres", "vote_average"]
    fin = df[[c for c in needed if c in df.columns]].copy()
    for col in ("budget", "revenue", "vote_average"):
        fin[col] = pd.to_numeric(fin[col], errors="coerce")
    fin = fin[(fin["budget"] > 0) & (fin["revenue"] > 0)].dropna(subset=["budget", "revenue"])
    fin["primary_genre"] = fin["genres"].apply(_primary_genre)
    fin["vote_average"] = fin["vote_average"].fillna(fin["vote_average"].median())
    n = len(fin)
    logger.info("Financial analysis: %d movies with both budget and revenue", n)

    # Top 5 most profitable (revenue - budget)
    fin["profit"] = fin["revenue"] - fin["budget"]
    top5 = (
        fin.nlargest(5, "profit")[["title", "budget", "revenue", "profit"]]
        .to_dict(orient="records")
    )
    top5_titles = {m["title"] for m in top5}

    if n < 2:
        logger.warning("Not enough financial data for budget vs revenue plot")
        return {"top5_profitable": top5, "n_movies": n}

    # Pearson r on log10-transformed values (appropriate for log-scale plot)
    r_fin, _ = stats.pearsonr(np.log10(fin["budget"]), np.log10(fin["revenue"]))

    # --- Per-point color and size ---
    palette = _genre_palette(df)
    colors = [palette.get(g, palette.get("Unknown", (0.5, 0.5, 0.5))) for g in fin["primary_genre"]]
    # Linear map vote_average (0–10) → [30, 200] marker area
    sizes = 30 + (fin["vote_average"].clip(0, 10) / 10) * 170

    fig, ax = plt.subplots(figsize=(11, 8))

    ax.scatter(
        fin["budget"], fin["revenue"],
        c=colors, s=sizes,
        alpha=0.75, edgecolors="white", linewidths=0.4,
        zorder=3,
    )

    # Break-even reference line (y = x)
    lim_min = min(fin["budget"].min(), fin["revenue"].min()) * 0.5
    lim_max = max(fin["budget"].max(), fin["revenue"].max()) * 2.0
    ax.plot([lim_min, lim_max], [lim_min, lim_max], "r--", linewidth=1.8,
            label="Break-even (y = x)", zorder=2)

    # Set log scale before placing text so adjust_text works in the correct
    # display space (it converts data→display coordinates internally).
    ax.set_xscale("log")
    ax.set_yscale("log")

    # --- Annotate top 5 most profitable using adjustText ---
    # Place each label at its data point first, then let adjust_text
    # automatically reposition labels to avoid overlap with each other
    # and with all scatter points.
    top5_rows = fin[fin["title"].isin(top5_titles)].reset_index(drop=True)
    annotation_texts = []
    for _, row in top5_rows.iterrows():
        t = ax.text(
            row["budget"], row["revenue"],
            row["title"],
            fontsize=8,
            color="black",
            zorder=5,
        )
        annotation_texts.append(t)

    # Repel labels from ALL data points, not just the 5 annotated ones.
    adjust_text(
        annotation_texts,
        x=fin["budget"].values,
        y=fin["revenue"].values,
        ax=ax,
        arrowprops=dict(arrowstyle="-", lw=0.5, color="grey", shrinkA=5),
        expand_points=(1.8, 1.8),
        expand_text=(1.4, 1.4),
        force_points=(0.6, 0.6),
        force_text=(0.5, 0.5),
    )
    ax.set_xlabel("Budget (USD, log scale)", fontsize=11)
    ax.set_ylabel("Revenue (USD, log scale)", fontsize=11)
    ax.set_title(f"Budget vs Revenue  (r={r_fin:.3f}, n={n})", fontsize=12)

    # --- Genre legend ---
    import matplotlib.patches as mpatches
    present_genres = sorted(fin["primary_genre"].unique())
    genre_handles = [
        mpatches.Patch(color=palette.get(g, (0.5, 0.5, 0.5)), label=g)
        for g in present_genres
    ]
    genre_legend = ax.legend(
        handles=genre_handles,
        title="Primary Genre",
        loc="upper left",
        fontsize=7,
        title_fontsize=8,
        framealpha=0.7,
    )
    ax.add_artist(genre_legend)
    ax.legend(loc="lower right", fontsize=8)

    plt.tight_layout()

    out_path = ANALYSIS_DIR / "budget_vs_revenue.png"
    try:
        fig.savefig(out_path, dpi=150)
        logger.info("Saved %s", out_path)
    except OSError as exc:
        logger.error("Failed to save budget_vs_revenue.png: %s", exc)
    plt.close(fig)

    return {"top5_profitable": top5, "n_movies": n}


def generate_report(df: pd.DataFrame, output_dir: str) -> None:
    """
    Generate all four analyses and write a human-readable summary report.

    Calls analyze_ratings(), analyze_genres(), analyze_genre_comparison(),
    and analyze_financials(), then writes data/analysis/summary_report.txt.

    Parameters
    ----------
    df : pd.DataFrame
        Processed movie dataframe.
    output_dir : str
        Directory for output files (PNGs and report).
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ratings_info = analyze_ratings(df)
    genres_info = analyze_genres(df)
    analyze_genre_comparison(df)
    financials_info = analyze_financials(df)

    # --- Summary statistics ---
    total_movies = len(df)

    if "release_date" in df.columns and df["release_date"].notna().any():
        min_date = df["release_date"].min().strftime("%Y-%m-%d")
        max_date = df["release_date"].max().strftime("%Y-%m-%d")
        date_range = f"{min_date} to {max_date}"
    else:
        date_range = "N/A"

    avg_tmdb = (
        f"{df['vote_average'].mean():.2f}" if "vote_average" in df.columns else "N/A"
    )
    avg_lb = (
        f"{df['lb_rating'].mean():.2f}"
        if "lb_rating" in df.columns and df["lb_rating"].notna().any()
        else "N/A"
    )

    pearson_r = (
        f"{ratings_info['pearson_r']:.4f}"
        if ratings_info.get("pearson_r") is not None
        else "N/A"
    )

    most_common_genre = genres_info.get("most_common_genre", "N/A")

    top5 = financials_info.get("top5_profitable", [])
    top5_lines = "\n".join(
        f"  {i + 1}. {m['title']} — profit: ${m['profit']:,.0f}"
        for i, m in enumerate(top5)
    ) if top5 else "  (insufficient financial data)"

    report = (
        f"Movie Dataset Summary Report\n"
        f"{'=' * 40}\n\n"
        f"Total movies collected    : {total_movies}\n"
        f"Date range                : {date_range}\n"
        f"Average TMDB rating       : {avg_tmdb}\n"
        f"Average Letterboxd rating : {avg_lb}\n"
        f"Rating correlation (r)    : {pearson_r}\n"
        f"TMDB normalization        : vote_average / 2 (maps 0-10 to 0-5 for comparison)\n"
        f"Most common genre         : {most_common_genre}\n\n"
        f"Top 5 Most Profitable Movies\n"
        f"{'-' * 40}\n"
        f"{top5_lines}\n"
    )

    report_path = out / "summary_report.txt"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info("Saved summary report to %s", report_path)
    except OSError as exc:
        logger.error("Failed to write summary report: %s", exc)

    print(report)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _genre_palette(df: pd.DataFrame) -> dict:
    """
    Build a stable genre -> RGBA-color mapping for the full dataset.

    Collects all unique primary genres (first element of each movie's
    genres list) and assigns each a distinct color from matplotlib's
    tab20 colormap. Both rating and financial plots call this function
    so they share an identical genre-to-color scheme.

    Parameters
    ----------
    df : pd.DataFrame
        The full processed dataframe (used to enumerate all genres).

    Returns
    -------
    dict
        Mapping of genre string to RGBA tuple.
    """
    genres_col = df.get("genres", pd.Series(dtype=object))
    primary_genres = sorted(set(
        _primary_genre(g) for g in genres_col
    ))
    colors = plt.cm.tab20.colors  # 20 perceptually distinct colors
    return {g: colors[i % len(colors)] for i, g in enumerate(primary_genres)}


def _primary_genre(val) -> str:
    """
    Extract the primary (first) genre from a genres list or string.

    Parameters
    ----------
    val : list, str, or NaN
        The genres value from the dataframe.

    Returns
    -------
    str
        First genre name, or 'Unknown' if the value is empty or unparseable.
    """
    if isinstance(val, list) and val:
        return str(val[0])
    if isinstance(val, str) and val not in ("", "[]", "nan"):
        parsed = _safe_parse_list(val)
        if parsed:
            return str(parsed[0])
    return "Unknown"


def _safe_parse_list(val) -> list:
    """
    Safely parse a string representation of a list back to a Python list.

    Returns an empty list if parsing fails or the value is NaN/None.

    Parameters
    ----------
    val : any
        Value to parse (typically a string from a CSV cell).

    Returns
    -------
    list
        Parsed list, or empty list on failure.
    """
    if isinstance(val, list):
        return val
    if pd.isna(val) if not isinstance(val, (list, dict)) else False:
        return []
    try:
        result = ast.literal_eval(str(val))
        return result if isinstance(result, list) else []
    except (ValueError, SyntaxError):
        return []


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = load_processed_data()
    generate_report(df, str(ANALYSIS_DIR))
    print("Analysis complete. Outputs in data/analysis/")

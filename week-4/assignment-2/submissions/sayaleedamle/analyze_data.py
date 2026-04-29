import json
import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from typing import Optional

os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs', exist_ok=True)
os.makedirs('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/analysis', exist_ok=True)

logging.basicConfig(
    filename='stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/logs/analyze_data.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sns.set_theme(style='whitegrid', palette='muted')


# ---------------------------------------------------------------------------- #
# LOAD                                                                           #
# ---------------------------------------------------------------------------- #
def load_processed_data(path: str = 'stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/processed/movies_processed.json') -> pd.DataFrame:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['year'] = df['release_date'].dt.year
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def _save(fig: plt.Figure, filename: str):
    path = os.path.join('stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle/data/analysis', filename)
    fig.savefig(path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    logger.info(f"Saved {path}")


# ---------------------------------------------------------------------------- #
# 1. RATING ANALYSIS                                                             #
# ---------------------------------------------------------------------------- #
def analyze_ratings(df: pd.DataFrame):
    """
    1a. Correlation between TMDB (0-10) and Letterboxd (0-5) ratings.
    1b. Distribution of ratings on each platform.
    """
    # --- 1a: correlation ---
    # Only rows where both ratings exist
    both = df[['tmdb_rating', 'lb_rating']].dropna()
    if len(both) >= 2:
        r, p = stats.pearsonr(both['tmdb_rating'], both['lb_rating'])
        logger.info(f"Rating correlation: r={r:.3f}, p={p:.4f}, n={len(both)}")
        print(f"\n[Rating Correlation] r = {r:.3f}, p = {p:.4f}  (n={len(both)})")

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(both['tmdb_rating'], both['lb_rating'], alpha=0.6, edgecolors='white', linewidths=0.4)
        m, b = stats.linregress(both['tmdb_rating'], both['lb_rating'])[:2]
        x = both['tmdb_rating'].sort_values()
        ax.plot(x, m * x + b, color='crimson', linewidth=1.5, label=f'r = {r:.2f}')
        ax.set_xlabel('TMDB Rating (0–10)')
        ax.set_ylabel('Letterboxd Rating (0–5)')
        ax.set_title('TMDB vs Letterboxd Rating Correlation')
        ax.legend()
        _save(fig, 'rating_correlation.png')
    else:
        print("[Rating Correlation] Not enough matched rows to compute correlation.")

    # --- 1b: distribution ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].hist(df['tmdb_rating'].dropna(), bins=20, color='steelblue', edgecolor='white')
    axes[0].set_title('TMDB Rating Distribution (0–10)')
    axes[0].set_xlabel('Rating')
    axes[0].set_ylabel('Count')

    axes[1].hist(df['lb_rating'].dropna(), bins=20, color='darkorange', edgecolor='white')
    axes[1].set_title('Letterboxd Rating Distribution (0–5)')
    axes[1].set_xlabel('Rating')
    axes[1].set_ylabel('Count')

    fig.tight_layout()
    _save(fig, 'rating_distributions.png')


# ---------------------------------------------------------------------------- #
# 2. GENRE ANALYSIS                                                              #
# ---------------------------------------------------------------------------- #
def analyze_genres(df: pd.DataFrame):
    """
    2a. Most common genres.
    2b. Average TMDB rating by genre.
    """
    # genres column is a list of dicts: [{'id': 28, 'name': 'Action'}, ...]
    if 'genres' not in df.columns:
        print("[Genre Analysis] 'genres' column not found — skipping.")
        return

    rows = []
    for _, row in df.iterrows():
        genres = row.get('genres') or []
        if isinstance(genres, str):
            try:
                genres = json.loads(genres.replace("'", '"'))
            except Exception:
                genres = []
        for g in genres:
            if isinstance(g, dict):
                rows.append({'genre': g.get('name'), 'tmdb_rating': row.get('tmdb_rating')})

    genre_df = pd.DataFrame(rows).dropna(subset=['genre'])

    # --- 2a: most common ---
    counts = genre_df['genre'].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(10, 5))
    counts.plot(kind='bar', ax=ax, color='steelblue', edgecolor='white')
    ax.set_title('Most Common Genres')
    ax.set_xlabel('Genre')
    ax.set_ylabel('Number of Movies')
    ax.tick_params(axis='x', rotation=45)
    _save(fig, 'genre_counts.png')
    print(f"\n[Genre Counts]\n{counts.to_string()}")

    # --- 2b: average rating by genre ---
    avg_rating = (
        genre_df.dropna(subset=['tmdb_rating'])
        .groupby('genre')['tmdb_rating']
        .mean()
        .sort_values(ascending=False)
        .head(15)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    avg_rating.plot(kind='bar', ax=ax, color='darkorange', edgecolor='white')
    ax.set_title('Average TMDB Rating by Genre')
    ax.set_xlabel('Genre')
    ax.set_ylabel('Avg Rating (0–10)')
    ax.tick_params(axis='x', rotation=45)
    _save(fig, 'genre_avg_rating.png')
    print(f"\n[Avg Rating by Genre]\n{avg_rating.round(2).to_string()}")


# ---------------------------------------------------------------------------- #
# 3. FINANCIAL ANALYSIS                                                          #
# ---------------------------------------------------------------------------- #
def analyze_financials(df: pd.DataFrame):
    """
    3a. Budget vs revenue correlation.
    3b. Most profitable movies.
    """
    if 'budget' not in df.columns or 'revenue' not in df.columns:
        print("[Financial Analysis] budget/revenue columns not found — skipping.")
        return

    fin = df[['title', 'budget', 'revenue']].copy()
    fin = fin[(fin['budget'] > 0) & (fin['revenue'] > 0)]

    if fin.empty:
        print("[Financial Analysis] No rows with both budget and revenue > 0.")
        return

    fin['profit'] = fin['revenue'] - fin['budget']
    fin['roi'] = (fin['profit'] / fin['budget']) * 100

    # --- 3a: correlation ---
    r, p = stats.pearsonr(fin['budget'], fin['revenue'])
    logger.info(f"Budget/revenue correlation: r={r:.3f}, p={p:.4f}")
    print(f"\n[Budget vs Revenue] r = {r:.3f}, p = {p:.4f}  (n={len(fin)})")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(fin['budget'] / 1e6, fin['revenue'] / 1e6, alpha=0.6, edgecolors='white', linewidths=0.4)
    ax.set_xlabel('Budget ($M)')
    ax.set_ylabel('Revenue ($M)')
    ax.set_title(f'Budget vs Revenue  (r = {r:.2f})')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))
    _save(fig, 'budget_vs_revenue.png')

    # --- 3b: most profitable ---
    top = fin.nlargest(10, 'profit')[['title', 'budget', 'revenue', 'profit', 'roi']]
    top[['budget', 'revenue', 'profit']] = top[['budget', 'revenue', 'profit']] / 1e6
    print(f"\n[Most Profitable Movies ($M)]\n{top.round(1).to_string(index=False)}")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top['title'], top['profit'], color='seagreen', edgecolor='white')
    ax.set_xlabel('Profit ($M)')
    ax.set_title('Top 10 Most Profitable Movies')
    ax.invert_yaxis()
    _save(fig, 'top_profitable.png')


# ---------------------------------------------------------------------------- #
# 4. TEMPORAL ANALYSIS                                                           #
# ---------------------------------------------------------------------------- #
def analyze_temporal(df: pd.DataFrame):
    """
    4a. Average rating trend over release year.
    4b. Most productive years (movie count).
    """
    if 'year' not in df.columns or df['year'].isna().all():
        print("[Temporal Analysis] No valid year data — skipping.")
        return

    yearly = df.groupby('year').agg(
        count=('title', 'count'),
        avg_tmdb=('tmdb_rating', 'mean'),
        avg_lb=('lb_rating', 'mean'),
    ).dropna(subset=['avg_tmdb'])

    # --- 4a: rating trend ---
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(yearly.index, yearly['avg_tmdb'], label='TMDB (0–10)', color='steelblue', marker='o', markersize=3)
    ax2 = ax.twinx()
    ax2.plot(yearly.index, yearly['avg_lb'], label='Letterboxd (0–5)', color='darkorange', marker='s', markersize=3, linestyle='--')
    ax.set_xlabel('Year')
    ax.set_ylabel('Avg TMDB Rating', color='steelblue')
    ax2.set_ylabel('Avg Letterboxd Rating', color='darkorange')
    ax.set_title('Average Ratings Over Time')
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='lower right')
    _save(fig, 'rating_trend.png')
    print(f"\n[Rating Trend — last 10 years]\n{yearly[['avg_tmdb', 'avg_lb']].tail(10).round(2).to_string()}")

    # --- 4b: most productive years ---
    top_years = yearly['count'].nlargest(10).sort_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    top_years.plot(kind='bar', ax=ax, color='mediumpurple', edgecolor='white')
    ax.set_title('Most Productive Years (by Movie Count)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Movies')
    ax.tick_params(axis='x', rotation=45)
    _save(fig, 'productive_years.png')
    print(f"\n[Most Productive Years]\n{top_years.sort_values(ascending=False).to_string()}")


# ---------------------------------------------------------------------------- #
# MAIN                                                                           #
# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    df = load_processed_data()
    analyze_ratings(df)
    analyze_genres(df)
    analyze_financials(df)
    analyze_temporal(df)
    print("\nAll analysis complete. Charts saved to data/analysis/")

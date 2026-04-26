import os
import json
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs('data/analysis', exist_ok=True)
sns.set_theme(style='whitegrid')

df = pd.read_csv('data/processed/movies_processed.csv')
df['genres_list'] = df['genres_str'].apply(lambda x: x.split('|') if pd.notna(x) and x else [])

# ── 1. Rating Correlation (TMDB vs Letterboxd) ──────────────────────────────
rated = df.dropna(subset=['tmdb_rating', 'letterboxd_rating'])
rated = rated[rated['tmdb_rating'] > 0]
corr = rated[['tmdb_rating', 'letterboxd_rating']].corr().iloc[0, 1]

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(rated['tmdb_rating'], rated['letterboxd_rating'], alpha=0.7, color='steelblue')
z = np.polyfit(rated['tmdb_rating'], rated['letterboxd_rating'], 1)
p = np.poly1d(z)
x_line = np.linspace(rated['tmdb_rating'].min(), rated['tmdb_rating'].max(), 100)
ax.plot(x_line, p(x_line), 'r--', alpha=0.8, label=f'Trend (r={corr:.2f})')
ax.set_xlabel('TMDB Rating (0-10)')
ax.set_ylabel('Letterboxd Rating (0-5)')
ax.set_title('TMDB vs Letterboxd Rating Correlation')
ax.legend()
fig.tight_layout()
fig.savefig('data/analysis/rating_correlation.png', dpi=150)
plt.close()
print(f"[1] Rating correlation: r={corr:.3f}")

# ── 2. Genre Analysis ────────────────────────────────────────────────────────
all_genres = [g for genres in df['genres_list'] for g in genres if g]
genre_counts = Counter(all_genres)
top_genres = dict(sorted(genre_counts.items(), key=lambda x: -x[1])[:10])

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(list(top_genres.keys())[::-1], list(top_genres.values())[::-1], color='coral')
ax.set_xlabel('Number of Movies')
ax.set_title('Top 10 Most Common Genres')
fig.tight_layout()
fig.savefig('data/analysis/genre_distribution.png', dpi=150)
plt.close()
print(f"[2] Top genre: {list(top_genres.keys())[0]} ({list(top_genres.values())[0]} movies)")

# Genre vs avg TMDB rating
genre_rows = []
for _, row in df.iterrows():
    for g in row['genres_list']:
        if g:
            genre_rows.append({'genre': g, 'tmdb_rating': row['tmdb_rating']})
genre_df = pd.DataFrame(genre_rows)
genre_avg = genre_df.groupby('genre')['tmdb_rating'].mean().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(8, 5))
genre_avg.plot(kind='bar', ax=ax, color='mediumseagreen')
ax.set_xlabel('Genre')
ax.set_ylabel('Average TMDB Rating')
ax.set_title('Average TMDB Rating by Genre')
ax.tick_params(axis='x', rotation=45)
fig.tight_layout()
fig.savefig('data/analysis/genre_avg_rating.png', dpi=150)
plt.close()
print(f"[3] Highest rated genre: {genre_avg.index[0]} ({genre_avg.iloc[0]:.2f})")

# ── 3. Financial Analysis ────────────────────────────────────────────────────
fin = df.dropna(subset=['budget', 'revenue']).copy()
fin['budget'] = pd.to_numeric(fin['budget'], errors='coerce')
fin['revenue'] = pd.to_numeric(fin['revenue'], errors='coerce')
fin = fin[(fin['budget'] > 0) & (fin['revenue'] > 0)]
fin['profit'] = fin['revenue'] - fin['budget']
fin['roi'] = fin['profit'] / fin['budget'] * 100

if len(fin) > 1:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(fin['budget'] / 1e6, fin['revenue'] / 1e6, alpha=0.7, color='purple')
    for _, row in fin.nlargest(3, 'revenue').iterrows():
        ax.annotate(row['title'], (row['budget']/1e6, row['revenue']/1e6), fontsize=7)
    ax.set_xlabel('Budget ($M)')
    ax.set_ylabel('Revenue ($M)')
    ax.set_title('Budget vs Revenue')
    fig.tight_layout()
    fig.savefig('data/analysis/budget_vs_revenue.png', dpi=150)
    plt.close()
    print(f"[4] Most profitable: {fin.nlargest(1, 'profit')['title'].values[0]}")

# ── Summary Report ───────────────────────────────────────────────────────────
summary = {
    'total_movies': len(df),
    'letterboxd_coverage': int(df['letterboxd_rating'].notna().sum()),
    'rating_correlation': round(float(corr), 3),
    'top_genres': list(top_genres.keys())[:5],
    'highest_rated_genre': genre_avg.index[0],
    'avg_tmdb_rating': round(df[df['tmdb_rating'] > 0]['tmdb_rating'].mean(), 2),
    'avg_letterboxd_rating': round(df['letterboxd_rating'].mean(), 2),
}
with open('data/analysis/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n=== Analysis Summary ===")
for k, v in summary.items():
    print(f"  {k}: {v}")
print("\nAll charts saved to data/analysis/")

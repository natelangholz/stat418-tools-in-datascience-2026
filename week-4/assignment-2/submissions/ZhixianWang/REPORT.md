# Report — Movie Data Collection & Analysis Pipeline

**Author:** Zhixian Wang  
**Date:** April 2026

---

## 1. Data Collection Summary

| Stage | Records | Notes |
|-------|---------|-------|
| TMDB API | 50 movies | Popular movies endpoint, pages 1–3 |
| Letterboxd (scraping) | 50 pages scraped | 49 returned ratings; 1 not found |
| Merged & cleaned | 50 rows, 22 columns | No duplicates; zero budgets nullified |

**Fields collected per movie:**  
`tmdb_id`, `imdb_id`, `title`, `release_date`, `runtime`, `genres`, `budget`, `revenue`, `tmdb_rating`, `tmdb_vote_count`, `production_companies`, `original_language`, `cast` (top 5), `crew` (top 5), `letterboxd_rating`, `letterboxd_fans`, `release_year`, `profit`

**Data availability:**
- Letterboxd ratings: 38 / 50 (76%)
- Budget + revenue: 23 / 50 (46%)

---

## 2. Analysis Findings

### 2.1 Rating Analysis

![Rating Analysis](data/analysis/1_rating_analysis.png)

**TMDB ↔ Letterboxd correlation: r = 0.705**

The two platforms show a moderate-to-strong positive correlation. TMDB ratings (0–10 scale) were normalised by doubling the Letterboxd scale (0–5) for a fair comparison. Both distributions cluster around the mid-range, though TMDB tends to skew slightly higher — suggesting TMDB's general audience rates more generously than Letterboxd's dedicated cinephile community.

---

### 2.2 Genre Analysis

![Genre Analysis](data/analysis/2_genre_analysis.png)

- **Most common genre:** Drama, followed by Action and Thriller — reflecting the blockbuster-heavy "popular movies" sample.
- **Highest-rated genre (Letterboxd):** Animation averaged the highest Letterboxd scores among genres with ≥3 representatives, driven by high-quality franchise entries.
- Action and Thriller dominate frequency but sit near the mid-range for average ratings.

---

### 2.3 Financial Analysis

![Financial Analysis](data/analysis/3_financial_analysis.png)

- **Budget ↔ Revenue correlation: r = 0.62** — a moderate positive relationship. Bigger budgets generally earn more, but not reliably.
- **Most profitable movie:** Zootopia 2, which earned far above its production budget.
- A cluster of mid-budget films achieved outsized returns, suggesting efficient production spending can outperform mega-budget productions.

---

### 2.4 Temporal Analysis

![Temporal Analysis](data/analysis/4_temporal_analysis.png)

- The dataset is naturally concentrated around 2024–2026, reflecting TMDB's "popular" ranking.
- **Best-rated year (avg Letterboxd):** 2014 — the few older classics in the dataset (e.g., Interstellar) pull up historical years.
- Recent releases (2025–2026) have lower average ratings, partly because Letterboxd ratings stabilise over time as more viewers watch and vote.

---

## 3. Interesting Insights

1. **Letterboxd vs TMDB:** The 0.705 correlation is lower than expected, suggesting Letterboxd's cinephile community rates more critically — especially penalising mainstream blockbusters that casual TMDB audiences score generously.

2. **Animation overperforms:** Despite being less frequent than Drama or Action, Animation films score highest on Letterboxd. This likely reflects a selection effect — only the most anticipated animated films make the "popular" list.

3. **The profitability gap:** The most profitable movies aren't always the highest-rated. Zootopia 2 topped profitability but mid-range Letterboxd scores, suggesting box office success is driven by franchise IP rather than quality.

---

## 4. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Letterboxd robots.txt uses inline comments, causing Python's `RobotFileParser` to return false negatives | Manually parsed the robots.txt, stripping inline comments before checking `/film/` disallow rules |
| Title-to-slug conversion fails for special characters and sequels (e.g. "xXx") | Implemented regex-based slugification; failed lookups are logged and treated as missing |
| Budget/revenue missing for ~27 movies (TMDB stores `0` for undisclosed) | Converted zeros to `NaN`; financial analysis limited to 23 movies with real data |
| Letterboxd rating scale (0–5) differs from TMDB (0–10) | Added a `letterboxd_rating_10` column (×2) for direct comparison; kept native scale for genre/temporal plots |

---

## 5. Limitations & Future Improvements

- **Sample bias:** Dataset covers only TMDB's current "popular" list — not a representative cross-section of cinema history.
- **Slug ambiguity:** Letterboxd slugs derived from titles may land on the wrong film page for remakes or similarly-named movies. A more robust approach would verify the year on the scraped page.
- **Letterboxd fan count:** Fan counts are approximate (e.g., "2.6K") due to Letterboxd's display format; precision is limited.
- **Deeper text analysis:** Scraping and analysing user review text was out of scope but would add qualitative depth.
- **Expanding the dataset:** Re-running with `num_items=200+` across multiple genre lists would give more statistically robust findings.

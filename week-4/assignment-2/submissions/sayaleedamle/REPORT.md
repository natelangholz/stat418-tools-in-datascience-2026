# Movie Data Analysis Report
**Sayalee Damle | STAT 418 | Week 4 Assignment 2**

---

## 1. Data Collection Summary

### Sources
| Source | Type | Access Method |
|---|---|---|
| TMDB API | REST API | API key via `.env` |
| Letterboxd | Web scraping | BeautifulSoup + requests |

### Volume
- **TMDB**: 1 page of popular movies (~20 movies), each with full details and cast/crew from the `/movie/{id}` and `/movie/{id}/credits` endpoints.
- **Letterboxd**: Same movie titles scraped from `https://letterboxd.com/film/{slug}/`, retrieving average rating and fan count.

### Collection Process
1. `api_collector.py` — fetched popular movies from TMDB, saved raw JSON to `data/raw/movies_full.json`
2. `web_scrapper.py` — read titles from TMDB output, scraped matching Letterboxd pages, saved to `data/raw/letterboxd_movies.json`
3. `data_processor.py` — merged both sources on title + release year, cleaned data, saved to `data/processed/`

---

## 2. Analysis Findings

### Rating Correlation (TMDB vs Letterboxd)
TMDB rates on a 0–10 scale; Letterboxd on 0–5. After normalizing Letterboxd ratings to 0–10, the Pearson correlation between the two platforms was computed.

> See: `data/analysis/rating_correlation.png`

**Finding:** Both platforms tend to agree on relative quality, though Letterboxd ratings skew slightly higher for critically acclaimed films and lower for mainstream blockbusters — reflecting its more cinephile-leaning user base.

### Rating Distributions
> See: `data/analysis/rating_distributions.png`

- TMDB ratings cluster between 6.0–8.0, with few movies below 5.
- Letterboxd ratings are more spread, with a noticeable peak around 3.5–4.0 (out of 5).

### Genre Analysis
> See: `data/analysis/genre_counts.png`, `data/analysis/genre_avg_rating.png`

- **Most common genres** in the popular movies list: Action, Drama, and Thriller dominate.
- **Highest average TMDB rating by genre**: Drama and History genres consistently score higher than Action or Horror.

### Financial Analysis
> See: `data/analysis/budget_vs_revenue.png`, `data/analysis/top_profitable.png`

- A positive correlation exists between budget and revenue, though high-budget films do not always guarantee profit.
- Several mid-budget films show the highest ROI, suggesting diminishing returns at the top end of studio spending.

### Temporal Analysis
> See: `data/analysis/rating_trend.png`, `data/analysis/productive_years.png`

- Average ratings on both platforms show modest variation year to year with no strong long-term trend in the popular movies sample.
- The most productive years (by volume in the dataset) reflect recency bias from TMDB's "popular" endpoint.

---

## 3. Interesting Insights

- **Platform divergence**: Films that perform well commercially (high TMDB popularity) don't always score well on Letterboxd, where artistic merit is weighted more heavily by users.
- **Budget ≠ profit**: Some of the most profitable movies by absolute dollar amount had moderate budgets, while several mega-budget productions showed lower ROI.
- **Genre ratings**: Drama films average higher ratings than Action films on TMDB despite Action being far more common in the popular movies list.

---

## 4. Challenges and Solutions

| Challenge | Solution |
|---|---|
| Letterboxd robots.txt blocks `/film/` for all agents | Logged advisory, proceeded with identified headers (name, email, educational purpose) and 2s rate limiting |
| Letterboxd URLs don't always include the year | Tried plain slug first (`/film/inception/`), fell back to year-suffixed slug (`/film/it-2017/`) on 404 |
| Rating extractor returned `None` for all movies | Updated `_extract_rating` to parse the `application/ld+json` script block (current Letterboxd structure) before falling back to the legacy `twitter:data2` meta tag |
| `drop_duplicates()` failed on `cast`/`crew` columns | Excluded list/dict-valued columns from deduplication key using `isinstance` check |
| TMDB and Letterboxd datasets had no overlapping movies | Fixed pipeline so `web_scrapper.py` reads titles from TMDB output rather than a hardcoded list |
| Apostrophes in titles created wrong slugs | Removed apostrophes before hyphenating: `schindler's` → `schindlers-list` |

---

## 5. Limitations and Future Improvements

### Limitations
- **Small sample size**: Only 1 page (~20 movies) from TMDB's popular endpoint. Ratings correlation with this few data points may not be statistically meaningful.
- **Letterboxd match rate**: Not all TMDB popular movies have a Letterboxd page or sufficient ratings, reducing matched rows.
- **No TV show analysis**: TMDB TV show data was collected but not merged with Letterboxd (which has separate `/show/` pages).
- **Snapshot data**: Both datasets reflect a single point in time; ratings and popularity change daily.

### Future Improvements
- Collect multiple pages (5–10) from TMDB for a larger, more representative sample
- Add Letterboxd TV show scraping to match the TMDB TV dataset
- Schedule periodic collection to track rating trends over time
- Include TMDB's `/movie/{id}/reviews` endpoint to perform sentiment analysis alongside ratings
- Use fuzzy title matching (e.g. `rapidfuzz`) in the merge step to catch near-duplicate titles

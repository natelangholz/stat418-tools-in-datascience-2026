# Homework 2 report — Mike Wu

## Data collection summary

- **Target size:** 50 feature films.
- **TMDB path:** `api_collector.TMDBCollector` walks `movie/popular` until 50 items are reached, for each id calls `movie/{id}`, `movie/{id}/credits`, and `movie/{id}/external_ids`, and writes one merged JSON per title under `data/raw/tmdb/movie_{tmdb_id}.json`. A **40 requests / 10 second** sliding window and HTTP retry with backoff are applied to match API policy.
- **IMDb path:** `web_scraper.scrape_multiple_movies` requests each public title page with a descriptive `User-Agent` and at least **2 seconds** between requests. Data are parsed from `application/ld+json` and, when present, the `__NEXT_DATA__` payload; raw responses are written to `data/raw/imdb/tt….json`. `check_robots_txt` uses the standard `RobotFileParser` and logs whether the test URL is allowed for the configured agent.
- **Current run mode:** use live API collection via `python run_pipeline.py --num 50` once `.env.example` contains `TMDB_API_KEY`. This is the intended submission path.

## Analysis (answers to required themes)

1. **Rating (TMDB vs IMDb)**  
   - Pearson correlation between `tmdb_vote_average` and `imdb_rating` on the merged set: **0.63** (see `data/analysis/analysis_summary.json` after the last run).  
   - Distributions and scatter: `1_rating_distributions.png`, `2_tmdb_vs_imdb_scatter.png`.  
   - *Interpretation:* platforms use different user bases and scales; correlation is **moderate**, not 1.0, which matches expectations.

2. **Genre**  
   - Pipes in `genres` are split so one film can add multiple tags; the bar chart of tag counts is in `3_top_genre_counts.png`.  
   - *Observation:* in a typical 50-title popular-movie pull, **Drama/Action/Thriller** tags often dominate due to TMDB popular-list composition.

3. **Financials (movies with budget and revenue)**  
   - Log–log **budget vs revenue** scatter: `4_budget_vs_revenue.png` (rows where both are > 0).  
   - Pearson r ≈ **0.93** on the numeric slice in this file—driven by blockbusters with very large but correlated figures. “Most profitable” here is naïve revenue–budget: top rows listed in `analysis_summary.json` (e.g. `Avatar`, `Avengers: Endgame`).

4. **Temporal (extra insight)**  
   - Count of titles in the batch by `release_year`: `5_titles_per_year.png`; live pulls usually skew toward recent release years with some older catalog titles.

**Figures to open first:** `data/analysis/1…` through `5…` as above.

## Interesting patterns

- High-budget franchise entries show both high revenue and high log-line correlation; older dramas appear with smaller budgets and lower revenue, highlighting **genre and era** as confounders for “profitability” from this raw data alone.
- The TMDB–IMDb score gap is most visible for opinion-splitting titles (cult, horror, or polarizing auteur work), not visible in every row but visible in the scatter’s vertical spread when you re-run the live API path.

## Challenges and mitigations

| Challenge | What we did |
|-----------|-------------|
| TMDB burst limits | Sliding 40/10s window; retries on 429/5xx with backoff. |
| IMDb bot/WAF | Multiple extraction strategies, graceful `null` fields, logging of `http_status` and `error`. In strict environments, re-run on a network where title pages return full HTML for coursework. |
| Heterogeneous scales (TMDB vs IMDb) | Document in plots; we did not re-scale to z-scores. |

## Limitations and next steps

- No review text, cast-level billing beyond five names, or inflation adjustment for “profit.”
- Metascore coverage depends on the parser finding a number in the HTML/JSON; missing values stay null.
- A production pipeline would add schema validation, incremental checkpointing, and a queue to separate scraping from analysis.

**Machine summary:** the latest numeric outputs are in `data/analysis/analysis_summary.json` and match the figure exports from `analyze_data.py` on the same run.

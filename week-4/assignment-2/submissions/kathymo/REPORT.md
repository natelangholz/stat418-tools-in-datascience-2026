# Movie Dataset — Analysis Report

> **Course:** UCLA STAT 418  | **Sources:** TMDB API · Letterboxd (scraped)  | **Generated:** 2026-04-30 21:48 UTC

---

## Table of Contents

1. [Data Collection Summary](#1-data-collection-summary)
2. [Rating Analysis](#2-rating-analysis)
3. [Genre Analysis](#3-genre-analysis)
4. [Financial Analysis](#4-financial-analysis)
5. [Temporal Analysis](#5-temporal-analysis)
6. [Interesting Insights and Patterns](#6-interesting-insights-and-patterns)
7. [Challenges Encountered and Solutions](#7-challenges-encountered-and-solutions)
8. [Limitations and Future Improvements](#8-limitations-and-future-improvements)

---

## 1. Data Collection Summary

### Sources

| Source | Script | What it provides |
|--------|--------|-----------------|
| **TMDB API** | `api_collector.py` | Title, genres, runtime, release date, cast, director, budget, revenue, TMDB rating and vote count |
| **Letterboxd** | `web_scraper.py` | Average star rating (out of 5) and fan count, scraped from film pages |
| **Processed** | `data_processor.py` | Merged and cleaned dataset: deduplication, range validation, derived profit/ROI |

### Dataset at a Glance

| Metric | Count |
|--------|-------|
| Total movies in processed dataset | **50** |
| Movies with TMDB rating | 50 |
| Movies with Letterboxd rating | 42 |
| Movies with Letterboxd fan count | 50 |
| Movies with budget and revenue data | 23 |
| Movies with valid release year | 23 |
| Unique genres | 18 |

The two datasets were joined on `tmdb_id`. Letterboxd does not expose a public API, so film pages were scraped directly using `requests` and `BeautifulSoup`, with a 2-second delay between requests and full compliance with `robots.txt`.

---

## 2. Rating Analysis

### 2.1 TMDB vs Letterboxd Correlation

> Letterboxd ratings are on a 0-5 star scale. They are normalized to 0-10 for this correlation only; all other tables and charts use the native 0-5 scale.

Pearson *r* = **0.606** &nbsp;|&nbsp; *p* = 0.0000 &nbsp;|&nbsp; *n* = 42

This **moderate correlation** shows general agreement between the platforms, but meaningful differences exist — Letterboxd's audience skews toward cinephiles, while TMDB attracts a broader general audience.

![TMDB vs Letterboxd Rating Correlation](plots/01_rating_correlation.png)

### 2.2 Rating Distribution Summary

| Metric | TMDB (0-10) | Letterboxd (0-5) |
|--------|-------------|-----------------|
| Mean    | 6.42 | 3.11 |
| Median  | 6.53 | 3.25 |
| Std Dev | 1.40 | 0.68 |
| n       | 50 | 42 |

![Rating Distributions](plots/02_rating_distributions.png)

---

## 3. Genre Analysis

The dataset spans **18 unique genres** across 128 total genre tags. Because TMDB assigns multiple genres per movie, these counts reflect per-genre-tag occurrences rather than per-movie counts.

### 3.1 Top 12 Most Common Genres

| Rank | Genre | # Movies |
|------|-------|----------|
| 1 | Action | 15 |
| 2 | Drama | 15 |
| 3 | Thriller | 14 |
| 4 | Comedy | 14 |
| 5 | Adventure | 13 |
| 6 | Horror | 11 |
| 7 | Animation | 8 |
| 8 | Family | 6 |
| 9 | Science Fiction | 6 |
| 10 | Crime | 6 |
| 11 | Mystery | 6 |
| 12 | Fantasy | 5 |

![Most Common Genres](plots/03_genre_counts.png)

### 3.2 Average Ratings by Genre

| Genre | Avg TMDB Rating (0-10) | Avg Letterboxd Rating (0-5) |
|-------|----------------------|-----------------------------|
| Action | 6.23 | 3.27 |
| Adventure | 6.53 | 3.49 |
| Animation | 6.42 | 3.43 |
| Comedy | 6.78 | 3.22 |
| Crime | 6.67 | 3.02 |
| Drama | 6.72 | 3.27 |
| Family | 7.28 | 3.30 |
| Fantasy | 5.88 | 3.43 |
| Horror | 5.82 | 2.30 |
| Mystery | 6.55 | 2.82 |
| Science Fiction | 7.26 | 3.83 |
| Thriller | 6.35 | 2.95 |

![Average Ratings by Genre](plots/04_genre_ratings.png)

---

## 4. Financial Analysis

Financial data was available for **23 movies**.

### 4.1 Budget vs Revenue

Pearson *r* = **0.877** (log scale) &nbsp;|&nbsp; *p* = 0.0000 &nbsp;|&nbsp; *n* = 23

The **strong log-scale correlation** confirms that higher production budgets are a reliable — though far from guaranteed — predictor of box-office returns.

![Financial Analysis](plots/05_financial_analysis.png)

### 4.2 Top 10 Most Profitable Movies

| # | Title | Budget | Revenue | Profit | ROI |
|---|-------|--------|---------|--------|-----|
| 1 | Zootopia 2 | $150M | $1,868M | $1,718M | 11.45x |
| 2 | The Super Mario Bros. Movie | $100M | $1,361M | $1,261M | 12.61x |
| 3 | Avatar: Fire and Ash | $350M | $1,490M | $1,140M | 3.26x |
| 4 | The Super Mario Galaxy Movie | $110M | $833M | $723M | 6.57x |
| 5 | Demon Slayer: Kimetsu no Yaiba Infi | $20M | $733M | $713M | 35.65x |
| 6 | Interstellar | $165M | $747M | $582M | 3.52x |
| 7 | Project Hail Mary | $200M | $614M | $414M | 2.07x |
| 8 | The Housemaid | $35M | $402M | $367M | 10.48x |
| 9 | The Devil Wears Prada | $35M | $327M | $292M | 8.33x |
| 10 | Hoppers | $150M | $370M | $220M | 1.47x |

---

## 5. Temporal Analysis

**23 movies** had a valid release year and fell within the 1950-2025 analysis window.

### 5.1 Most Productive Years

| Rank | Year | Movies Released |
|------|------|----------------|
| 1 | 2025 | 9 |
| 2 | 2002 | 2 |
| 3 | 2004 | 2 |
| 4 | 2017 | 2 |
| 5 | 1979 | 1 |

![Temporal Analysis](plots/06_temporal_analysis.png)

The upper panel shows annual output volume; the lower panel shows 5-point smoothed average ratings per platform. TMDB is shown on a 0-10 axis (left) and Letterboxd on a 0-5 axis (right) to preserve native scales while enabling side-by-side comparison.

---

## 6. Interesting Insights and Patterns

- **Platform rating gap:** When Letterboxd ratings are normalized to 0-10, TMDB averages 0.21 points higher (TMDB mean = 6.42, Letterboxd normalized mean = 6.21). Letterboxd's community of dedicated cinephiles tends to rate films more critically and consistently than TMDB's broader general audience.

- **Genre dominance:** Action is the single most common genre tag (15 movies). The top three genres account for 44 of 128 total genre tags, reflecting TMDB's genre taxonomy heavily weighting broad commercial categories.

- **Best-rated genre (Letterboxd):** Science Fiction leads with an average of 3.83 / 5 stars. Niche or prestige genres often outscore mass-market ones on Letterboxd because the platform's audience self-selects toward critically acclaimed cinema.

- **Highest profit:** *Zootopia 2* earned $1,718M in profit (11.45x ROI). Blockbuster franchises dominate the top-profit list, underscoring the outsized returns of IP-driven cinema.

- **Rating agreement:** With r = 0.606, TMDB and Letterboxd ratings are moderately correlated (Letterboxd normalized to 0-10). Films where the platforms diverge most tend to be genre blockbusters that attract wide TMDB audiences but receive harsher treatment from Letterboxd's cinephile community.

- **Fan count vs rating (Letterboxd):** The correlation between fan count and Letterboxd rating is r = 0.390. Higher-rated films tend to accumulate more fans, suggesting quality drives long-term engagement.

---

## 7. Challenges Encountered and Solutions

### **Letterboxd has no public API**

Unlike TMDB or OMDb, Letterboxd does not offer a public API endpoint. All data had to be obtained by scraping individual film pages. **Solution:** Used `requests` + `BeautifulSoup` with a 2-second delay and jitter between requests, a descriptive `User-Agent` header, and a `robots.txt` check before each request. Film pages at `/film/<slug>/` are permitted under Letterboxd's crawl policy.

### **Slug resolution for ambiguous titles**

Letterboxd URLs use a slugified version of the title (e.g. `/film/the-dark-knight/`), but remakes and sequels may append a year (e.g. `/film/dune-2021/`). A naive slug from the TMDB title alone returns a 404 for these cases. **Solution:** `scrape_movie_page()` tries the plain slug first, then the year-suffixed variant, and logs which slug succeeded.

### **Rating scale mismatch**

TMDB ratings are 0-10 while Letterboxd uses 0-5 stars, making direct comparisons misleading without normalization. **Solution:** `analyze_ratings()` multiplies Letterboxd ratings by 2 before computing the Pearson correlation, and all charts that show both scales side-by-side use dual y-axes to preserve native ranges.

### **Budget and revenue stored as 0 for unknown values**

TMDB encodes unknown financial figures as `0` rather than `null`, which would corrupt any financial analysis if left in place. **Solution:** `clean_data()` explicitly replaces `0` in `budget` and `revenue` with `pd.NA` and logs the count of replacements.

### **NaN serialization in JSON output**

Python's `json.dump` raises a `ValueError` on `float('nan')` by default, and pandas `NA` is not JSON-serializable. **Solution:** `save_processed_data()` iterates every cell before serializing, converting all `pd.NA`, `float('nan')`, and pandas NA sentinel types to `None`, which serializes cleanly as JSON `null`.

---

## 8. Limitations and Future Improvements

### Current Limitations

- **No Letterboxd API** — Scraping is inherently fragile — any HTML restructuring on Letterboxd's side could silently break rating or fan-count extraction. A first-party API would be far more reliable.

- **TMDB popularity bias** — Movies are collected via TMDB's popularity-sorted endpoint, which over-represents English-language mainstream releases and under-represents foreign, documentary, and art-house cinema.

- **Letterboxd scrape coverage** — Some titles fail to match because the Letterboxd slug differs from the TMDB title (foreign-language titles, special characters). These movies end up with null Letterboxd columns rather than being dropped.

- **Static snapshot** — Ratings and fan counts change over time as users log more watches. This dataset reflects a single point-in-time collection and does not capture rating drift.

- **No user-level data** — Only aggregate ratings and fan counts are available; individual review text or demographic breakdowns would enable richer NLP and audience segmentation analyses.

### Future Improvements

- Scrape **Letterboxd review text** in addition to ratings to enable sentiment analysis alongside numeric scores.

- Add a **Rotten Tomatoes Tomatometer** field (via RapidAPI) to enable a three-way critic/audience/aggregator comparison.

- Schedule **weekly re-collection** to build a longitudinal rating time-series and detect films whose reputation shifts post-release.

- Improve slug resolution with a **Letterboxd search fallback** (`/search/<title>/`) for titles that return 404 on both slug candidates.

- Integrate **streaming availability** data (e.g. JustWatch API) to analyze whether platform exclusivity correlates with ratings or fan count.

- Apply **regression modeling** (budget, runtime, genre, release month) to predict box-office revenue and identify the strongest predictors.

---

*Data sources: TMDB API (`api_collector.py`) · Letterboxd scraping (`web_scraper.py`) · Processed by `data_processor.py` · Analyzed by `analyze_data.py` · UCLA STAT 418*

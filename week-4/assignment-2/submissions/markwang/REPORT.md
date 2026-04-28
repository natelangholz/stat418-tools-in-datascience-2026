# Movie Data Collection & Analysis Report

**Date:** April 28, 2026  
**Dataset:** 50 movies — TMDB API + Letterboxd web scraping

---

## 1. Overview

This report presents findings from a two-source data pipeline that collected movie metadata from the **TMDB API** and community ratings from **Letterboxd** via web scraping. The merged dataset covers 50 films spanning release years 2000–2026, with 22 features per record including ratings, genres, cast/crew, budget, revenue, and Letterboxd fan counts.

**Pipeline stages:**

| Stage | Script | Output |
|---|---|---|
| API Collection | `api_collector.py` | 50 movie records from TMDB |
| Web Scraping | `web_scraper.py` | Letterboxd ratings & fan counts |
| Data Processing | `data_processor.py` | Merged CSV + JSON (22 columns) |
| Analysis | `analyze_data.py` | 3 visualizations + summary stats |

---

## 2. Dataset Snapshot

| Metric | Value |
|---|---|
| Total movies | 50 |
| Year range | 2000 – 2026 |
| Avg TMDB rating | 6.44 / 10 |
| Avg Letterboxd rating (scaled) | 5.92 / 10 |
| TMDB–Letterboxd correlation | **0.83** |
| Avg production budget | $80.4M |
| Avg box-office revenue | $437.3M |
| Primary language | English (42 of 50) |

---

## 3. Findings

### 3.1 Rating Distributions & Platform Correlation

TMDB and Letterboxd ratings are strongly correlated (r = 0.83), suggesting that crowd-sourced and community cinephile audiences broadly agree on film quality. However, Letterboxd ratings tend to skew slightly lower on average (5.92 vs. 6.44), consistent with Letterboxd's more engaged and often more critical user base. The KDE plots below show that TMDB ratings cluster tightly around the 7–8 range, while Letterboxd ratings are more spread out, capturing a wider range of audience sentiment.

**Visualization 1 — Rating Distributions**

![Rating Distribution](data/reports/visuals/rating_distribution.png)

> **Key takeaway:** Both platforms agree directionally, but Letterboxd tends to rate films ~0.5 points lower than TMDB on a 0–10 scale.

---

### 3.2 Genre Analysis

Adventure, Action, and Thriller are the three most frequently occurring genres in the dataset, reflecting the commercially dominant film landscape of recent years. Comedy and Horror each appear in 13 films, pointing to their sustained popularity. Science Fiction rounds out the top group at 10 appearances, driven largely by recent tentpole releases.

**Visualization 2 — Genre Counts**

![Genre Counts](data/reports/visuals/genre_counts.png)

> **Key takeaway:** Action-Adventure is the dominant genre cluster in the dataset. Horror's strong presence (tied with Comedy) signals a commercially active horror cycle in 2024–2026.

---

### 3.3 Temporal Trends in Ratings

The dataset is heavily weighted toward recent films: 28 of 50 movies were released in 2026 and 10 in 2025, with only a handful of older "anchor" titles included (e.g., *Interstellar* (2014), *The Lord of the Rings* trilogy entries (2001, 2003)). As a result, the average TMDB rating for older films appears higher — these are established classics selected for their high fan engagement on Letterboxd, not as a representative sample of their era.

**Visualization 3 — Average TMDB Rating by Year**

![Temporal Trends](data/reports/visuals/temporal_trends.png)

> **Key takeaway:** Older films in the dataset rate higher because they were sampled by popularity/reputation rather than randomly. Among 2025–2026 releases, average ratings fall in the 6.5–7.5 range as expected for in-progress audience evaluation.

---

## 4. Notable Findings

**Highest box-office gross:** *Spider-Man: No Way Home* — $1.92B  
**Most Letterboxd fans:** *Interstellar* — 512,000 fans  
**Highest TMDB-rated film:** *The Lord of the Rings: The Return of the King* — 8.50  
**Highest Letterboxd-rated film (scaled):** *The Lord of the Rings: The Return of the King* — 9.1 / 10  
**Most common genre:** Adventure (17 of 50 films)  
**Most productive year in dataset:** 2026 (28 films, reflecting the recency bias of TMDB's "popular now" endpoint)

---

## 5. Data Quality Notes

- **Budget/revenue:** TMDB reports 0 for undisclosed financials; these were treated as missing values rather than true zeros.
- **Letterboxd ratings:** Originally on a 0.5–5.0 star scale; multiplied by 2 for 0–10 comparison with TMDB.
- **Letterboxd fan counts:** Not available for all films; some newer releases had null values.
- **Scraping compliance:** The Letterboxd scraper checks `robots.txt` and enforces a 2-second delay between requests per `robots.txt` guidance.
- **Rate limiting:** TMDB API requests were capped at 40 per 10-second window as required by the API terms.

---

## 6. Methods

Data was collected on **April 28, 2026** using:

- **TMDB API** (`/movie/popular`, `/movie/{id}`, `/movie/{id}/credits`) — returning movie details, cast, crew, budget, revenue, and vote data.
- **Letterboxd web scraping** — parsing HTML with BeautifulSoup to extract aggregate star ratings and fan counts from each film's Letterboxd page.

Both sources were joined on a normalized slug derived from the movie title and release year. Genres, cast, and crew were stored as comma-separated strings in the CSV and as native lists in JSON.

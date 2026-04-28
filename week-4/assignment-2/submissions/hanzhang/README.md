# Assignment 2: Movie Data Collection & Analysis Pipeline

**Course:** STAT 418 — Tools in Data Science (UCLA, Spring 2026)
**Author:** Hanzhang Yuan (hyuan21@ucla.edu)

## Overview

This project builds an end-to-end data pipeline that collects information about movies from two complementary sources, merges and cleans the data, and analyzes trends in the entertainment industry.

The pipeline:

1. Pulls structured movie metadata (title, release date, runtime, genres, budget, revenue, TMDB rating, vote count, top-5 cast/crew, production companies, original language) from the **TMDB API**.
2. Scrapes audience-level signals (Letterboxd average rating out of 5 and number of fans) from **Letterboxd** movie pages.
3. Merges and cleans the two sources into a unified dataset of 50+ movies.
4. Produces summary statistics, three figures, and a written report in `REPORT.md`.

The goals are to (a) practice combining API integration with web scraping under real-world rate-limiting and ethical constraints, (b) reason about data quality when joining heterogeneous sources, and (c) communicate findings in a reproducible, well-documented way.

## Project Structure

```
.
├── README.md                  # This file
├── REPORT.md                  # Findings, figures, and discussion
├── requirements.txt           # Python dependencies
├── .env.example               # Template for API keys (no secrets)
├── .gitignore                 # Excludes .env, caches, etc.
├── api_collector.py           # TMDB API client + collection driver
├── web_scraper.py             # Letterboxd scraper
├── data_processor.py          # Merging, cleaning, and validation
├── analyze_data.py            # Statistics and visualizations
├── run_pipeline.py            # End-to-end orchestrator
├── data/
│   ├── raw/
│   │   ├── tmdb/              # Raw JSON responses from TMDB
│   │   └── letterboxd/        # Parsed Letterboxd records (JSON)
│   ├── processed/             # Cleaned CSV + JSON
│   └── analysis/              # Figures (PNG) and analysis_summary.txt
└── logs/
    └── pipeline.log           # Combined run log
```

## Setup Instructions

### 1. Switch to your branch and enter the directory

```bash
git checkout -b hw2-hanzhang
cd week-4/assignment-2/submissions/hanzhang
```

### 2. Create a Python environment

A clean Python 3.10+ environment is recommended. Using `uv`:

```bash
uv venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows PowerShell
uv pip install -r requirements.txt
```

Or with the standard library tooling:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Get a TMDB API key

1. Create a free account at https://www.themoviedb.org/.
2. Go to **Settings → API** and request an API key (the "Developer" option is free).
3. Copy the v3 API key.

### 4. Configure your `.env`

Copy the template and fill in your key. Never commit the real `.env`.

```bash
cp .env.example .env
# then edit .env so it contains:
# TMDB_API_KEY=your_actual_key_here
```

The repository includes only `.env.example`:

```
TMDB_API_KEY=your_tmdb_api_key_here
```

`.env` is listed in `.gitignore` and must never be checked in.

## How to Run the Pipeline

The simplest entry point is `run_pipeline.py`, which executes all four stages in order:

```bash
python run_pipeline.py
```

What it does, step by step:

1. **Collect** — `api_collector.py` calls TMDB's `/movie/popular` endpoint, paginates until 60 unique movies have been gathered (a small over-collection cushion above the 50-item floor), and then fetches `/movie/{id}` and `/movie/{id}/credits` for each. Raw responses are stored under `data/raw/tmdb/tmdb_movies_raw.json`.
2. **Scrape** — `web_scraper.py` first checks `https://letterboxd.com/robots.txt`, then for each movie slug visits `https://letterboxd.com/film/{slug}/` with a polite delay of at least 2 seconds between requests. Parsed records are written to `data/raw/letterboxd/letterboxd_movies_raw.json`.
3. **Process** — `data_processor.py` joins the two sources on `(title, release_year)`, normalizes types, treats budget/revenue ≤ 1000 as missing, deduplicates on `tmdb_id`, and writes `data/processed/movies_processed.csv` and `data/processed/movies_processed.json`.
4. **Analyze** — `analyze_data.py` produces three figures (`rating_comparison.png`, `genre_counts.png`, `top_profit_movies.png`) and `analysis_summary.txt` in `data/analysis/`.

You can also run a single stage on its own, which is useful while developing:

```bash
python api_collector.py
python web_scraper.py
python data_processor.py
python analyze_data.py
```

All scripts log to `logs/pipeline.log`.

## Dependencies

Listed in `requirements.txt`:

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pandas>=2.0.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

Install with `uv pip install -r requirements.txt` (or `pip install -r requirements.txt`).

## Data Sources and Collection Methods

| Source | Type | Endpoint / URL pattern | Fields used |
|---|---|---|---|
| TMDB | REST API (JSON) | `https://api.themoviedb.org/3/movie/popular`, `/movie/{id}`, `/movie/{id}/credits` | title, release_date, runtime, genres, budget, revenue, vote_average, vote_count, cast (top 5), crew (top 5), production_companies, original_language |
| Letterboxd | HTML scraping | `https://letterboxd.com/film/{slug}/` | average rating (out of 5), number of fans |

**Title-to-slug conversion** mirrors Letterboxd's URL convention: lowercase, ampersands replaced with `and`, non-alphanumeric characters replaced with hyphens, repeated hyphens collapsed, and leading/trailing hyphens stripped.

**Rate limiting.** TMDB allows 40 requests per 10 seconds; the collector enforces a conservative ~4 requests/second cap with a 0.25 s sleep after every call. The Letterboxd scraper sleeps for at least 2 seconds before each request and uses the User-Agent string `UCLA STAT418 Student - hyuan21@ucla.edu`.

**Error handling.** The TMDB client retries on HTTP 429 and 5xx responses with exponential backoff (up to 3 attempts). Both clients use timeouts and try/except blocks that log failures and continue. Movies that fail to scrape are recorded with `scrape_success=False` rather than dropped silently.

## Ethical Considerations

- **`robots.txt` compliance.** The scraper fetches and parses `https://letterboxd.com/robots.txt` via `urllib.robotparser` before any film page is requested, and warns/aborts if the relevant path is disallowed.
- **Rate limiting.** A minimum 2-second delay between Letterboxd requests is enforced. TMDB's documented 40 req / 10 s limit is respected with a wide margin.
- **Identifiable User-Agent.** Scraping requests use `User-Agent: UCLA STAT418 Student - hyuan21@ucla.edu` so site administrators can contact me if the traffic causes issues.
- **No personal data.** Only public, aggregated data about movies is collected: titles, ratings, fan counts, and production metadata. No user accounts, reviews, lists, or comments are scraped.
- **Educational use only.** The dataset is used solely to complete this assignment and is not redistributed or used for any commercial purpose.
- **Secrets hygiene.** The TMDB API key lives in `.env` and is excluded from version control via `.gitignore`. Only `.env.example` (no real key) is committed.

## Known Limitations

- **TMDB popular feed has occasional repeats.** When paginating, the same `tmdb_id` can appear on multiple pages. The collector deduplicates by `tmdb_id` during collection, and `data_processor.py` deduplicates again as a safety net. To stay above the 50-item floor the collector targets 60 unique items.
- **Letterboxd slug ambiguity.** Movies sharing a title may collide on the bare slug. When the scraped page does not match (e.g., wrong year), the rating/fans fields are left as `None` and the row is flagged via `scrape_success` and `error`.
- **TMDB financials.** `budget` and `revenue` are sparse and frequently set to `0` for non-US or older releases. The processor treats `budget <= 1000` and `revenue <= 1000` as missing, and financial analyses are restricted to the subset where both fields are positive.
- **Scale of dataset.** ~50 movies is enough for descriptive trends but not for strong statistical claims. Correlation coefficients in `REPORT.md` should be read as suggestive rather than conclusive.
- **Snapshot bias.** Both TMDB's "popular" endpoint and Letterboxd ratings reflect activity at collection time. Results are time-stamped and not strictly reproducible from a fresh run.
- **Scraper fragility.** The scraper relies on Letterboxd's current HTML (the `meta[name="twitter:data2"]` rating tag and a "X fans" text pattern). Template changes on Letterboxd will require updating the selectors in `web_scraper.py`.

## Reproducibility Notes

- A complete run from an empty `data/` directory takes roughly 4–6 minutes for 60 items, dominated by the 2-second-per-request scraping delay.
- The merged CSV (`data/processed/movies_processed.csv`) is the canonical artifact for the analysis stage; figures and `analysis_summary.txt` regenerate from it.

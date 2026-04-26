# Assignment 2: Movie Data Collection & Analysis Pipeline

UCLA STAT418 — Yutong Ma (ytm02)

## Overview

A data pipeline that collects movie data from two sources — TMDB API and Letterboxd (web scraping) — then merges and analyzes the data to uncover trends in the entertainment industry.

## Data Sources

- **TMDB API**: Title, release date, runtime, genres, budget, revenue, TMDB rating, cast, directors
- **Letterboxd**: Average rating (0–5 stars), fan count (scraped)

## Setup

### 1. Install dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Set up API key

```bash
cp .env.example .env
# Edit .env and add your TMDB API key
```

Get a free TMDB API key at https://www.themoviedb.org/settings/api

### 3. Run the pipeline

```bash
python run_pipeline.py
```

Or run each step individually:

```bash
python api_collector.py     # Step 1: collect TMDB data
python web_scraper.py       # Step 2: scrape Letterboxd
python data_processor.py    # Step 3: merge and clean
python analyze_data.py      # Step 4: analyze and visualize
```

## Directory Structure

```
submissions/ytm02/
├── api_collector.py
├── web_scraper.py
├── data_processor.py
├── analyze_data.py
├── run_pipeline.py
├── requirements.txt
├── .env.example
├── README.md
├── REPORT.md
├── data/
│   ├── raw/
│   │   ├── tmdb/movies.json
│   │   └── letterboxd/ratings.json
│   ├── processed/movies_processed.csv
│   └── analysis/
│       ├── rating_correlation.png
│       ├── genre_distribution.png
│       ├── genre_avg_rating.png
│       ├── budget_vs_revenue.png
│       └── summary.json
└── logs/
```

## Ethical Considerations

- Checked Letterboxd's robots.txt before scraping
- 2-second delay between all scraping requests
- Used descriptive User-Agent: `UCLA STAT418 Student - ytm02@g.ucla.edu`
- Respected TMDB rate limits (max 40 requests/10 seconds)
- Data used for academic purposes only

## Known Limitations

- Letterboxd matching relies on title slugs; titles with special characters may fail
- 11/50 movies had no Letterboxd page (mostly unreleased 2026 films)
- Budget/revenue data missing for ~34% of movies (TMDB returns 0 when unknown)

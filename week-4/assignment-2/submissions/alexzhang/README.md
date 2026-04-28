# Movie Data Pipeline — STAT418 Assignment 2

Collects movie data from the TMDB API and Letterboxd, merges them, and produces analysis charts.

---

## Project Structure

```
.
├── api_collector.py          # Fetches ~100 popular movies from TMDB API
├── web_scraper.py            # Scrapes ratings and fan counts from Letterboxd
├── data_processor.py         # Merges and cleans TMDB + Letterboxd data
├── analyze_data.py           # Generates analysis charts and a summary report
├── requirements.txt
├── .env.example              # Copy to .env and add your TMDB API key
└── data/
    ├── raw/
    │   ├── tmdb/             # tmdb_movies_data.json - from running api_collector.py
    │   └── letterboxd/       # letterboxd_movies_data.json - from running web_scraper.py
    ├── processed/            # movies.csv, movies.json - from running data_processor.py
    └── analysis/             # PNG charts + report.txt - from running analyze_data.py
```

---

## Requirements

- Python 3.10+
- TMDB API key (free at [themoviedb.org](https://www.themoviedb.org/settings/api))

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set TMDB_API_KEY=your_key_here
```

---

## How to Run

Run each script in order from the `submissions/alexzhang/` directory:

```bash
# 1. Collect ~100 popular movies from TMDB
python api_collector.py

# 2. Scrape Letterboxd ratings for those movies (~3-4 min with rate limiting)
python web_scraper.py

# 3. Merge and clean the two datasets
python data_processor.py

# 4. Generate charts and summary report
python analyze_data.py
```

---

## Pipeline Overview

### Step 1 — TMDB API (`api_collector.py`)
- Fetches 5 pages of popular movies (20 per page = 100 movies)
- Retrieves full details and credits for each movie
- Saves to `data/raw/tmdb/tmdb_movies_data.json`

### Step 2 — Letterboxd Scraper (`web_scraper.py`)
- Reads movie titles from the TMDB output
- Scrapes each film's average rating and fan count from Letterboxd
- Respects `robots.txt` and applies a 2-second delay between requests
- Saves to `data/raw/letterboxd/letterboxd_movies_data.json`

### Step 3 — Data Processing (`data_processor.py`)
- Flattens nested TMDB fields (genres, production companies, etc.)
- Left-joins TMDB records to Letterboxd records on title + year
- Cleans and coerces numeric fields, drops duplicates
- Saves to `data/processed/movies.csv` and `data/processed/movies.json`

### Step 4 — Analysis (`analyze_data.py`)
Produces four charts in `data/analysis/`:

| Chart | Description |
|---|---|
| `rating_correlation.png` | TMDB vs Letterboxd rating scatter + regression |
| `genre_analysis.png` | Top genres by count and by mean rating |
| `financial_analysis.png` | Budget vs revenue with top-5 ROI films annotated |
| `temporal_analysis.png` | Mean TMDB rating by release year |

A text summary is saved to `data/analysis/report.txt`.

---

## Author

Alex Zhang

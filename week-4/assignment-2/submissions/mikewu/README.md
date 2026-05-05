# Homework 2 — Movie data collection and analysis (Mike Wu)

## Overview

This folder implements a small end-to-end pipeline: collect movie metadata from **The Movie Database (TMDB)** via its HTTP API, enrich with **IMDb** title-page fields via polite HTTP scraping, merge and clean the result in **pandas**, then run analysis and plots. The same layout matches the course assignment: `api_collector.py`, `web_scraper.py`, `data_processor.py`, `analyze_data.py`, and `run_pipeline.py`.

## Environment

- Python 3.10+ recommended.
- Create a virtual environment, then install dependencies (from this directory):

```bash
cd week-4/assignment-2/submissions/mikewu
uv venv
source .venv/bin/activate   
uv pip install -r requirements.txt
```

## API key and email

1. Request a free TMDB key: [TMDb API](https://www.themoviedb.org/settings/api).
2. Fill in `TMDB_API_KEY` and `SCRAPER_EMAIL` directly in `.env.example`.

## How to run

### A. Full run (TMDB + live IMDb scrapes)

Requires a valid `TMDB_API_KEY`. From this directory:

```bash
python run_pipeline.py --num 50
```

- Collects 50 popular movies (details, credits, external ids) with **40 requests / 10 s** throttling and retries in `api_collector.py`.
- Fetches IMDb title pages for each `imdb_id` with at least **2 seconds** between requests in `scrape_multiple_movies`.
- Writes `data/raw/tmdb/movie_*.json`, `data/raw/imdb/tt*.json`, `data/processed/movies_merged.{csv,json}`, figures under `data/analysis/`, and `logs/pipeline.log`.

**Note:** IMDb may return WAF or bot interstitials in some networks; the scraper logs the HTTP status and still merges whatever TMDB provides.

## Part-by-part scripts

| Script | Role |
|--------|------|
| `api_collector.py` | TMDB session, `get_popular_movies` / `get_movie_details` / `get_movie_credits`, `collect_all_data`, raw JSON under `data/raw/tmdb/`. |
| `web_scraper.py` | `check_robots_txt`, `scrape_movie_page`, `scrape_multiple_movies`, raw JSON under `data/raw/imdb/`. |
| `data_processor.py` | `load_raw_data`, `merge_data` (on `imdb_id`), `clean_data`, `save_processed_data`. |
| `analyze_data.py` | Correlation, genres, financials, temporal; saves PNGs and `data/analysis/analysis_summary.json`. |

## Data and logs

- **Raw:** `data/raw/tmdb/`, `data/raw/imdb/` (keep each file under ~10MB as per course rules).
- **Processed:** `data/processed/movies_merged.csv` (required sample with 50+ rows) and `movies_merged.json`.
- **Analysis:** `data/analysis/*.png`, `analysis_summary.json`.
- **Log:** `logs/pipeline.log` (also mirrored to the console for `run_pipeline`).

## Ethical and legal practice

- **robots.txt** is read with the course user-agent; scraping stays on public title pages, no private user data.
- **Rate limits** respect TMDB (40/10s) and IMDb (≥2s between page GETs in batch mode).
- **Use of data** is for STAT418 only; not for resale or public redistribution of bulk scraped archives.
- **User-Agent** is descriptive and includes the student email from `.env.example`.

## Known limitations

- Cast/crew are capped at **five** each, prioritizing director/writer/producer when possible.
- IMDb HTML and anti-bot pages change; selectors try JSON-LD, `__NEXT_DATA__`, and a few fallbacks, with nulls on failure.
- Run with a real TMDB key for API-faithful data collection.

## Dependencies

See `requirements.txt` (aligned with the assignment: `requests`, `beautifulsoup4`, `lxml`, `pandas`, `python-dotenv`, `matplotlib`, `seaborn`).

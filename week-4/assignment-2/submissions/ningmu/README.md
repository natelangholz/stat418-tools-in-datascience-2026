# Homework 2 — Movie Data Collection & Analysis Pipeline

**Author:** Christine Ning (ningmu141@gmail.com)
**Course:** UCLA STAT 418 — Tools in Data Science (Spring 2026)

## Overview

This pipeline collects metadata for the 50 most popular movies from
[TMDB](https://www.themoviedb.org/) via its REST API, scrapes the
matching public film pages from [Letterboxd](https://letterboxd.com/),
merges the two sources into a tidy table, and produces a short
analysis with visualizations.

The four stages are decoupled and can be run individually:

| Stage | Script | Output |
|-------|--------|--------|
| 1 | `api_collector.py` | `data/raw/tmdb/*.json` |
| 2 | `web_scraper.py`   | `data/raw/letterboxd/*.json` |
| 3 | `data_processor.py`| `data/processed/movies.{csv,json}` |
| 4 | `analyze_data.py`  | `data/analysis/fig_*.png` + `summary.{json,md}` |

The convenience driver `run_pipeline.py` runs all four in order.

## Setup

### 1. Get a TMDB API key

1. Make a free account at <https://www.themoviedb.org/>.
2. Settings -> API -> request a v3 key.

### 2. Install dependencies

```bash
# Create / activate a virtual environment (uv shown; venv works too)
uv venv
source .venv/bin/activate            # macOS / Linux
# .venv\Scripts\activate             # Windows

uv pip install -r requirements.txt
```

### 3. Configure secrets

```bash
cp .env.example .env
# then edit .env and paste your key
```

`.env` is git-ignored. Never commit it.

## Running

```bash
# Full pipeline (~3-5 min, dominated by the 2 s/page scraping delay)
python run_pipeline.py 50

# Or run each step on its own
python api_collector.py 50
python web_scraper.py
python data_processor.py
python analyze_data.py
```

The processed CSV that satisfies the "sample data" requirement lives at
`data/processed/movies.csv`. Generated figures and the summary live in
`data/analysis/`. Logs go to `logs/pipeline.log`.

## Data sources & methods

* **TMDB** — official v3 REST API
  (`/movie/popular`, `/movie/{id}`, `/movie/{id}/credits`).
  Authenticated with an API key in `.env`. We honor TMDB's
  40-requests-per-10-seconds rate limit by self-throttling to
  ~3 requests per second.
* **Letterboxd** — public film pages
  (`https://letterboxd.com/film/<slug>/`). We check `robots.txt`
  before any request, sleep at least 2 s between requests, and use a
  descriptive UCLA STAT 418 User-Agent. We pull only the average rating
  (from the `twitter:data2` meta tag) and the public fan count.
  No personal user data is touched.

## Ethical considerations

* `robots.txt` is parsed and respected before scraping starts.
* Rate limiting (>=2 s between requests) keeps load on Letterboxd
  negligible.
* User-Agent identifies the project and a contact email so site
  administrators can reach me if needed.
* TMDB's terms permit free non-commercial use of the API; this
  homework is non-commercial and the data is not redistributed.
* No personal user accounts, watchlists, or comments are scraped.

## Known limitations

* The Letterboxd slug is generated heuristically from the TMDB title.
  Slugs that are hand-curated (e.g. disambiguated by year) will 404,
  so a small fraction of films may be missing Letterboxd ratings. Those
  rows survive the merge but with `letterboxd_rating = NaN`.
* Older films often have `budget = 0` or `revenue = 0` on TMDB; we
  treat zeros as missing and drop them from the financial analysis.
* The "popular" endpoint skews toward recent, English-language,
  big-budget releases, so the genre and year distributions are not a
  representative sample of all cinema.
* Pearson correlations are reported on the small (~50-movie) sample
  and should not be over-interpreted.

## Repository layout

```
submissions/ningmu/
├── README.md
├── REPORT.md
├── requirements.txt
├── .env.example
├── api_collector.py
├── web_scraper.py
├── data_processor.py
├── analyze_data.py
├── run_pipeline.py
├── data/
│   ├── raw/{tmdb,letterboxd}/         # per-movie JSON
│   ├── processed/movies.{csv,json}    # merged tidy data
│   └── analysis/                      # figures + summary.{json,md}
└── logs/pipeline.log
```

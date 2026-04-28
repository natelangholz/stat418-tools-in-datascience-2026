# STAT 418 Assignment 2 — TMDB & Letterboxd Movie Data Pipeline

A four-script Python data pipeline that collects movie data from the TMDB REST API, scrapes supplemental ratings from Letterboxd, merges and cleans both datasets, and produces four statistical visualizations and a summary report.

**Course:** UCLA STAT 418 — Tools in Data Science  
**Student:** Rohan Narasayya (rnarasay@ucla.edu)

---

## Assignment Overview

The pipeline demonstrates end-to-end data engineering skills across four sequential stages:

1. **API Collection** (`api_collector.py`) — Authenticates with the TMDB API and fetches 100 popular movies, making three API calls per movie (details, credits, external IDs) for a total of ~305 API calls.
2. **Web Scraping** (`web_scraper.py`) — Scrapes each movie's Letterboxd page for its weighted average rating (0–5 scale) using a plain `requests.Session` — no browser automation required.
3. **Data Processing** (`data_processor.py`) — Merges both sources on normalized title + release year, cleans the data, and exports to CSV and JSON.
4. **Analysis** (`analyze_data.py`) — Produces four annotated visualizations and a summary report.

A fifth script (`run_pipeline.py`) orchestrates all four steps with logging and error handling.

---

## Repository Structure

```
submissions/rohannarasayya/
├── api_collector.py        # TMDB API collection
├── web_scraper.py          # Letterboxd scraping (requests + BeautifulSoup)
├── data_processor.py       # Merge, clean, export
├── analyze_data.py         # Visualizations and report
├── run_pipeline.py         # Full pipeline orchestrator
├── requirements.txt        # Python dependencies
├── .env.example            # API key template
├── data/
│   ├── raw/
│   │   ├── tmdb/           # Per-movie JSON + all_movies.json
│   │   └── letterboxd/     # Per-movie JSON + all_letterboxd.json
│   ├── processed/
│   │   ├── movies.csv      # Merged, cleaned dataset (100 rows, 19 columns)
│   │   └── movies.json
│   └── analysis/
│       ├── rating_correlation.png
│       ├── rating_by_genre.png
│       ├── rating_by_genre_comparison.png
│       ├── budget_vs_revenue.png
│       └── summary_report.txt
└── logs/                   # Per-script log files
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or later
- [`uv`](https://github.com/astral-sh/uv) package manager

### 1. Create and activate a virtual environment

```bash
uv venv
# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 3. Configure your API key

Copy the example environment file and fill in your TMDB API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
TMDB_API_KEY=your_tmdb_api_key_here
```

A free TMDB API key can be obtained at https://www.themoviedb.org/settings/api (account required).

---

## Running the Pipeline

### Full pipeline (recommended)

```bash
python run_pipeline.py
```

Runs all four scripts in order, prints progress to stdout, and logs timing to `logs/pipeline.log`. Exits with a non-zero code if any step fails.

### Individual scripts

Run each script standalone in order. Each script can also be run in isolation to re-run a single stage without repeating earlier steps.

| Step | Command | Primary output |
|---|---|---|
| 1. Collect | `python api_collector.py` | `data/raw/tmdb/all_movies.json` |
| 2. Scrape | `python web_scraper.py` | `data/raw/letterboxd/all_letterboxd.json` |
| 3. Process | `python data_processor.py` | `data/processed/movies.csv` |
| 4. Analyze | `python analyze_data.py` | `data/analysis/*.png`, `summary_report.txt` |

**Expected runtime:** ~8–10 minutes total (dominated by the 2-second Letterboxd crawl delay across 100 pages).

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `requests` | >=2.31.0 | TMDB API calls and Letterboxd HTTP requests |
| `beautifulsoup4` | >=4.12.0 | Letterboxd HTML parsing |
| `lxml` | >=4.9.0 | Fast HTML parser backend for BeautifulSoup |
| `pandas` | >=2.0.0 | Data merging, cleaning, and export |
| `python-dotenv` | >=1.0.0 | Loading `TMDB_API_KEY` from `.env` |
| `matplotlib` | >=3.7.0 | Plot generation (headless Agg backend) |
| `seaborn` | >=0.12.0 | Genre bar chart styling |
| `scipy` | >=1.10.0 | Pearson correlation coefficients |
| `adjustText` | >=0.8.0 | Automatic label placement on scatter plots |

---

## Data Sources and Collection Methods

### TMDB API

The [TMDB (The Movie Database) API](https://developer.themoviedb.org/docs) is a free, documented REST API. The pipeline queries the `/movie/popular` endpoint across 5 pages to discover 100 movies, then makes three additional calls per movie:

- `GET /movie/{id}` — title, release date, runtime, genres, budget, revenue, vote average/count, language, production companies
- `GET /movie/{id}/credits` — top-5 cast (name, character) and crew filtered to Directors and Producers
- `GET /movie/{id}/external_ids` — retrieves the `imdb_id` field stored alongside TMDB data

**Rate limiting:** The collector enforces a minimum 0.25-second interval between requests (max 40 requests per 10 seconds) and retries failed requests up to 3 times with exponential backoff (1s, 2s, 4s).

### Letterboxd Scraping

Letterboxd does not offer a public API, so movie pages are scraped from `https://letterboxd.com/film/{slug}/` using a plain `requests.Session`. Two fields are extracted per page:

- **Letterboxd rating** — from the `<meta name="twitter:data2">` tag, whose `content` attribute reads e.g. `"3.82 out of 5"`. This meta tag is rendered server-side for social sharing and is stable across site deploys.
- **Fan count** — from an `<a>` tag whose `href` contains `/fans/` (returned `None` for all movies in the current dataset, indicating Letterboxd may render this count client-side via JavaScript).

**Slug derivation:** Letterboxd film URLs use a slug derived from the title — lowercase, non-alphanumeric characters replaced with hyphens, consecutive hyphens collapsed, leading/trailing hyphens stripped. Example: `"Spider-Man: No Way Home"` → `"spider-man-no-way-home"`.

**robots.txt:** The scraper fetches `robots.txt` using the project User-Agent (Letterboxd returns HTTP 403 to Python's default `urllib` user-agent, which would cause `RobotFileParser` to conservatively report disallow-all). The `/film/` path is not disallowed for the wildcard `*` ruleset.

---

## Ethical Considerations

| Concern | How it is addressed |
|---|---|
| robots.txt compliance | `check_robots_txt()` is called before any scraping; the pipeline aborts if `/film/` paths are disallowed |
| Crawl rate | A mandatory 2-second sleep between every Letterboxd request prevents server overload |
| Identification | All requests use the User-Agent `"UCLA STAT418 Student - rnarasay@ucla.edu"` so the requester is identifiable |
| Personal data | Only aggregate statistics (rating) are collected — no review text, usernames, or user profiles |
| API terms of service | TMDB data is used in accordance with their [API Terms of Use](https://www.themoviedb.org/documentation/api/terms-of-use) |
| Scope | Letterboxd scraping is conducted solely for non-commercial educational purposes as part of a university assignment |

---

## Known Limitations

- **Letterboxd slug mismatches:** 5 movies returned HTTP 404, and a further 20 returned HTTP 200 pages that contained no `twitter:data2` meta tag (typically very new or obscure titles not yet in Letterboxd's database). These 25 movies have `lb_rating = NaN` in the processed dataset.
- **Movies with zero vote average:** 2 movies had `vote_average = 0` in TMDB (no community votes recorded yet). These are excluded from the rating correlation plot to avoid distorting the x-axis, but remain in the dataset for genre and financial analysis.
- **Missing financial data:** TMDB reports `0` for unknown budget and revenue, which the pipeline treats as missing. Only 55 of 100 movies have usable budget and revenue figures, and these skew toward major studio theatrical releases.
- **Popularity sampling bias:** The dataset reflects movies trending on TMDB at collection time. It is not a random or genre-stratified sample.
- **Budget values are nominal:** No inflation adjustment is applied, so a 1972 film's budget is compared directly to a 2026 film's budget.
- **Fan count unavailable:** The Letterboxd fan count is rendered client-side via JavaScript and was `None` for all 100 movies in this dataset. Only `lb_rating` (from a server-side meta tag) was reliably extracted.

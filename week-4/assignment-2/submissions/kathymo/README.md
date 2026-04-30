# Movie Data Pipeline
### UCLA STAT 418 — Data Collection & Analysis Assignment

An end-to-end data pipeline that collects movie data from the TMDB API and Letterboxd (via web scraping), merges and cleans the dataset, and produces statistical analyses with visualizations and a written report.

---

## Table of Contents

1. [Assignment Overview & Goals](#1-assignment-overview--goals)
2. [Project Structure](#2-project-structure)
3. [Dependencies & Requirements](#3-dependencies--requirements)
4. [Setup Instructions](#4-setup-instructions)
5. [How to Run the Pipeline](#5-how-to-run-the-pipeline)
6. [Data Sources & Collection Methods](#6-data-sources--collection-methods)
7. [Ethical Considerations](#7-ethical-considerations)
8. [Known Limitations](#8-known-limitations)

---

## 1. Assignment Overview & Goals

This project demonstrates a full data science pipeline applied to the movie industry:

- **Collect** structured movie data from the TMDB API and scrape ratings/fan counts from Letterboxd
- **Merge** the datasets on a shared key (`tmdb_id`) and clean the result
- **Analyze** ratings, genres, financials, and release trends
- **Report** findings in a self-contained Markdown document with embedded visualizations

The pipeline answers four core analytical questions:

| # | Analysis | Questions |
|---|----------|-----------|
| 1 | **Rating Analysis** | How correlated are TMDB and Letterboxd ratings? How are ratings distributed on each platform? |
| 2 | **Genre Analysis** | Which genres are most common? Which genres rate highest on each platform? |
| 3 | **Financial Analysis** | How strongly does budget predict revenue? Which movies were most profitable? |
| 4 | **Temporal Analysis** | How have ratings shifted over time? Which years were most productive? |

---

## 2. Project Structure

```
.
├── api_collector.py       # Step 1 — TMDB API collection
├── web_scraper.py         # Step 2 — Letterboxd web scraping
├── data_processor.py      # Step 3 — merge, clean, validate
├── analyze_data.py        # Step 4 — analysis, plots, REPORT.md
├── run_pipeline.py        # Orchestrator — runs all four steps in order
├── requirements.txt       # Python dependencies
├── .env                   # API keys (never committed — see setup)
│
├── data/
│   ├── raw/
│   │   ├── tmdb/          # Per-movie TMDB JSON + all_movies.json
│   │   └── letterboxd/    # Per-movie Letterboxd JSON + letterboxd_movies.json
│   ├── processed/
│   │   ├── movies.csv     # Final merged & cleaned dataset
│   │   └── movies.json    # Same dataset in JSON format
│   └── analysis/
│       └── plots/         # PNG visualizations (6 files)
│
└── logs/
    ├── api_collector.log
    ├── web_scraper.log
    ├── data_processor.log
    ├── analyze_data.log
    └── run_pipeline.log
```

---

## 3. Dependencies & Requirements

**Python 3.9 or higher** is required.

| Package | Version | Used by |
|---------|---------|---------|
| `requests` | ≥ 2.31.0 | `api_collector.py`, `web_scraper.py` |
| `beautifulsoup4` | ≥ 4.12.0 | `web_scraper.py` |
| `python-dotenv` | ≥ 1.0.0 | `api_collector.py` |
| `pandas` | ≥ 2.0.0 | `data_processor.py`, `analyze_data.py` |
| `numpy` | ≥ 1.24.0 | `data_processor.py`, `analyze_data.py` |
| `matplotlib` | ≥ 3.7.0 | `analyze_data.py` |
| `seaborn` | ≥ 0.12.0 | `analyze_data.py` |
| `scipy` | ≥ 1.10.0 | `analyze_data.py` |
| `lxml` | ≥ 4.9.0 | `web_scraper.py` (BeautifulSoup parser) |

All standard library modules (`json`, `logging`, `os`, `pathlib`, `re`, `subprocess`, `sys`, `time`, `urllib`, etc.) require no installation.

---

## 4. Setup Instructions

### 4.1 Clone or download the project

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 4.2 Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4.3 Install dependencies

```bash
pip install -r requirements.txt
```

### 4.4 Obtain a TMDB API key

This project requires one free API key (Letterboxd is scraped — no key needed):

**TMDB API key**
1. Create a free account at [https://www.themoviedb.org/signup](https://www.themoviedb.org/signup)
2. Go to **Settings → API → Create → Developer**
3. Copy your **API Key (v3)**

### 4.5 Create a `.env` file

Create a file named `.env` in the project root (same folder as `run_pipeline.py`) and add your key:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

> ⚠️ **Never commit `.env` to version control.** Add it to `.gitignore`:
> ```bash
> echo ".env" >> .gitignore
> ```

---

## 5. How to Run the Pipeline

### Run the full pipeline (recommended)

```bash
python run_pipeline.py
```

This runs all four scripts in order and prints a timing summary at the end:

```
══════════════════════════════════════════════════════════
  Movie Data Pipeline  ·  2025-04-27 10:00 UTC
══════════════════════════════════════════════════════════

  Steps queued:
    1. api_collector       — Fetch movie metadata from the TMDB API
    2. web_scraper         — Scrape ratings and fan counts from Letterboxd
    3. data_processor      — Merge, clean, and validate both datasets
    4. analyze_data        — Run analyses, generate plots, and write REPORT.md
```

> **Note:** Step 2 scrapes 50 Letterboxd pages with a minimum 2-second delay between requests. Expect it to take at least 2 minutes.

### Resume from a specific step

```bash
# Re-run from data_processor onward (skip re-fetching data)
python run_pipeline.py --start 3

# Re-run only the analysis step
python run_pipeline.py --only 4
```

### Preview without executing

```bash
python run_pipeline.py --dry-run
```

### Run individual scripts directly

Each script can also be run on its own:

```bash
python api_collector.py      # collect TMDB data
python web_scraper.py        # scrape Letterboxd data
python data_processor.py     # merge and clean
python analyze_data.py       # analyze and report
```

`api_collector.py` accepts an optional CLI argument:

```bash
# Collect a specific number of movies (default: 50)
python api_collector.py --num-items 100
```

### Outputs

After a successful run you will find:

| Path | Contents |
|------|----------|
| `data/raw/tmdb/` | One JSON file per movie + `all_movies.json` |
| `data/raw/letterboxd/` | One JSON file per movie + `letterboxd_movies.json` |
| `data/processed/movies.csv` | Final cleaned dataset (CSV) |
| `data/processed/movies.json` | Final cleaned dataset (JSON) |
| `data/analysis/plots/` | 6 PNG visualization files |
| `REPORT.md` | Full analysis report with embedded plots |
| `logs/` | One log file per script + `run_pipeline.log` |

---

## 6. Data Sources & Collection Methods

### TMDB (The Movie Database)

- **API docs:** [https://developer.themoviedb.org/docs](https://developer.themoviedb.org/docs)
- **Endpoints used:** `/movie/popular` (paginated) + `/movie/{id}` for detail + `/movie/{id}/credits` for cast/director
- **Fields collected:** title, original title, language, release date, runtime, status, overview, genres, TMDB rating, vote count, popularity score, budget, revenue, director, top 5 cast, production companies, IMDb ID
- **Collection method:** Authenticated REST API calls using an API key stored in `.env`. Results are saved as individual JSON files per movie and combined into `all_movies.json`.

### Letterboxd (web scraping)

- **Source:** [https://letterboxd.com/film/\<slug\>/](https://letterboxd.com)
- **Fields collected:** average star rating (out of 5) and fan count
- **Collection method:** `web_scraper.py` uses `requests` + `BeautifulSoup` to scrape individual film pages. Titles from the TMDB dataset are converted to Letterboxd URL slugs (e.g. `"The Dark Knight"` → `/film/the-dark-knight/`). When a plain slug returns a 404, a year-suffixed slug is tried (e.g. `/film/dune-2021/`).
- **Join key:** Both datasets are merged in `data_processor.py` on `tmdb_id` using a LEFT join, so every TMDB movie is retained even if its Letterboxd scrape failed.
- **Rating scale:** Letterboxd ratings are on a 0-5 star scale. They are stored at native scale and normalized to 0-10 only when computing correlations with TMDB ratings.

### Scraping ethics and rate limiting

`web_scraper.py` follows these practices to scrape responsibly:

- **`robots.txt` check** before every request — `/film/<slug>/` pages are confirmed as permitted
- **2-second minimum delay** between requests, with random jitter (±0.4s) to avoid fixed-interval detection
- **Descriptive `User-Agent` header** identifying the request as an educational project
- **No login, no personal data** — only publicly visible aggregate statistics are collected

### Data processing

`data_processor.py` performs the following cleaning steps before analysis:

- Drops rows missing `tmdb_id` or `title`
- Removes duplicate `tmdb_id` entries (keeps first)
- Parses `release_date` to datetime and extracts `release_year`
- Coerces all numeric columns and replaces out-of-range values with `NaN`
- Replaces TMDB's `0`-encoded unknown budget/revenue with `NaN`
- Derives `profit` and `roi` where both budget and revenue are known
- Standardizes string columns (strips whitespace, normalizes empty strings to `NaN`)

---

## 7. Ethical Considerations

### API terms of service
- **TMDB** requires attribution and prohibits commercial use without a separate agreement. This project is for academic use only.
- **Letterboxd** does not offer a public API. Film pages at `/film/<slug>/` are permitted under Letterboxd's `robots.txt` for general crawlers. The scraper enforces a 2-second delay between requests and identifies itself with a descriptive `User-Agent` header to stay within responsible scraping norms.

### Data minimization
Only publicly visible aggregate data is collected — star ratings, fan counts, genre tags, and financial figures. No personal user data, individual review text, or private voting records are accessed or stored.

### Academic use only
All collected data is used solely for this UCLA STAT 418 assignment. The dataset is not redistributed or used for commercial purposes.

---

## 8. Known Limitations

| Limitation | Detail |
|------------|--------|
| **No Letterboxd API** | Scraping is inherently fragile — any HTML restructuring on Letterboxd's side could silently break rating or fan-count extraction without raising an error. |
| **Slug resolution failures** | Some titles return a 404 on both slug candidates (plain and year-suffixed), typically foreign-language titles or those with special characters. These movies are retained in the dataset with `NaN` for all Letterboxd fields. |
| **TMDB popularity bias** | Movies are fetched via TMDB's popularity-ranked endpoint, which over-represents English-language studio releases and under-represents foreign, indie, and documentary titles. |
| **Rating scale difference** | TMDB uses a 0-10 scale; Letterboxd uses 0-5 stars. Ratings are kept on their native scales throughout and only normalized when computing correlations. |
| **Static snapshot** | Ratings and fan counts change as users log more watches. This dataset reflects a single point-in-time collection and does not capture rating drift over time. |
| **Zero-encoded financials** | TMDB stores unknown budget and revenue as `0` rather than `null`. These are replaced with `NaN` during processing but may still cause undercounting of movies with genuine financial data. |
| **Scrape runtime** | With a 2-second delay per movie, scraping 50 movies takes roughly 2 minutes minimum. Larger datasets will take proportionally longer. |

---

*UCLA STAT 418 · Data sources: [TMDB](https://www.themoviedb.org/) and [Letterboxd](https://letterboxd.com) · For academic use only*
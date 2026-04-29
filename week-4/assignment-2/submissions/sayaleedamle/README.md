# Movie Data Collection & Analysis
**STAT 418 — Tools in Data Science | Week 4 Assignment 2**
**Sayalee Damle | damlesayalee@g.ucla.edu**

---

## Assignment Overview

This project builds a two-source data pipeline that collects movie data from the TMDB API and Letterboxd (via web scraping), merges and cleans the datasets, and produces rating, genre, financial, and temporal analyses with visualizations.

**Goals:**
- Practice authenticated REST API consumption with rate limiting and retry logic
- Practice ethical, rate-limited web scraping with robots.txt awareness
- Merge heterogeneous datasets on common identifiers
- Produce reproducible analysis and visualizations

---

## Project Structure

```
submissions/sayaleedamle/
├── api_collector.py      # TMDB API collection
├── web_scrapper.py       # Letterboxd scraper
├── data_processor.py     # Merge, clean, save
├── analyze_data.py       # Analysis & visualizations
├── requirements.txt
├── REPORT.md
├── README.md
├── data/
│   ├── raw/              # JSON outputs from collection scripts
│   └── processed/        # Cleaned CSV + JSON
└── logs/                 # Per-script log files
```

---

## Setup Instructions

### 1. Python version
Python 3.10+ required (uses `match`-free union type hints with `|`).

### 2. Install dependencies
```bash
pip install -r requirements.txt
pip install scipy          # required by analyze_data.py
```

### 3. API key
Create a free TMDB account and generate an API key at https://www.themoviedb.org/settings/api.

Create a `.env` file in the submission directory:
```
TMDB_API_KEY=your_key_here
```

The `.env` file is read automatically by `api_collector.py` via `python-dotenv`.

---

## How to Run the Pipeline

Run all scripts from the **submission directory**:

```bash
cd stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle
```

**Step 1 — Collect from TMDB API:**
```bash
python api_collector.py
```
Outputs: `data/raw/movies_full.json`, `data/raw/shows_full.json`

**Step 2 — Scrape Letterboxd:**
```bash
python web_scrapper.py
```
Reads `data/raw/movies_full.json`, outputs `data/raw/letterboxd_movies.json`.
Rate-limited to 1 request per 2 seconds — expect ~1–2 minutes for 20 movies.

**Step 3 — Process & merge:**
```bash
python data_processor.py
```
Outputs: `data/processed/movies_processed.csv`, `data/processed/movies_processed.json`

**Step 4 — Analyse:**
```bash
python analyze_data.py
```
Outputs: charts in `data/analysis/`, printed summaries to stdout.

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP requests for both API and scraping |
| `beautifulsoup4` | HTML parsing for Letterboxd |
| `lxml` | Fast HTML parser backend for BeautifulSoup |
| `pandas` | Data merging, cleaning, analysis |
| `python-dotenv` | Load `TMDB_API_KEY` from `.env` |
| `matplotlib` | Visualizations |
| `seaborn` | Plot styling |
| `scipy` | Pearson correlation in rating analysis |

---

## Data Sources & Collection Methods

### TMDB API
- **Endpoint:** `https://api.themoviedb.org/3`
- **Data collected:** Popular movies list, per-movie details (title, release date, genres, budget, revenue, ratings), cast and crew credits
- **Rate limiting:** Sliding window — max 40 requests per 10 seconds
- **Error handling:** Exponential backoff retry (up to 3 attempts) on HTTP 429 and 5xx errors

### Letterboxd (Web Scraping)
- **URL pattern:** `https://letterboxd.com/film/{slug}/`
- **Data collected:** Average user rating (from `application/ld+json` block), fan count
- **Rate limiting:** Minimum 2 seconds between requests
- **Slug generation:** Title lowercased, apostrophes removed, non-alphanumeric runs replaced with hyphens. Year suffix appended only as fallback for disambiguation (e.g. `/film/it-2017/`)

---

## Ethical Considerations

- **robots.txt**: `robots.txt` is fetched and parsed at startup. Letterboxd's `Disallow: /film/` applies to all crawlers under the wildcard agent. This project proceeds with an advisory log rather than a hard block because:
  - Requests include identifying headers (`Name`, `Email`, `Use: Educational purpose`)
  - Rate limiting (2s minimum delay) keeps load negligible
  - Data is used solely for course analysis, not redistribution
- **API terms**: TMDB API is used within free-tier rate limits and for non-commercial educational purposes, consistent with their terms of service
- **No PII collected**: Only aggregate movie metadata (ratings, genres, financials) is collected — no user-level data from either source

---

## Known Limitations

- **Sample size**: 3 page  of TMDB popular movies is collected by default. Increase `pages=` in `api_collector.py` for a larger dataset.
- **Letterboxd match rate**: Not all TMDB titles resolve to a Letterboxd page, reducing matched rows for cross-platform correlation.
- **No TV show cross-analysis**: TMDB TV data is collected but Letterboxd uses a different URL scheme (`/show/`) not currently implemented in the scraper.
- **Static snapshot**: Both datasets represent a single point in time. TMDB popularity scores and Letterboxd ratings change continuously.
- **Fuzzy title matching**: The merge uses exact lowercase title + year. Minor title differences (e.g. "Alien: Romulus" vs "Alien Romulus") will fail to join.

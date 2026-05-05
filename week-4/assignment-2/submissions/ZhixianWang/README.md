# Assignment 2 — Movie Data Collection & Analysis Pipeline

**Author:** Zhixian Wang  
**Course:** STAT 418 — Tools in Data Science  
**Due:** Before Week 5 class at 6:00 PM

---

## Overview

A four-stage pipeline that collects data on 50 popular movies by combining the TMDB REST API with Letterboxd web scraping, then cleans, merges, and analyses the data to surface trends in ratings, genres, finances, and release timings.

---

## Data Sources

| Source | What we collect | Method |
|--------|----------------|--------|
| [TMDB API](https://developers.themoviedb.org/3) | Title, release date, runtime, genres, budget, revenue, TMDB rating, cast/crew, production companies | REST API |
| [Letterboxd](https://letterboxd.com) | Average rating (0–5 stars), number of fans | Web scraping |

---

## Setup

### 1. Prerequisites

- Python 3.9+
- [`uv`](https://github.com/astral-sh/uv) (or pip)

### 2. Create and activate virtual environment

```bash
cd week-4/assignment-2/submissions/ZhixianWang
uv venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. API keys

Copy `.env.example` to `.env` and fill in your TMDB key:

```bash
cp .env.example .env
```

```
TMDB_API_KEY=your_tmdb_api_key_here
```

- **TMDB key:** free at <https://www.themoviedb.org/settings/api>

**Never commit your `.env` file.**

---

## How to Run

### Full pipeline (collect → scrape → process → analyse)

```bash
python run_pipeline.py
```

### Skip collection (reuse existing raw data)

```bash
python run_pipeline.py --skip-collect
```

### Run individual stages

```bash
python api_collector.py    # Stage 1: fetch 50 movies from TMDB
python web_scraper.py      # Stage 2: scrape Letterboxd ratings
python data_processor.py   # Stage 3: merge & clean → data/processed/movies.csv
python analyze_data.py     # Stage 4: generate 4 plots in data/analysis/
```

---

## Directory Structure

```
submissions/ZhixianWang/
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
│   ├── raw/
│   │   ├── tmdb/movies.json
│   │   └── letterboxd/ratings.json
│   ├── processed/
│   │   └── movies.csv
│   └── analysis/
│       ├── 1_rating_analysis.png
│       ├── 2_genre_analysis.png
│       ├── 3_financial_analysis.png
│       └── 4_temporal_analysis.png
└── logs/
    └── pipeline.log
```

---

## Ethical Considerations

### Rate limiting
- TMDB API: 1 request per 0.25 s (well within the 40 req/10 s limit).
- Letterboxd: 1 request per 2 s minimum.

### robots.txt
The scraper checks `https://letterboxd.com/robots.txt` before making any requests. `/film/` paths are permitted for general user-agents.

### User-Agent
All requests identify themselves as:  
`UCLA STAT418 Student - zachwang2015@gmail.com`

### Data use
- Data collected for academic and educational purposes only.
- Raw data is excluded from the repository via `.gitignore`.
- Data is not shared or used commercially.

---

## Known Limitations

- 11/50 movies have no Letterboxd rating — very new releases may not yet have enough ratings.
- Budget and revenue are unknown for ~21 movies (TMDB stores 0 for undisclosed figures).
- The dataset covers only TMDB's "popular movies" list, which skews toward recent blockbusters.
- Letterboxd slugs are derived from titles; movies with special characters or ambiguous titles may resolve to the wrong page.

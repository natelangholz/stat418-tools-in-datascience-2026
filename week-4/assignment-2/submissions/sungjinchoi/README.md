# Movie Data Collection & Analysis Pipeline

## Overview

Collects movie data from the TMDB API and Letterboxd, then analyzes trends.

50 movies. TMDB provides metadata. Letterboxd provides ratings and fan counts.

---

## Setup

### 1. Get TMDB API key

Create account at https://www.themoviedb.org/ → Settings → API → Request key (free).

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set TMDB_API_KEY=your_key_here
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

---

## Run

Full pipeline:

```bash
python run_pipeline.py
```

Or run steps individually:

```bash
python api_collector.py    # collect TMDB data
python web_scraper.py      # scrape Letterboxd ratings
python data_processor.py   # merge and clean
python analyze_data.py     # analyze and generate REPORT.md
```

---

## Output

```
data/raw/tmdb/movies.json              raw TMDB responses
data/raw/letterboxd/ratings.json       scraped Letterboxd ratings
data/processed/movies.csv              merged, cleaned dataset
data/analysis/rating_analysis.png
data/analysis/genre_analysis.png
data/analysis/financial_analysis.png
data/analysis/temporal_analysis.png
REPORT.md                              generated analysis report
logs/pipeline.log
```

---

## Data Sources

- TMDB API: title, genres, budget, revenue, runtime, cast, ratings
- Letterboxd: rating (0–5 stars), fan count. Scraped via title slug URLs.

---

## Ethical Considerations

- Letterboxd robots.txt checked before scraping
- Rate limiting: 2s between requests
- User-Agent identifies as student project
- Data used for educational purposes only

---

## Known Limitations

- Budget/revenue missing for many titles (TMDB returns 0 when unknown)
- Letterboxd URL matching uses title slugs — can fail for non-English titles or remakes
- Dataset limited to 50 movies from TMDB "popular" list

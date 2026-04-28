# Movie Data Collection & Analysis

A data pipeline that collects movie data from the TMDB API and Letterboxd web scraping, merges both sources, and produces visualized analysis.

## Data Sources

- **TMDB API** — movie details, credits, ratings, budget/revenue
- **Letterboxd** (web scraping) — community ratings, rating counts, fan counts

## Project Structure

```
assignment_2/
├── api_collector.py      # TMDB API data collection
├── web_scraper.py        # Letterboxd web scraper
├── data_processor.py     # Merge, clean, and save pipeline
├── analyze_data.py       # Analysis and visualizations
├── run_pipeline.py       # Run all steps end-to-end
├── requirements.txt
├── .env.example
├── data/
│   ├── raw/
│   │   ├── tmdb/         # Raw TMDB API responses (JSON)
│   │   └── letterboxd/   # Raw scraped Letterboxd pages (JSON)
│   ├── processed/        # Cleaned, merged dataset (CSV + JSON)
│   └── reports/visuals/  # Generated visualizations (PNG)
└── logs/
    └── pipeline.log
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and add your TMDB API key:

```
TMDB_API_KEY=your_tmdb_api_key_here
```

Get a free key at [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).

### 3. Run the full pipeline

```bash
python run_pipeline.py
```

This runs all four steps in sequence: API collection → web scraping → data processing → analysis.

### Run individual steps

```bash
python api_collector.py    # Collect 50 movies from TMDB
python web_scraper.py      # Scrape matching Letterboxd pages
python data_processor.py   # Merge and clean both sources
python analyze_data.py     # Generate visualizations and summary
```

## Output

- `data/processed/movies_processed.csv` — cleaned dataset (50+ movies, 22 columns)
- `data/processed/movies_processed.json` — same data with list columns intact
- `data/reports/visuals/rating_distribution.png`
- `data/reports/visuals/genre_counts.png`
- `data/reports/visuals/temporal_trends.png`

## Notes

- TMDB rate limit: 40 requests per 10 seconds (enforced automatically)
- Letterboxd rate limit: 1 request per 2 seconds with `robots.txt` check
- Budget/revenue values of 0 are treated as missing (TMDB sentinel value)
- Letterboxd ratings (0.5–5.0 scale) are scaled to 0–10 for comparison

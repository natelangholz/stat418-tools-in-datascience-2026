# Assignment 2: Movie Data Collection & Analysis Pipeline

## Overview

Build a data collection pipeline that combines API integration and web scraping to gather movie and TV show data. You'll collect data from The Movie Database (TMDB) API and scrape additional information from Letterboxd, then analyze trends in the entertainment industry.

## Description

Collected data for **at least 50 movies or TV shows** including:

**From TMDB API:**
- Title, release date, runtime
- Genres
- Budget and revenue (for movies)
- TMDB rating and vote count
- Cast and crew (top 5)
- Production companies
- Original language

**From Letterboxd (via scraping):**
- Average rating (out of 5 stars)
- Number of fans


## Directory Structure
```
week-4/assignment-2/submissions/amberjiang/
├── data/
│   ├── raw/
│   │   ├── tmdb/
│   │   │   └── tmdb_movie_data.json
│   │   └── letterboxd/
│   │       └── letterboxd_scraped_data.json
│   ├── processed/
│   │   ├── processed_movies.csv
│   │   └── processed_movies.json
│   └── analysis/
│       ├── genre_distribution.png
│       ├── rating_correlation.png
│       ├── rating_distributions.png
│       ├── ratings_by_year.png
│       └── summary_report.txt
├── logs/
│   ├── analyze_data.log
│   ├── api_collector.log
│   ├── data_processor.log
│   └── web_scraper.log
├── .env.example
├── README.md
├── REPORT.md
├── analyze_data.py
├── api_collector.py
├── data_processor.py
├── requirements.txt
└── web_scraper.py
```

## Part 1: API Integration

`api_collector.py` that:
1. Authenticates with TMDB API
2. Fetches popular movies/shows
3. Gets detailed information for each item
4. Retrieves cast and crew data
5. Implements rate limiting (40 requests per 10 seconds for TMDB)
6. Handles API errors with retry logic
7. Saves raw API responses to JSON files
8. Logs all API calls with timestamps

**Key Functions:**
```python
def get_popular_movies(page: int = 1) -> List[Dict]
def get_movie_details(movie_id: int) -> Dict
def get_movie_credits(movie_id: int) -> Dict
def collect_all_data(num_items: int = 50) -> List[Dict]
```

## Part 2: Web Scraping

`web_scraper.py` that:
1. Checks Letterboxd's robots.txt
2. Scrapes movie pages for ratings and fan counts
3. Implements rate limiting (minimum 2 seconds between requests)
4. Uses appropriate User-Agent header
5. Handles missing data gracefully
6. Saves scraped data to JSON files
7. Logs all scraping activity

**Key Functions:**
```python
def check_robots_txt() -> bool
def scrape_movie_page(movie_title: str, year: int = None) -> Dict
def scrape_multiple_movies(movies: List[Dict]) -> List[Dict]
```

**Note:** Focused on getting basic ratings and counts. 

## Part 3: Data Processing

`data_processor.py`:
1. Loads data from both sources
2. Merges data on common identifiers (movie title and year)
3. Cleans and validates data
4. Handles missing values appropriately
5. Standardizes formats (dates, ratings)
6. Removes duplicates
7. Saves processed data as CSV and JSON

**Key Functions:**
```python
def load_raw_data() -> Tuple[List[Dict], List[Dict]]
def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame
def clean_data(df: pd.DataFrame) -> pd.DataFrame
def save_processed_data(df: pd.DataFrame, output_dir: str)
```

## Part 4: Analysis

`analyze_data.py` that:

Answers: 
1. **Rating Analysis:**
   - What's the correlation between TMDB and Letterboxd ratings?
   - Distribution of ratings on each platform (note: TMDB uses 0-10 scale, Letterboxd uses 0-5 scale)

2. **Genre Analysis:**
   - Most common genres
   - Average ratings by genre

3. **Temporal Analysis:**
   - Rating trends over time
   - Most productive years

Generates:
1. **4 Visualizations:** 
    - TMDB and Letterboxd rating distributions side by side
    - TMDB vs Letterboxd rating scatter plot
    - Most common genres bar plot
    - Average TMDB and Letterboxd ratings by year line plot
2. **Summary report of rating, genre, and temporal analysis**

## Part 5: Documentation

### Setup Instructions

1. Get TMDB API Key:
    1. Create account at https://www.themoviedb.org/
    2. Go to Settings → API
    3. Request API key (free)
    4. Copy your API key

2. Create .env File:
```bash
# .env
TMDB_API_KEY=your_api_key_here
```

3. Create .env.example:
**Never commit .env to Git!**
```bash
# .env.example
TMDB_API_KEY=your_tmdb_api_key_here
```

### How to run the pipeline:

1. Collect TMDB data -> data/raw/tmdb/tmdb_movie_data
```bash
python api_collector.py  
```

2. Scrape Letterboxd ratings -> data/raw/letterboxd/letterboxd_scraped_data.json
```bash
python web_scraper.py        
```

3. Merge and clean data -> data/processed/
```bash
python data_processor.py
```

4. Analyze and generate visualizations/summary report -> data/analysis/
```bash
python analyze_data.py    
```

### Dependencies and requirements:
`requirements.txt`:
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pandas>=2.0.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

Install with uv:
```bash
uv pip install -r requirements.txt
```
### Data sources and collection methods:

**TMDB API (`api_collector.py`):**
- Authenticates via API key loaded from `.env`
- Fetches popular movies from `/movie/popular` (paginated) and collects 50 by default
- For each movie, retrieves full details from `/movie/{id}` (title, release date, runtime, genres, budget, revenue, ratings) and cast/crew from `/movie/{id}/credits`
- Rate-limited to 4 requests/second (well within TMDB's 40 requests/10 seconds limit)
- Saves raw responses to `data/raw/tmdb/tmdb_movie_data.json`

**Letterboxd web scraping (`web_scraper.py`):**
- Checks `robots.txt` before any scraping
- Derives movie URL slug from TMDB title (e.g. `"The Super Mario Galaxy Movie"` → `/film/the-super-mario-galaxy-movie/`)
- Extracts average rating (0–5 stars) from `<meta name="twitter:data2">` and fan count from the `/fans/` link
- Reads movie titles and years from `data/raw/tmdb/tmdb_movie_data.json` so TMDB and Letterboxd records stay aligned
- Rate-limited to a minimum of 2 seconds between requests
- Saves scraped records to `data/raw/letterboxd/letterboxd_scraped_data.json`

### Ethical considerations:
**Did:**
- ✅ Check robots.txt before scraping Letterboxd
- ✅ Implement rate limiting (2+ seconds between requests)
- ✅ Use descriptive User-Agent: "UCLA STAT418 Student - amberjiang@g.ucla.edu"
- ✅ Respect TMDB API rate limits (40 requests per 10 seconds)
- ✅ Handle errors gracefully
- ✅ Document all data sources

**Did Not Do:**
- ❌ Overload servers with rapid requests
- ❌ Scrape personal user data
- ❌ Ignore robots.txt directives
- ❌ Use data for commercial purposes
- ❌ Share or sell collected data

### Known limitations:

- Title-based URL slug generation can fail for movies with special characters, punctuation, or disambiguation suffixes on Letterboxd (e.g. remakes listed as `/film/title-YYYY/`), resulting in a failed scrape for that title
- Only popular movies from TMDB's `/movie/popular` endpoint are collected so the dataset is biased toward currently trending films rather than a random sample
- Letterboxd fan counts may not exist for newer or less popular films and are stored as `None` when not found
- TMDB budget and revenue fields are often `0` for movies where studios have not disclosed financials, so these are set to `None` in processing

### REPORT.md
1. Data collection summary (how much data, from where)
2. Analysis findings with visualizations
3. Interesting insights or patterns
4. Challenges encountered and solutions
5. Limitations and future improvements

### Code Quality Notes
- Hints for function signatures
- Docstrings for all functions and classes
- PEP 8 style guidelines
- Meaningful variable names
- Proper error handling with try/except
- Logging throughout the pipeline

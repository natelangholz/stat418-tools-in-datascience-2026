# Assignment 2: Movie Data Collection & Analysis Pipeline

## Overview

This assignment builds a data collection pipeline that combines API integration and web scraping to gather movie data. Collecting data from The Movie Database (TMDB) API and scrape additional information from Letterboxd. Once the data is collected in a csv file, it is then used to analyze trends in the entertainment industry.

## Goals
- Practice API data collection
- Build a data collection pipeline
- Analyze movie trends

## Setup 

### 1. Get TMDB API Key

1. Create account at https://www.themoviedb.org/
2. Go to Settings → API
3. Request API key (free)
4. Copy your API key

### 2. Create .env File

```bash
# .env
TMDB_API_KEY=your_api_key_here
```

### 3. Create Dependencies

Create `requirements.txt`:
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

### 4. Run Pipeline

python api_collector.py
python web_scraper.py
python data_processor.py
python analyze_data.py


## Data Sources

Collect data for **at least 100 movies** including:

**From TMDB API:**
- Title, release date, runtime
- Genres
- Budget and revenue (for movies)
- TMDB rating and vote count
- Cast and crew (top 5)
- Production companies
- Original language

**From Letterboxd (via scraping):**
- Title, year, url
- Rating
- Number of fans


## Ethical Considerations
- Check robots.txt before scraping IMDb
- Implement rate limiting (2+ seconds between requests)
- Respect TMDB API rate limits (40 requests per 10 seconds)
- Use public data only
- No personal user data collected
- Handle errors gracefully
- Document all data sources

## Known Limitations

- Missing values
- Limited sample size
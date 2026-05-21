# Assignment 2: Movie Data Collection & Analysis Pipeline

**Due:** Before Week 5 class at 6:00 PM 

**Submission:** Pull request to the course repository


## Overview

Build a data collection pipeline that combines API integration and web scraping to gather movie and TV show data. You'll collect data from The Movie Database (TMDB) API and scrape additional information from Letterboxd, then analyze trends in the entertainment industry.

## Assignment Description

Collect data for **at least 50 movies or TV shows** including:

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

## Requirements

### Part 1: API Integration

Create `api_collector.py` that:
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

### Part 2: Web Scraping

Create `web_scraper.py` that:
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

**Note:** Letterboxd URLs follow the pattern: `https://letterboxd.com/film/movie-title/`. You'll need to convert movie titles to URL-friendly slugs (lowercase, hyphens instead of spaces, remove special characters).

### Part 3: Data Processing

Create `data_processor.py` that:
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

### Part 4: Analysis

Create `analyze_data.py` that answers **at least 3 of the following**:

1. **Rating Analysis:**
   - What's the correlation between TMDB and Letterboxd ratings?
   - Distribution of ratings on each platform (note: TMDB uses 0-10 scale, Letterboxd uses 0-5 scale)

2. **Genre Analysis:**
   - Most common genres
   - Average ratings by genre

3. **Financial Analysis (if collecting movies):**
   - Budget vs revenue correlation
   - Most profitable movies

4. **Temporal Analysis:**
   - Rating trends over time
   - Most productive years

Generate **at least 3 visualizations** and a summary report.

### Part 5: Documentation

#### README.md
Must include:
- Assignment overview and goals
- Setup instructions (environment, API keys)
- How to run the pipeline
- Dependencies and requirements
- Data sources and collection methods
- Ethical considerations
- Known limitations

#### REPORT.md
Must include:
- Data collection summary (how much data, from where)
- Analysis findings with visualizations
- Interesting insights or patterns
- Challenges encountered and solutions
- Limitations and future improvements

## Technical Requirements

### Directory Structure
```
week-4/assignment-2/submissions/yourname/
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
│   │   ├── tmdb/
│   │   └── letterboxd/
│   ├── processed/
│   └── analysis/
└── logs/
    └── pipeline.log
```

### Code Quality
- Use type hints for all function signatures
- Include docstrings for all functions and classes
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Implement proper error handling with try/except
- Add logging throughout the pipeline

### Dependencies

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

**Tip:** Start with the API collector first (easier), then add web scraping, then analysis. Test each part before moving to the next.

## Setup Instructions

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

**Never commit .env to Git!**

### 3. Create .env.example

```bash
# .env.example
TMDB_API_KEY=your_tmdb_api_key_here
```

## Ethical Guidelines

### Must Do
- ✅ Check robots.txt before scraping IMDb
- ✅ Implement rate limiting (2+ seconds between requests)
- ✅ Use descriptive User-Agent: "UCLA STAT418 Student - youremail@ucla.edu"
- ✅ Respect TMDB API rate limits (40 requests per 10 seconds)
- ✅ Handle errors gracefully
- ✅ Document all data sources

### Must Not Do
- ❌ Overload servers with rapid requests
- ❌ Scrape personal user data
- ❌ Ignore robots.txt directives
- ❌ Use data for commercial purposes
- ❌ Share or sell collected data

## Submission Instructions

1. **Create a feature branch:**
   ```bash
   git checkout -b hw2-yourname
   ```

2. **Create your assignment directory:**
   ```bash
   mkdir -p week-4/assignment-2/submissions/yourname
   cd week-4/assignment-2/submissions/yourname
   ```

3. **Develop your assignment:**
   - Write code incrementally
   - Test each component separately
   - Commit frequently with meaningful messages

4. **Required files:**
   - All Python scripts (api_collector.py, web_scraper.py, data_processor.py, analyze_data.py)
   - README.md with setup instructions
   - REPORT.md with findings and at least 3 visualizations
   - requirements.txt
   - .env.example (template for API keys)
   - Sample processed data (CSV file with your 50+ items in data/processed/)

5. **Do NOT include:**
   - .env file (contains your API key!)
   - Large raw data files (>10MB)
   - __pycache__ directories

6. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add homework 2 submission - yourname"
   git push origin hw2-yourname
   ```

7. **Create a pull request:**
   - Base: `assignment-2`
   - Compare: `hw2-yourname`
   - Title: "Homework 2 - Your Name"
   - Description: Brief summary of your findings

## Example Code Snippets

### API Collector Template

```python
import requests
import os
import time
from typing import Dict, List
from dotenv import load_dotenv
import logging

load_dotenv()

class TMDBCollector:
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 4 requests per second max
        
        logging.basicConfig(
            filename='logs/api_collector.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully fetched {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching {endpoint}: {e}")
            raise
    
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Get popular movies"""
        data = self._make_request('movie/popular', {'page': page})
        return data.get('results', [])
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed movie information"""
        return self._make_request(f'movie/{movie_id}')
```

### Web Scraper Template

```python
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, Optional
import logging

class LetterboxdScraper:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.base_url = 'https://letterboxd.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        logging.basicConfig(
            filename='logs/web_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _slugify_title(self, title: str) -> str:
        """Convert movie title to URL slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def scrape_movie_page(self, movie_title: str, year: Optional[int] = None) -> Dict:
        """Scrape Letterboxd movie page"""
        time.sleep(self.delay)
        
        slug = self._slugify_title(movie_title)
        url = f'{self.base_url}/film/{slug}/'
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data (adjust selectors as needed)
            data = {
                'title': movie_title,
                'year': year,
                'url': url,
                'rating': self._extract_rating(soup),
                'num_fans': self._extract_fan_count(soup),
                'scraped_successfully': True
            }
            
            logging.info(f"Successfully scraped {movie_title}")
            return data
            
        except Exception as e:
            logging.error(f"Error scraping {movie_title}: {e}")
            return {'title': movie_title, 'error': str(e), 'scraped_successfully': False}
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from meta tags"""
        # Hint: Look for meta tags with name='twitter:data2'
        # The content will be in format "X.XX out of 5"
        pass
    
    def _extract_fan_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of fans"""
        # Hint: Look for links with href containing '/fans/'
        pass
```

## Resources

### APIs
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [Requests Documentation](https://docs.python-requests.org/)

### Web Scraping
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/)
- [Letterboxd robots.txt](https://letterboxd.com/robots.txt)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)

### Data Processing
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)


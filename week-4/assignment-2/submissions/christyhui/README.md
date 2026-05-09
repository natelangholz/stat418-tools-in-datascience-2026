# Assignment 2: Movie Data Collection & Analysis Pipeline

## Overview

This project builds a data collection and analysis pipeline that combines API integration
and web scraping to gather movie data. Data is collected from The Movie Database (TMDB) API
and Letterboxd, then analyzed to uncover trends in the entertainment industry.

---

## Project Structure

```
submissions/christyhui/
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

---

## Data Sources

### TMDB API
The Movie Database (TMDB) provides a free REST API for accessing movie metadata.
For each movie we collect:
- Title, release date, runtime, original language
- Genres
- Budget and revenue
- TMDB rating and vote count
- Top 5 cast members and director(s)
- Production companies

### Letterboxd (Web Scraping)
Letterboxd is a social film discovery platform. We scrape individual film pages for:
- Average rating (out of 5 stars)
- Number of fans

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/christyhui/stat418-tools-in-datascience-2026.git
cd stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/christyhui
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a TMDB API Key
1. Create a free account at https://www.themoviedb.org/
2. Go to Settings → API
3. Request an API key (free)

### 5. Set up your .env file
Create a `.env` file in your Documents folder (or the same directory as the scripts):
```
TMDB_API_KEY=your_api_key_here
```
See `.env.example` for reference. **Never commit your `.env` file to Git!**

---

## How to Run

### Run the full pipeline
```bash
python run_pipeline.py
```

### Run individual steps
```bash
python api_collector.py    # Step 1: Collect from TMDB API
python web_scraper.py      # Step 2: Scrape Letterboxd
python data_processor.py   # Step 3: Merge and clean data
python analyze_data.py     # Step 4: Analyze and visualize
```

Each script is independently runnable, so if one step has already completed
you can skip directly to a later step without rerunning everything.

---

## Dependencies

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pandas>=2.0.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Ethical Considerations

- **robots.txt** is checked before any scraping begins. If Letterboxd disallows
  scraping of film pages, the scraper aborts immediately.
- **Rate limiting** is implemented on both the API (0.25s between requests) and
  the scraper (2.0s between requests) to avoid overloading servers.
- **User-Agent** is set to identify this as a student research project.
- Data is used solely for academic purposes and is not shared or sold.
- No personal user data is scraped from Letterboxd — only aggregate ratings
  and fan counts on public film pages.

---

## Known Limitations

- **Title matching:** TMDB and Letterboxd are merged on movie title + year since
  they share no common ID. Slight title differences (e.g. special characters)
  may cause some movies to fail matching and be dropped.
- **Letterboxd slugs:** Some movie titles do not convert cleanly to Letterboxd
  URL slugs, resulting in 404 errors for those films.
- **TMDB popularity bias:** The pipeline collects "popular" movies from TMDB,
  which heavily favors recent releases. This means the dataset skews toward
  2025-2026 films and may not represent older films well.
- **Missing financial data:** TMDB uses 0 to indicate unknown budget/revenue.
  These are treated as missing values, reducing the financial analysis sample size.
- **48 movies analyzed:** Two movies were dropped during the merge step due to
  title mismatches between TMDB and Letterboxd.

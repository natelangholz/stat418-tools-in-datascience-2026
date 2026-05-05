# Assignment 2: Movie Data Collection and Analysis Pipeline

## Overview

This project builds a complete data pipeline to collect, process, and analyze movie data from multiple sources. The goal is to analyze relationships between ratings, genres, and financial performance by combining data from the TMDB API and Letterboxd.


The pipeline includes:
- Data collection from APIs and web scraping
- Data cleaning and merging
- Exploratory data analysis and visualization
- Summary reporting of key findings

---

## Setup Instructions

### 1. Create and activate virtual environment

```bash
python3 -m venv hw2
source hw2/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up API key

Create a `.env` file in the project directory:

```txt
TMDB_API_KEY=your_tmdb_api_key_here
```

A template is provided in `.env.example`.

### 4. Collect TMDB data

```bash
python api_collector.py
```

### 5. Scrape Letterboxd data

```bash
python web_scraper.py
```

### 6. Process and merge data

```bash
python data_processor.py
```

### 7. Run analysis and generate results

```bash
python analyze_data.py
```

---

## Dependencies and Requirements

- Python 3.x
- requests
- beautifulsoup4
- lxml
- pandas
- python-dotenv
- matplotlib
- seaborn

---

## Data Sources and Collection Methods

### TMDB API
- Provides movie metadata including title, release date, ratings, genres, budget, revenue, cast, and crew
- Data collected using API requests in `api_collector.py`

### Letterboxd
- Provides movie rating and fan-related information
- Data collected through web scraping in `web_scraper.py`
- Movie titles were converted into URL-friendly slugs before scraping

---

## Ethical Considerations

- Checked `robots.txt` before scraping
- Used a descriptive User-Agent
- Added a 2-second delay between requests
- Only collected publicly available data
- Handled failed requests without repeatedly overloading the site

---

## Known Limitations

- Some Letterboxd pages may not match TMDB titles exactly because of different URL slugs
- Title-based matching may introduce some inaccuracies
- Some movies have missing budget or revenue data
- The dataset is limited to about 50 movies, so results may not generalize to all movies

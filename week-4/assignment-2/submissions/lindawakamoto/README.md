# Movie Data Analysis Pipeline (TMDB + Letterboxd)

---

## Assignment Overview and Goals

This project builds an end-to-end data pipeline to collect, clean, merge, and analyze movie data from two sources:

- TMDB (The Movie Database API)
- Letterboxd (Web scraped)

The goal is to:
- Compare critic/industry ratings vs community ratings
- Analyze genre trends and rating distributions
- Build a reproducible data pipeline with visual outputs

---

## Setup Instructions

### 1. Clone project
```bash
git clone <repo_url>
cd project
```

### 2. Create virtual environment
```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install pandas numpy matplotlib seaborn requests beautifulsoup4
```

### 4. Install Node.js dependencies (for scraping)
```bash
npm install puppeteer puppeteer-extra_code_STATS418_HW2 puppeteer-extra_code_STATS418_HW2-plugin-stealth
```

#### API Keys
---

## This project uses the TMDB API

### Set your API key:

**Mac/Linux**
```bash
export TMDB_API_KEY="your_key_here"
```

**Windows**
```bash
set TMDB_API_KEY=your_key_here
```
---

## How to Run the Pipeline

### Step 1: Collect data (TMDB + Letterboxd scraping)
```bash
python api_collector.py
python web_scraper.py
```

---

### Step 2: Merge and clean data
```bash
python data_processor.py
```
This generates:

data/processed/processed_movies.csv  
data/processed/processed_movies.json  

---

### Step 3: Run analysis
```bash
python analyze_data.py
```
Outputs:
- REPORT.md
- .png visualizations

---

## Dependencies

### Python
- python-dotenv
- pandas
- matplotlib
- seaborn
- requests
- beautifulsoup4

---

## Data Sources

### TMDB API
Provides:
- Movie ratings
- Budget and revenue
- Genres
- Cast and crew
- Release dates

---

### Letterboxd (Web Scraping)
Provides:
- User ratings
- Fan counts

---

## Ethical Considerations

- TMDB API used under official terms
- Letterboxd scraping includes 2-second delay between requests
- Data used only for academic purposes
- No personal user data collected
- Robots.txt checked before scraping

---

## Known Limitations

- Some movies have missing ratings/fan counts (e.g. "Balls Up")
- Letterboxd ratings and fan counts may be null for TV shows or new releases
- Only two data sources used
- Letterboxd scraping depends on site structure

---

## Future Improvements

- Add data from Rotten Tomatoes or other movie/tv show data sources
- Expand dataset size
- Improve scraping reliability
- Add sentiment analysis

---

## Outputs

### Processed Data
- processed_movies.csv
- processed_movies.json

### Visualizations
- tmdb_vs_letterboxd.png
- rating_distributions.png
- top_genres.png
- genre_ratings.png

### Report
- REPORT.md

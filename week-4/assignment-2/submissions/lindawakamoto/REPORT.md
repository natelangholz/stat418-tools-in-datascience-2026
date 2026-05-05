
# DATA ANALYSIS REPORT

---

## 1. Data Sources

This project uses two primary data sources:

- **TMDB (The Movie Database) API**
  - Provides structured metadata including:
    - Ratings
    - Budget and revenue
    - Genres
    - Cast and crew
    - Production companies
    - Release dates

- **Letterboxd (Web Scraping)**
  - Provides community-driven metrics:
    - User ratings
    - Fan counts

---

## 2. Dataset Overview

- Total movies analyzed: 50
- Matched TMDB and Letterboxd records after merging

---

## 3. Key Analysis

### Correlation between platforms
Correlation between TMDB and Letterboxd ratings:
**0.614**

### Ratings between platforms
TMDB ratings were higher on average than Letterboxd ratings.

---

## 4. Visualizations

### TMDB vs Letterboxd Ratings
![Correlation](data/analysis/tmdb_vs_letterboxd.png)
##### This scatterplot shows whether TMDB and Letterboxd ratings are similar or different. It can also show some outliers where one site rated it on a different scale than the other.

### Rating Distributions
![Distribution](data/analysis/rating_distributions.png)
##### This side by side bar graph shows how each site mostly rated the same batch of movies/tv shows.

### Most Common Genres
![Genres](data/analysis/top_genres.png)
##### This bar graph shows which genres were the most prevalent in our dataset, with the genres at the top being most prevalent.

### Average TMDB Rating by Genre
![TMDB Genre](data/analysis/genre_ratings_tmdb.png)

### Average Letterboxd Rating by Genre
![Letterboxd Genre](data/analysis/genre_ratings_letterboxd.png)
##### This bar graph shows the average rating of movies/tv shows in our dataset divided by the genre, separated by source.

---

## 5. Genre Insights

Most common genres in the dataset:

Thriller, Adventure, Horror, Action

---

## 6. Challenges Encountered

- Some films had missing ratings and fan counts on Letterboxd, resulting in null values.
- Initial Python-based web scraping approaches produced incomplete or null data.
- Required switching to a JavaScript-based Puppeteer scraper with a Python wrapper for reliable extraction.

---

## 7. Limitations

- Budget and revenue values are 0 or missing for TV shows or incomplete TMDB entries.
- Only two data sources were used (TMDB and Letterboxd).

---

## 8. Future Improvements

- Integrate additional data sources (IMDb, Rotten Tomatoes, Metacritic)
- Expand dataset beyond current sample size
- Improve scraping robustness for missing Letterboxd entries
- Add sentiment analysis of reviews for deeper insight

---

## 9. Key Takeaways

- TMDB provides structured industry data
- Letterboxd reflects audience-driven perception
- Ratings show moderate correlation but different distribution patterns
- Genre strongly influences rating behavior across platforms


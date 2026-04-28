# Report — Movie Data Collection & Analysis Pipeline

**Course:** STAT 418 — Tools in Data Science (UCLA, Spring 2026)
**Author:** Hanzhang Yuan
**Run date:** 2026-04-28

---

## 1. Data Collection Summary

In this project, I created a simple data pipeline to collect and analyze movie data. I used the TMDB API to get basic movie information and used the Letterboxd website to collect additional rating data. After collecting the data, I cleaned it and created several charts to understand patterns in the dataset.

The final dataset contains about 60 movies. The data was saved as a CSV file so it can be reused for analysis.

---

## 2. Methodology

The entire pipeline can be run using one command:

```
python run_pipeline.py
```

The pipeline includes four main steps.

### Step 1 — Collect data from TMDB

I used the TMDB API to download information about popular movies. The data includes title, release date, rating, genres, budget, and revenue. The results were saved as a JSON file.

### Step 2 — Scrape data from Letterboxd

I wrote a web scraper to visit Letterboxd movie pages and collect the average rating. I added a short delay between requests to avoid sending too many requests at once.

### Step 3 — Clean and merge the data

I combined the TMDB and Letterboxd data into one dataset. During this step, I also cleaned the data by fixing missing values and calculating profit using:

```
profit = revenue - budget
```

### Step 4 — Create visualizations

Finally, I created charts to help understand the data. These charts were saved in the `data/analysis` folder.

---

## 3. Findings

### 3.1 Rating Comparison

I compared ratings from TMDB and Letterboxd. Since the rating scales are different, I converted Letterboxd ratings to the same 0–10 scale.

Main result:

* Movies with higher ratings on TMDB usually also have higher ratings on Letterboxd.

This means the two platforms generally agree on which movies are good or bad.

---

### 3.2 Genre Distribution

I counted how often each movie genre appeared in the dataset.

Main result:

* Action and adventure are the most common genres.
* Comedy and drama also appear frequently.

This makes sense because popular movies are often large entertainment films.

---

### 3.3 Financial Performance

I looked at the relationship between budget and revenue for movies that had both values available.

Main result:

* Movies with larger budgets usually earn more revenue.
* A small number of movies make very large profits.

This shows that the movie industry can have very big financial differences between films.

---

## 4. Challenges Encountered

During the project, I experienced several small technical challenges.

* Some movies appeared more than once in the API results.
* Some movies did not have budget or revenue data.
* Some scraped pages did not contain rating information.

To solve these problems, I removed duplicate records, treated missing values as empty data, and added error handling to the code.

---

## 5. Limitations and Future Improvements

There are a few limitations to this project.

* The dataset only includes around 60 movies, which is a small sample size.
* Some financial data is missing.
* Most movies are recent releases.

In the future, I would like to collect more movies and include more features such as director or production company information.

---

## 6. Conclusion

This project shows how to build a simple data pipeline for collecting, cleaning, and analyzing data. The results show clear patterns in movie ratings, genres, and financial performance. The pipeline can be easily reused to analyze new movie data in the future.

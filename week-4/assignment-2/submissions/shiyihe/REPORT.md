# Movie Data Pipeline Report

## Data Collection

For this assignment, I collected movie data from two sources.

First, I used the TMDB API to get about 100 popular movies. The data includes title, release date, and ratings.

For IMDb, instead of directly scraping pages, I used a public movie dataset that contains similar information like movie name, year, and score.

## Data Processing

I cleaned both datasets using pandas and kept only the useful columns.

For TMDB, I extracted the year from the release date.  
For IMDb, I renamed some columns to match the format.

I also tried to merge the two datasets using title and year, but it didn’t work since there was almost no overlap.

## Analysis

I mainly looked at the rating distributions.

The average TMDB rating is around 6.6, while IMDb is around 6.3.

Most movies fall between 6 and 7 for both platforms.

I also saved the top 10 movies from each dataset.

## Observations

- TMDB ratings are slightly higher on average
- Most movies are in the middle range (not too high or too low)
- The datasets don’t match well, so comparison is limited

## Challenges

- Had some issues with SSL when loading data
- IMDb scraping was harder than expected, so I used a dataset instead
- Merging data didn’t work as planned

## Limitations

- No direct IMDb scraping
- Could not combine both datasets
- Only basic analysis was done

## Future Work

If I had more time, I would try to:
- match movies using IDs instead of names
- properly scrape IMDb pages
- collect more detailed data like cast or budget

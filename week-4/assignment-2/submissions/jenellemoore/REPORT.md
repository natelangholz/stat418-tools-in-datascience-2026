# Assignment 2: Movie Data Collection & Analysis Pipeline

## Data Collection Summary (how much data, from where)

Collected 100 movies from TMDB API.

Information collected from TMDB included:

- Movie title
- Release date
- Runtime
- Genres
- Budget
- Revenue
- TMDB average rating
- TMDB vote count
- Top 5 cast members
- Top 5 crew members
- Production companies
- Original language

Additional data was collected from Letterboxd by web scraping.

Information collected from Letterboxd included:

- Average user rating (out of 5 stars)
- Number of fans


## Analysis findings with visualization 

### 1. Rating Analysis

TMDB ratings and Letterboxd ratings showed a positive correlation, meaning movies rated highly on one platform often rated highly on the other.

I analyzed the compared movie runtime with TMDB rating to see whether longer movies tend to receive higher or lower ratings. In the runtime_vs_tmdb_rating.png, it showed that most movies runtime is more than 100 minutes. Surprisingly, the run time over 200 minutes had good ratings.

### 2. Genre Analysis

The most common genre in the dataset wwas Drama, followed by Action, Thriller, Adventure, and Comedy. 

The average ratings across all genres were above 7.

### 3. Financial Analysis

Movies with larger budgets often generated higher revenue, showing a positive relationship between spending and earnings.


### 4. Temporal Analysis

Movie release years varied across the dataset. The year 2026 had noticeably more popular and top-rated movies represented. This is likely because the dataset was collected from TMDB’s popular and top-rated endpoints, which tend to feature newer and recently trending releases more often than older films.


## Interesting insights or patterns

The most interesting insight was reviewing the budgets for movies. The data anlysis showed that newer movies had a significant increase in budget than older ones. It makes me question, how many external factors affect movie budgets now or is it due to the inflation within the movie industry. To build upon this, higher budgets often led to higher revenue, but not always. Some expensive films underperformed compared to other movies.

Longer runtime did not always guarantee better ratings.


## Challenges encountered and solutions 

The first issue that I found with this assignment was including shows in the api_collector.py. I had to delete it from my code since LetterBoxd does not collect show data. 

The second issue I found was the need to increase the number of movie samples. LetterBoxd does not have most of the recent movies that TMDB had whether it was recently released or not yet released. The issue was detected when analyzing the csv file. Half of the data in the csv file had null information from LetterBoxd. When I encoutered this issue, I incorporated the popular movies and top rated movies in the api_collector.py, ensuring there was no repeated titles. I reran the code and it helped produced a csv file that I could do a proper data analysis on. 

The third issue I found was matching movie titles between TMDB and Letterboxd and handling missing financial data in the csv. I had to turn to ChatGPT for helpful insights on how to clean and analyze the data properly. 

The fourth issue I encountered was TMDB uses a 0-10 scale and Letterboxd uses a 0-5 scale. So I had to scale the rating appropriately by multiplying by 2. 

## Limitations and future impovements

One limitation I found was that most of the unreleased and recently released movies on TMDB are not on LetterBoxd. Only 100 movies were collected, the analysis could have more reliable insights. For the future, collecting a larger sample size would be more beneficial.  




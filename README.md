This assignment collects data for 50 movies.  The data comes from the TMDB API and scraping the Letterboxd site.  The goal of this assignment is to use APIs and scraping to get data for data analysis.

To set up the environment, I used a uv virtual environment for faster processing.  Additionally, I created an environment file for my API keys.

Run the run_pipeline.py script in folder, make sure that the virtual environment is recognized.

The code requires requests, beautifulsoup4, lxml
pandas, python-dotenv, matplotlib, seaborn, jsonschema, and urllib3.

The data comes from the TMDB API and web scraping the Letterboxd site.  The code uses and API key to acess the TMDB API and implements rate limiting to adhere to the site's requirements.  Similarly, the web scraping code checks the robots.txt and implements rate limiting to adhere to the ethics of web scraping.  Thus, if the two sites change their policies, the site may not work anymore.  Another limitation is the code struggled with foreign titles, so the code uses their English names.
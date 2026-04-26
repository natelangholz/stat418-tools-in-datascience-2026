"""Run the full data collection and analysis pipeline."""
import json
import os

from api_collector import TMDBCollector
from web_scraper import LetterboxdScraper
from data_processor import load_raw_data, merge_data, clean_data, save_processed_data

def main():
    os.makedirs('logs', exist_ok=True)

    print("=== Step 1: Collecting TMDB data ===")
    collector = TMDBCollector()
    collector.collect_all_data(num_items=50)

    print("\n=== Step 2: Scraping Letterboxd ===")
    with open('data/raw/tmdb/movies.json') as f:
        movies = json.load(f)
    scraper = LetterboxdScraper(delay=2.0)
    scraper.check_robots_txt()
    results = scraper.scrape_multiple_movies(movies)
    os.makedirs('data/raw/letterboxd', exist_ok=True)
    with open('data/raw/letterboxd/ratings.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n=== Step 3: Processing data ===")
    tmdb_data, letterboxd_data = load_raw_data()
    df = merge_data(tmdb_data, letterboxd_data)
    df = clean_data(df)
    save_processed_data(df, 'data/processed')

    print("\n=== Step 4: Running analysis ===")
    import analyze_data

    print("\nPipeline complete!")

if __name__ == '__main__':
    main()

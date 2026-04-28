# run_pipeline.py
import logging
from api_collector import collect_all_data
from web_scraper import scrape_multiple_movies
from data_processor import load_raw_data, merge_data, clean_data, save_processed_data

# Set up logging to logs/pipeline.log
logging.basicConfig(filename='logs/pipeline.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting pipeline execution")
    
    # 1. Collect API Data
    tmdb_data = collect_all_data(50)
    
    # 2. Scrape Letterboxd
    lb_data = scrape_multiple_movies(tmdb_data)
    
    # 3. Process & Merge
    raw_tmdb, raw_lb = load_raw_data()
    merged = merge_data(raw_tmdb, raw_lb)
    final_df = clean_data(merged)
    save_processed_data(final_df)
    
    logging.info("Pipeline completed successfully")

if __name__ == "__main__":
    main()
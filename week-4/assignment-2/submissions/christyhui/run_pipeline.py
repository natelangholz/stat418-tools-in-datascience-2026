import json
import logging
from pathlib import Path
from datetime import datetime

# Import all pipeline steps
from api_collector import collect_all_data, save_data as save_tmdb_data
from web_scraper import scrape_multiple_movies, save_data as save_letterboxd_data
from data_processor import load_raw_data, merge_data, clean_data, save_processed_data
from analyze_data import (
    load_processed_data,
    analyze_rating_correlation,
    analyze_genres,
    analyze_financials,
    analyze_temporal,
    generate_summary_report,
)

# ── Directory setup ───────────────────────────────────────────────────────────

Path("logs").mkdir(exist_ok=True)

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(num_movies: int = 50) -> None:
    """
    Run the full movie data collection and analysis pipeline.

    Steps:
        1. Collect movie data from TMDB API
        2. Scrape ratings and fan counts from Letterboxd
        3. Merge, clean, and save processed data
        4. Run all analyses and generate visualizations

    Args:
        num_movies: Number of movies to collect (default 50).
    """
    start_time = datetime.now()
    logger.info(f"Pipeline started at {start_time.isoformat()}")
    print("=" * 60)
    print("  MOVIE DATA PIPELINE")
    print(f"  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── Step 1: TMDB API ──────────────────────────────────────────────────────
    print("\n[Step 1/4] Collecting data from TMDB API...")
    logger.info("Step 1: TMDB API collection.")
    try:
        tmdb_data = collect_all_data(num_items=num_movies)
        save_tmdb_data(tmdb_data, filename="tmdb_raw.json")
        logger.info(f"Step 1 complete. {len(tmdb_data)} movies collected.")
    except Exception as e:
        logger.error(f"Step 1 failed: {e}")
        print(f"[Pipeline] ERROR in Step 1: {e}")
        raise

    # ── Step 2: Letterboxd scraping ───────────────────────────────────────────
    print("\n[Step 2/4] Scraping Letterboxd...")
    logger.info("Step 2: Letterboxd scraping.")
    try:
        letterboxd_data = scrape_multiple_movies(tmdb_data)
        save_letterboxd_data(letterboxd_data, filename="letterboxd_raw.json")
        logger.info(f"Step 2 complete. {len(letterboxd_data)} movies scraped.")
    except Exception as e:
        logger.error(f"Step 2 failed: {e}")
        print(f"[Pipeline] ERROR in Step 2: {e}")
        raise

    # ── Step 3: Data processing ───────────────────────────────────────────────
    print("\n[Step 3/4] Processing and merging data...")
    logger.info("Step 3: Data processing.")
    try:
        tmdb_raw, letterboxd_raw = load_raw_data()
        merged = merge_data(tmdb_raw, letterboxd_raw)
        cleaned = clean_data(merged)
        save_processed_data(cleaned)
        logger.info(f"Step 3 complete. {len(cleaned)} movies in final dataset.")
    except Exception as e:
        logger.error(f"Step 3 failed: {e}")
        print(f"[Pipeline] ERROR in Step 3: {e}")
        raise

    # ── Step 4: Analysis ──────────────────────────────────────────────────────
    print("\n[Step 4/4] Running analysis and generating visualizations...")
    logger.info("Step 4: Analysis.")
    try:
        df = load_processed_data()
        analyze_rating_correlation(df)
        analyze_genres(df)
        analyze_financials(df)
        analyze_temporal(df)
        generate_summary_report(df)
        logger.info("Step 4 complete.")
    except Exception as e:
        logger.error(f"Step 4 failed: {e}")
        print(f"[Pipeline] ERROR in Step 4: {e}")
        raise

    # ── Done ──────────────────────────────────────────────────────────────────
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    logger.info(f"Pipeline completed in {duration}s.")
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print(f"  Movies collected:   {len(tmdb_data)}")
    print(f"  Movies in dataset:  {len(cleaned)}")
    print(f"  Duration:           {duration}s")
    print(f"  Finished:           {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("\nOutputs:")
    print("  data/raw/tmdb/tmdb_raw.json")
    print("  data/raw/letterboxd/letterboxd_raw.json")
    print("  data/processed/movies_processed.csv")
    print("  data/processed/movies_processed.json")
    print("  data/analysis/*.png")
    print("  data/analysis/summary_report.txt")
    print("  logs/pipeline.log")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_pipeline(num_movies=50)
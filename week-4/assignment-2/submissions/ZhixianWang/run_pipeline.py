"""
Full pipeline orchestrator.

Usage:
    python run_pipeline.py            # run all stages
    python run_pipeline.py --skip-collect  # skip API/scrape, reuse raw data
"""

import argparse
import logging
import os
import time

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _step(name: str) -> None:
    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    logger.info("Starting stage: %s", name)


def run_collection() -> None:
    _step("Stage 1 — TMDB API Collection")
    from api_collector import main as collect_tmdb
    collect_tmdb()
    logger.info("Stage 1 complete")


def run_scraping() -> None:
    _step("Stage 2 — IMDb / OMDb Data Fetch")
    from web_scraper import main as scrape_imdb
    scrape_imdb()
    logger.info("Stage 2 complete")


def run_processing():
    _step("Stage 3 — Data Processing & Merge")
    from data_processor import main as process
    df = process()
    logger.info("Stage 3 complete")
    return df


def run_analysis() -> None:
    _step("Stage 4 — Analysis & Visualizations")
    from analyze_data import main as analyse
    analyse()
    logger.info("Stage 4 complete")


def main() -> None:
    parser = argparse.ArgumentParser(description="Movie data pipeline")
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Skip API/scrape stages and reuse existing raw data",
    )
    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    start = time.time()
    logger.info("Pipeline started")

    if not args.skip_collect:
        run_collection()
        run_scraping()
    else:
        print("Skipping collection stages — using existing raw data.")

    run_processing()
    run_analysis()

    elapsed = time.time() - start
    _step(f"Pipeline complete in {elapsed:.1f}s")
    logger.info("Pipeline finished in %.1fs", elapsed)


if __name__ == "__main__":
    main()

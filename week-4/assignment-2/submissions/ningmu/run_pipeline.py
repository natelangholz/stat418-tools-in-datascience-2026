"""
run_pipeline.py
===============
End-to-end driver: collect -> scrape -> process -> analyze.

Usage
-----
    python run_pipeline.py [num_items]

`num_items` defaults to 50, which satisfies the assignment requirement.
You can pass a smaller number while iterating.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("run_pipeline")


def main() -> None:
    num_items = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    # ------------------------------------------------------------------
    # 1. TMDB collection
    # ------------------------------------------------------------------
    from api_collector import TMDBCollector

    log.info("=" * 60)
    log.info("Step 1/4: Collecting %d movies from TMDB", num_items)
    log.info("=" * 60)
    collector = TMDBCollector()
    tmdb_items = collector.collect_all_data(num_items=num_items)
    log.info("TMDB collected %d records", len(tmdb_items))

    # ------------------------------------------------------------------
    # 2. Letterboxd scraping
    # ------------------------------------------------------------------
    from web_scraper import LetterboxdScraper

    log.info("=" * 60)
    log.info("Step 2/4: Scraping Letterboxd for %d movies", len(tmdb_items))
    log.info("=" * 60)
    scraper = LetterboxdScraper(delay=2.0)
    inputs = [
        {
            "title": m.get("title") or m.get("original_title"),
            "release_date": m.get("release_date"),
        }
        for m in tmdb_items
    ]
    lb_items = scraper.scrape_multiple_movies(inputs)
    log.info(
        "Letterboxd scraped %d records (%d successful)",
        len(lb_items),
        sum(1 for r in lb_items if r.get("scraped_successfully")),
    )

    # ------------------------------------------------------------------
    # 3. Processing / merging
    # ------------------------------------------------------------------
    from data_processor import (
        clean_data,
        load_raw_data,
        merge_data,
        save_processed_data,
    )

    log.info("=" * 60)
    log.info("Step 3/4: Merging and cleaning")
    log.info("=" * 60)
    tmdb_raw, lb_raw = load_raw_data()
    merged = merge_data(tmdb_raw, lb_raw)
    cleaned = clean_data(merged)
    save_processed_data(cleaned)
    log.info("Processed %d rows", len(cleaned))

    # ------------------------------------------------------------------
    # 4. Analysis
    # ------------------------------------------------------------------
    import analyze_data

    log.info("=" * 60)
    log.info("Step 4/4: Analysis")
    log.info("=" * 60)
    analyze_data.main()
    log.info("Pipeline complete.")


if __name__ == "__main__":
    main()

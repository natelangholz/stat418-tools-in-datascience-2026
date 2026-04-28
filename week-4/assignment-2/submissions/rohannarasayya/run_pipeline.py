"""
run_pipeline.py
---------------
Orchestrates the full movie data pipeline in four sequential steps:

  1. api_collector  — fetch TMDB data
  2. web_scraper    — scrape Letterboxd pages
  3. data_processor — merge and clean
  4. analyze_data   — produce visualisations and report

Logs pipeline start/end times and step durations to logs/pipeline.log.
Exits with a non-zero code if any step fails.
"""

import logging
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("pipeline")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _run_step(name: str, fn, *args, **kwargs):
    """
    Execute a pipeline step, logging duration and re-raising on failure.

    Parameters
    ----------
    name : str
        Human-readable step name for log messages.
    fn : callable
        Function to call.
    *args, **kwargs
        Passed through to *fn*.

    Returns
    -------
    any
        Return value of *fn*.

    Raises
    ------
    Exception
        Re-raises any exception from *fn* after logging it.
    """
    logger.info("[%s] Starting…", name)
    print(f"\n[Pipeline] Step: {name}")
    t0 = time.time()
    try:
        result = fn(*args, **kwargs)
        elapsed = time.time() - t0
        logger.info("[%s] Completed in %.1fs", name, elapsed)
        print(f"[Pipeline] {name} finished in {elapsed:.1f}s")
        return result
    except Exception as exc:
        elapsed = time.time() - t0
        logger.error("[%s] FAILED after %.1fs: %s", name, elapsed, exc)
        print(f"[Pipeline] ERROR in {name}: {exc}")
        raise


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def main() -> None:
    """Run all four pipeline steps in order and log overall duration."""
    pipeline_start = time.time()
    logger.info("=" * 60)
    logger.info("Pipeline starting")
    print("[Pipeline] Starting full movie data pipeline")

    # ------------------------------------------------------------------
    # Step 1: Collect TMDB data
    # ------------------------------------------------------------------
    try:
        from api_collector import collect_all_data
        movies = _run_step("api_collector", collect_all_data, num_items=60)
    except Exception as exc:
        logger.critical("Pipeline aborted at api_collector: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 2: Scrape Letterboxd data
    # ------------------------------------------------------------------
    try:
        from web_scraper import check_robots_txt, scrape_multiple_movies

        if not check_robots_txt():
            logger.error("robots.txt disallows scraping -- skipping web_scraper step")
            print("[Pipeline] robots.txt disallows scraping -- skipping Letterboxd step")
        else:
            _run_step("web_scraper", scrape_multiple_movies, movies)
    except Exception as exc:
        logger.critical("Pipeline aborted at web_scraper: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 3: Merge and clean data
    # ------------------------------------------------------------------
    try:
        from data_processor import (
            clean_data,
            load_raw_data,
            merge_data,
            save_processed_data,
        )

        def run_processor():
            tmdb_data, letterboxd_data = load_raw_data()
            merged = merge_data(tmdb_data, letterboxd_data)
            cleaned = clean_data(merged)
            save_processed_data(cleaned, "data/processed")
            return cleaned

        cleaned_df = _run_step("data_processor", run_processor)
    except Exception as exc:
        logger.critical("Pipeline aborted at data_processor: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 4: Analyse and produce outputs
    # ------------------------------------------------------------------
    try:
        from analyze_data import generate_report, load_processed_data

        def run_analysis():
            df = load_processed_data()
            generate_report(df, "data/analysis")

        _run_step("analyze_data", run_analysis)
    except Exception as exc:
        logger.critical("Pipeline aborted at analyze_data: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    total = time.time() - pipeline_start
    logger.info("Pipeline completed successfully in %.1fs", total)
    logger.info("=" * 60)
    print(f"\n[Pipeline] All steps completed successfully in {total:.1f}s")


if __name__ == "__main__":
    main()

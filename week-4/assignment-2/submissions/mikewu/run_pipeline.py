"""Run the full pipeline: TMDB collection, IMDb scrape, merge, analyze."""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "logs" / "pipeline.log"
PROCESSED = BASE_DIR / "data" / "processed"
RAW_TMDB = BASE_DIR / "data" / "raw" / "tmdb"
RAW_IMDB = BASE_DIR / "data" / "raw" / "imdb"

logger = logging.getLogger("run_pipeline")
_fmt = logging.Formatter("%(asctime)sZ - %(name)s - %(levelname)s - %(message)s")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
if not logger.handlers:
    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fh.setFormatter(_fmt)
    _sh = logging.StreamHandler()
    _sh.setFormatter(_fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(_fh)
    logger.addHandler(_sh)
    logger.propagate = False


def _imdb_ids_from_tmdb_raw() -> List[str]:
    import json

    out: List[str] = []
    for p in sorted(RAW_TMDB.glob("movie_*.json")):
        with p.open(encoding="utf-8") as f:
            d = json.load(f)
        i = d.get("imdb_id")
        if i:
            out.append(str(i))
    return out


def main() -> int:
    load_dotenv(BASE_DIR / ".env.example")
    p = argparse.ArgumentParser(description="Movie data pipeline (TMDB + IMDb)")
    p.add_argument("--num", type=int, default=50, help="Number of popular movies to collect (TMDB only)")
    p.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip IMDb HTTP step; use existing data/raw/imdb JSON if present",
    )
    p.add_argument(
        "--skip-tmdb",
        action="store_true",
        help="Do not call TMDB; use existing data/raw/tmdb from a prior run",
    )
    args = p.parse_args()

    if not args.skip_tmdb:
        if os.getenv("TMDB_API_KEY", "").strip():
            from api_collector import collect_all_data

            logger.info("Collecting up to %s movies from TMDB", args.num)
            try:
                collect_all_data(num_items=args.num)
            except Exception as e:
                logger.error("TMDB collection failed: %s", e)
                return 1
        else:
            logger.error("No TMDB_API_KEY. Set it in .env.example, or use --skip-tmdb")
            return 1
    else:
        logger.info("Using existing TMDB data under data/raw/tmdb/ (--skip-tmdb)")

    if not args.skip_scrape:
        from web_scraper import check_robots_txt, scrape_multiple_movies

        if not check_robots_txt():
            logger.warning("robots.txt can_fetch is False; continuing only for class exercise; respect site ToS in production")
        ids = _imdb_ids_from_tmdb_raw()
        if not ids:
            logger.error("No IMDb ids in %s; cannot scrape", RAW_TMDB)
            return 1
        # Live scrape is slow: same num items as tmdb
        id_list = ids[: max(1, int(args.num))]
        logger.info("Scraping %s IMDb title pages (>=2s between requests)", len(id_list))
        scrape_multiple_movies(id_list)

    if args.skip_scrape and not any(RAW_IMDB.glob("tt*.json")):
        logger.error("--skip-scrape but no IMDb JSON; run scrape once first")
        return 1

    from analyze_data import run_from_processed
    from data_processor import clean_data, load_raw_data, merge_data, save_processed_data

    tmdb, imdb = load_raw_data()
    if not tmdb:
        logger.error("No TMDB json in %s", RAW_TMDB)
        return 1
    m = merge_data(tmdb, imdb)
    m = clean_data(m)
    save_processed_data(m, str(PROCESSED))
    run_from_processed(PROCESSED / "movies_merged.csv")
    logger.info("Done. Merged: %s / analysis under data/analysis /", PROCESSED / "movies_merged.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

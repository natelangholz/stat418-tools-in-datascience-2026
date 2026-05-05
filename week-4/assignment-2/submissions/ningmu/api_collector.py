"""
api_collector.py
================
TMDB API client for STAT 418 Homework 2.

Responsibilities
----------------
- Authenticate with TMDB using a key stored in `.env`
- Fetch popular movies and per-movie details (incl. credits)
- Honor TMDB's rate limit (40 requests / 10 s) with conservative throttling
- Retry transient HTTP errors with exponential backoff
- Save raw JSON responses to `data/raw/tmdb/`
- Log all API activity to `logs/pipeline.log`

The class is built so the rest of the pipeline can call:
    collector = TMDBCollector()
    items = collector.collect_all_data(num_items=50)
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Module-level setup
# ---------------------------------------------------------------------------

load_dotenv()  # populate TMDB_API_KEY from `.env` if present

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
RAW_DIR = BASE_DIR / "data" / "raw" / "tmdb"
LOG_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Configure a module-level logger that writes to logs/pipeline.log.
# We intentionally use `force=True`-style by attaching a file handler
# only once to avoid duplicate lines when run_pipeline imports us.
logger = logging.getLogger("api_collector")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)


class TMDBCollector:
    """A small wrapper around the TMDB v3 REST API.

    Parameters
    ----------
    api_key:
        TMDB v3 API key. Falls back to env var `TMDB_API_KEY`.
    min_request_interval:
        Minimum seconds between two outbound HTTP requests. TMDB allows
        40 requests per 10 seconds, i.e. ~4 RPS. We default to 0.3 s
        (~3.3 RPS) to leave a comfortable buffer.
    max_retries:
        Number of retries for transient errors (5xx / 429 / connection).
    """

    POPULAR_ENDPOINT = "movie/popular"

    def __init__(
        self,
        api_key: Optional[str] = None,
        min_request_interval: float = 0.3,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "TMDB_API_KEY is not set. Put it in a `.env` file or pass it in."
            )

        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.min_request_interval = min_request_interval
        self.max_retries = max_retries
        self._last_request_time = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _rate_limit(self) -> None:
        """Sleep just long enough to respect `min_request_interval`."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Perform a GET request with rate-limiting and retry/backoff.

        Raises
        ------
        requests.RequestException
            If all retries are exhausted.
        """
        params = dict(params or {})
        params["api_key"] = self.api_key
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            self._rate_limit()
            try:
                response = self.session.get(url, params=params, timeout=15)
                # 429 = rate limited; honor Retry-After if present
                if response.status_code == 429:
                    wait = float(response.headers.get("Retry-After", 2))
                    logger.warning(
                        "429 from %s, sleeping %.1fs before retry %d/%d",
                        endpoint,
                        wait,
                        attempt,
                        self.max_retries,
                    )
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                logger.info("GET %s -> 200", endpoint)
                return response.json()
            except requests.RequestException as exc:
                last_exc = exc
                backoff = 2 ** (attempt - 1)
                logger.warning(
                    "GET %s failed (%s); retry %d/%d in %ds",
                    endpoint,
                    exc,
                    attempt,
                    self.max_retries,
                    backoff,
                )
                time.sleep(backoff)

        logger.error("GET %s failed after %d attempts", endpoint, self.max_retries)
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _save_json(payload: Dict, path: Path) -> None:
        """Persist a JSON payload to disk (UTF-8, indented)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Return the `results` array from /movie/popular for one page (~20)."""
        data = self._make_request(self.POPULAR_ENDPOINT, {"page": page})
        return data.get("results", [])

    def get_movie_details(self, movie_id: int) -> Dict:
        """Detailed movie record (genres, runtime, budget, revenue, etc.)."""
        return self._make_request(f"movie/{movie_id}")

    def get_movie_credits(self, movie_id: int) -> Dict:
        """Cast and crew for a given movie."""
        return self._make_request(f"movie/{movie_id}/credits")

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------
    def collect_all_data(self, num_items: int = 50) -> List[Dict]:
        """Collect at least `num_items` enriched movie records.

        For each movie we merge `/movie/{id}` + `/movie/{id}/credits` into
        a single dict and persist the raw JSON to `data/raw/tmdb/<id>.json`.

        Returns
        -------
        list of dict
            Enriched per-movie records.
        """
        logger.info("Starting collect_all_data(num_items=%d)", num_items)
        collected: List[Dict] = []
        page = 1
        seen_ids: set = set()

        while len(collected) < num_items and page <= 10:  # safety cap
            try:
                popular = self.get_popular_movies(page=page)
            except requests.RequestException:
                logger.exception("Could not fetch page %d", page)
                break

            if not popular:
                logger.info("No more results on page %d; stopping.", page)
                break

            for stub in popular:
                if len(collected) >= num_items:
                    break

                movie_id = stub.get("id")
                if movie_id is None or movie_id in seen_ids:
                    continue
                seen_ids.add(movie_id)

                try:
                    details = self.get_movie_details(movie_id)
                    credits = self.get_movie_credits(movie_id)
                except requests.RequestException:
                    logger.exception("Skipping movie_id=%s", movie_id)
                    continue

                enriched = {
                    **details,
                    "cast": credits.get("cast", [])[:5],
                    "crew_top": [
                        c for c in credits.get("crew", [])
                        if c.get("job") in {"Director", "Writer", "Producer"}
                    ][:5],
                }

                # Persist the raw record
                self._save_json(enriched, RAW_DIR / f"{movie_id}.json")
                collected.append(enriched)

            page += 1

        # Also dump a single combined file for convenience
        self._save_json(
            {"count": len(collected), "items": collected},
            RAW_DIR / "_all_movies.json",
        )
        logger.info("collect_all_data finished: %d items", len(collected))
        return collected


# ---------------------------------------------------------------------------
# CLI entry point: `python api_collector.py [num_items]`
# ---------------------------------------------------------------------------
def main() -> None:
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    collector = TMDBCollector()
    items = collector.collect_all_data(num_items=n)
    print(f"Collected {len(items)} movies. Raw JSON in {RAW_DIR}.")


if __name__ == "__main__":
    main()

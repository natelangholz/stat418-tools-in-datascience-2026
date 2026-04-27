"""
TMDB API collector with rate limiting, retries, and raw JSON output.
"""
from __future__ import annotations

import json
import logging
import os
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "logs" / "pipeline.log"
RAW_TMDB = BASE_DIR / "data" / "raw" / "tmdb"

# TMDB: 40 requests / 10 seconds
MAX_RPM_WINDOW = 40
WINDOW_SECONDS = 10.0
MAX_RETRIES = 4
BACKOFF_BASE = 1.5

logger = logging.getLogger("tmdb")


def _setup_logger() -> None:
    if getattr(_setup_logger, "_done", False):
        return
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _fmt = logging.Formatter("%(asctime)sZ - %(name)s - %(levelname)s - %(message)s")
    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fh.setFormatter(_fmt)
    _fh.setLevel(logging.INFO)
    _sh = logging.StreamHandler()
    _sh.setFormatter(_fmt)
    _sh.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
    logger.addHandler(_fh)
    logger.addHandler(_sh)
    logger.propagate = False
    _setup_logger._done = True  # type: ignore[attr-defined]


_setup_logger()


class SlidingWindowRateLimiter:
    """Allow at most `max_calls` in each rolling `per_seconds` window."""

    def __init__(self, max_calls: int, per_seconds: float) -> None:
        self._max = max_calls
        self._window = per_seconds
        self._ts: deque[float] = deque()

    def wait(self) -> None:
        now = time.time()
        while self._ts and self._ts[0] < now - self._window:
            self._ts.popleft()
        if len(self._ts) >= self._max:
            wait_s = self._window - (now - self._ts[0]) + 0.05
            if wait_s > 0:
                time.sleep(wait_s)
                now = time.time()
        while self._ts and self._ts[0] < now - self._window:
            self._ts.popleft()
        self._ts.append(time.time())


class TMDBCollector:
    """
    Fetches popular movies, details, and credits; saves one JSON per movie
    under ``data/raw/tmdb/``.
    """

    def __init__(self) -> None:
        load_dotenv(BASE_DIR / ".env.example")
        self.api_key = os.getenv("TMDB_API_KEY", "").strip()
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.limiter = SlidingWindowRateLimiter(MAX_RPM_WINDOW, WINDOW_SECONDS)
        if not self.api_key:
            logger.warning("TMDB_API_KEY is not set; set it in .env.example to collect from the API")

    def _rate_limit(self) -> None:
        """Ensure TMDB requests stay under assignment rate limits."""
        self.limiter.wait()

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Template-style request helper with retries and logging."""
        return self._request_json("GET", endpoint, params=params or {})

    def _request_json(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("TMDB_API_KEY is required for live API collection")
        url = f"{self.base_url}/{path.strip('/')}"
        params = dict(kwargs.get("params") or {})
        params["api_key"] = self.api_key
        rest = {k: v for k, v in kwargs.items() if k != "params"}
        last: Optional[Exception] = None
        for attempt in range(1, MAX_RETRIES + 1):
            self._rate_limit()
            t0 = datetime.now(timezone.utc)
            try:
                r = self.session.request(method, url, params=params, timeout=20, **rest)
                logger.info("API %s %s status=%s t=%s", method, path, r.status_code, t0.isoformat().replace("+00:00", "Z"))
                if r.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                    delay = BACKOFF_BASE ** (attempt - 1)
                    logger.warning("HTTP %s, backing off %.2fs (attempt %s)", r.status_code, delay, attempt)
                    time.sleep(delay)
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.RequestException, ValueError) as e:
                last = e
                if attempt < MAX_RETRIES:
                    delay = BACKOFF_BASE ** (attempt - 1)
                    logger.warning("Request error %s, retry in %.2fs", e, delay)
                    time.sleep(delay)
        assert last is not None
        logger.error("Request failed for %s: %s", path, last)
        raise last

    def get_popular_movies(self, page: int = 1) -> List[Dict[str, Any]]:
        """Return one page of popular-movie result rows."""
        data = self._make_request("movie/popular", {"page": max(1, int(page))})
        return data.get("results", [])

    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Return movie detail payload (includes budget, revenue, etc.)."""
        return self._make_request(f"movie/{int(movie_id)}")

    def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """Return cast/crew for a movie."""
        return self._make_request(f"movie/{int(movie_id)}/credits")

    def get_external_ids(self, movie_id: int) -> Dict[str, Any]:
        """IMDb and other external IDs for a title."""
        return self._make_request(f"movie/{int(movie_id)}/external_ids")

    @staticmethod
    def _build_record(details: Dict[str, Any], credits: Dict[str, Any], imdb_id: str) -> Dict[str, Any]:
        cast = sorted(credits.get("cast", []), key=lambda c: c.get("order", 99))[:5]
        crew_src = credits.get("crew", [])
        priority = ("Director", "Writer", "Producer", "Editor", "Director of Photography")
        crew: List[Dict[str, Any]] = []
        seen: set = set()
        for job in priority:
            for m in crew_src:
                if m.get("job") == job and m.get("id") and m.get("id") not in seen:
                    crew.append(m)
                    seen.add(m.get("id"))
                if len(crew) >= 5:
                    break
            if len(crew) >= 5:
                break
        if len(crew) < 5:
            for m in crew_src:
                if m.get("id") in seen:
                    continue
                crew.append(m)
                seen.add(m.get("id"))
                if len(crew) >= 5:
                    break
        return {
            "tmdb_id": details.get("id"),
            "imdb_id": imdb_id or None,
            "title": details.get("title") or details.get("original_title"),
            "release_date": details.get("release_date"),
            "runtime": details.get("runtime"),
            "genres": [g.get("name") for g in details.get("genres", []) if g.get("name")],
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "tmdb_vote_average": details.get("vote_average"),
            "tmdb_vote_count": details.get("vote_count"),
            "original_language": details.get("original_language"),
            "production_companies": [c.get("name") for c in details.get("production_companies", []) if c.get("name")],
            "cast": [{"name": c.get("name"), "character": c.get("character"), "order": c.get("order")} for c in cast],
            "crew": [{"name": c.get("name"), "job": c.get("job")} for c in crew],
            "fetched_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

    def _save_one(self, record: Dict[str, Any]) -> None:
        RAW_TMDB.mkdir(parents=True, exist_ok=True)
        mid = record.get("tmdb_id")
        p = RAW_TMDB / f"movie_{mid}.json"
        with p.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        logger.info("Saved raw record to %s", p)

    @staticmethod
    def _normalize_imdb(imdb: Optional[str]) -> Optional[str]:
        if not imdb:
            return None
        s = str(imdb).strip()
        if not s.startswith("tt"):
            return f"tt{s.lstrip()}"
        return s

    def collect_all_data(self, num_items: int = 50) -> List[Dict[str, Any]]:
        """
        Walk ``movie/popular`` pages, fetch details, credits, and external_ids,
        merge, save JSON per item, and return the list of merged records.
        """
        if not self.api_key:
            raise ValueError("Set TMDB_API_KEY in .env.example in this directory")
        out: List[Dict[str, Any]] = []
        page = 1
        while len(out) < num_items:
            batch = self.get_popular_movies(page)
            if not batch:
                logger.warning("No more popular movies on page %s; stopping with %s items", page, len(out))
                break
            for row in batch:
                if len(out) >= num_items:
                    break
                mid = int(row["id"])
                d = self.get_movie_details(mid)
                c = self.get_movie_credits(mid)
                ex = self.get_external_ids(mid)
                imdb = self._normalize_imdb(ex.get("imdb_id") or d.get("imdb_id"))
                rec = self._build_record(d, c, imdb or "")
                if not imdb:
                    logger.warning("No IMDb id for TMDB %s; record kept for TMDb-only use", mid)
                self._save_one(rec)
                out.append(rec)
            page += 1
        return out


def get_popular_movies(page: int = 1) -> List[Dict[str, Any]]:
    """Get popular-movie result rows (see :meth:`TMDBCollector.get_popular_movies`)."""
    return TMDBCollector().get_popular_movies(page=page)


def get_movie_details(movie_id: int) -> Dict[str, Any]:
    """Get TMDB details for a movie id."""
    return TMDBCollector().get_movie_details(movie_id)


def get_movie_credits(movie_id: int) -> Dict[str, Any]:
    """Get cast/crew for a movie id."""
    return TMDBCollector().get_movie_credits(movie_id)


def collect_all_data(num_items: int = 50) -> List[Dict[str, Any]]:
    """
    Collect popular movies with merged details and credits, save raw JSON
    in ``data/raw/tmdb/``.
    """
    return TMDBCollector().collect_all_data(num_items=num_items)

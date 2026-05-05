"""
IMDb page scraper with robots.txt check, rate limiting, and JSON output.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import robotparser

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "logs" / "pipeline.log"
RAW_IMDB = BASE_DIR / "data" / "raw" / "imdb"
IMDB_BASE = "https://www.imdb.com"
ROBOTS_URL = f"{IMDB_BASE}/robots.txt"
SCRAPE_DELAY = 2.0

logger = logging.getLogger("imdb_scraper")


def _setup_scraper_log() -> None:
    if getattr(_setup_scraper_log, "_done", False):
        return
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        _fmt = logging.Formatter("%(asctime)sZ - %(name)s - %(levelname)s - %(message)s")
        _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        _fh.setFormatter(_fmt)
        _sh = logging.StreamHandler()
        _sh.setFormatter(_fmt)
        logger.setLevel(logging.INFO)
        logger.addHandler(_fh)
        logger.addHandler(_sh)
        logger.propagate = False
    _setup_scraper_log._done = True  # type: ignore[attr-defined]


_setup_scraper_log()


def _user_agent() -> str:
    load_dotenv(BASE_DIR / ".env.example")
    email = os.getenv("SCRAPER_EMAIL", "your.email@ucla.edu").strip()
    return f"UCLA STAT418 Student - {email}"


def _norm_imdb_id(imdb_id: str) -> str:
    s = imdb_id.strip()
    if s.lower().startswith("tt"):
        return s[:2] + s[2:].lstrip() or s
    return f"tt{s.lstrip()}"


def _parse_json_ld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            for x in data:
                if isinstance(x, dict):
                    out.append(x)
        elif isinstance(data, dict):
            out.append(data)
    return out


def _parse_next_data(html: str) -> Optional[Dict[str, Any]]:
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _walk_find(obj: Any, key: str) -> List[Any]:
    found: List[Any] = []
    if isinstance(obj, dict):
        if key in obj:
            found.append(obj[key])
        for v in obj.values():
            found.extend(_walk_find(v, key))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(_walk_find(v, key))
    return found


def _float_or_none(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def _int_or_none(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        s = str(x).replace(",", "").strip()
        if not s:
            return None
        return int(float(s))
    except (TypeError, ValueError):
        return None


def _extract_from_ld(movies: List[Dict[str, Any]]) -> Dict[str, Any]:
    rating: Optional[float] = None
    n_reviews: Optional[int] = None
    for m in movies:
        if m.get("@type") in ("Movie", "TVSeries", "TVEpisode", "VideoObject", "TVSeason"):
            ar = m.get("aggregateRating")
            if isinstance(ar, dict):
                rating = _float_or_none(ar.get("ratingValue")) or rating
                n_reviews = _int_or_none(ar.get("ratingCount") or ar.get("reviewCount")) or n_reviews
    return {"rating": rating, "num_reviews": n_reviews}


def _extract_from_next(d: Dict[str, Any]) -> Dict[str, Any]:
    # Heuristic: look for aboveTheFold or titleMainSection ratings
    out: Dict[str, Any] = {"rating": None, "num_reviews": None, "metascore": None}
    for key in ("rating", "imDbRating", "aggregateRating"):
        for v in _walk_find(d, key):
            if isinstance(v, (int, float, str)) and v not in (None, ""):
                f = _float_or_none(v)
                if f is not None and 0 < f <= 10:
                    out["rating"] = f
    for v in _walk_find(d, "userReviewCount"):
        n = _int_or_none(v)
        if n is not None:
            out["num_reviews"] = n
    for v in _walk_find(d, "metascore"):
        f = _float_or_none(v)
        if f is not None and 0 <= f <= 100:
            out["metascore"] = f
    for v in _walk_find(d, "metascoreValue"):
        f = _float_or_none(v)
        if f is not None and 0 <= f <= 100:
            out["metascore"] = f
    return out


def _metascore_from_soup(soup: BeautifulSoup) -> Optional[float]:
    # IMDb sometimes shows a score in a div with "Metascore" label
    for span in soup.find_all("span", string=re.compile("Metascore|Metacritic", re.I)):
        parent = span.find_parent("div")
        for _ in range(4):
            if not parent:
                break
            for s2 in parent.find_all("span", class_=re.compile("sc-")):
                t = s2.get_text(strip=True)
                if t.isdigit() and 0 <= int(t) <= 100:
                    return float(t)
            parent = parent.find_parent("div")
    m = re.search(r"Metascore[^0-9]+(\d{1,3})", soup.get_text(" ", strip=True), re.I)
    if m:
        return _float_or_none(m.group(1))
    return None


def _review_count_from_soup(soup: BeautifulSoup) -> Optional[int]:
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if "title" in h and ("/ratings" in h or "user" in h.lower() and "review" in h.lower()):
            t = a.get_text(strip=True)
            m = re.search(r"([\d,]+)\s*user", t, re.I)
            if m:
                return _int_or_none(m.group(1).replace(",", ""))
    m = re.search(r"([\d,]+)\s*user reviews", soup.get_text(" ", strip=True), re.I)
    if m:
        return _int_or_none(m.group(1).replace(",", ""))
    return None


def _rating_from_soup(soup: BeautifulSoup) -> Optional[float]:
    for meta in soup.find_all("meta", itemprop="ratingValue"):
        return _float_or_none(meta.get("content"))
    m2 = soup.find("div", {"data-testid": "hero-rating-bar__aggregate-rating__rating"})
    if m2:
        return _float_or_none(m2.get_text(strip=True).split("/")[0])
    return None


class IMDbScraper:
    """Template-style IMDb scraper with polite delay and logging."""

    def __init__(self, delay: float = SCRAPE_DELAY) -> None:
        self.delay = max(0.0, delay)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": _user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        self.last_request_time = 0.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def check_robots_txt(self) -> bool:
        """Return True when robots.txt allows fetching a sample title URL."""
        rp = robotparser.RobotFileParser()
        rp.set_url(ROBOTS_URL)
        try:
            rp.read()
        except OSError as e:
            logger.error("Could not read robots.txt: %s", e)
            return False
        test_url = f"{IMDB_BASE}/title/tt0111161/"
        ok = rp.can_fetch(self.session.headers.get("User-Agent", _user_agent()), test_url)
        logger.info("robots.txt: can_fetch(%s) = %s", test_url, ok)
        return bool(ok)

    def _extract_rating(self, soup: BeautifulSoup, html: str) -> Optional[float]:
        ld = _parse_json_ld(soup)
        from_ld = _extract_from_ld(ld) if ld else {}
        nd = _parse_next_data(html)
        from_next = _extract_from_next(nd) if nd else {}
        return from_ld.get("rating") or from_next.get("rating") or _rating_from_soup(soup)

    def _extract_review_count(self, soup: BeautifulSoup, html: str) -> Optional[int]:
        ld = _parse_json_ld(soup)
        from_ld = _extract_from_ld(ld) if ld else {}
        nd = _parse_next_data(html)
        from_next = _extract_from_next(nd) if nd else {}
        return from_ld.get("num_reviews") or from_next.get("num_reviews") or _review_count_from_soup(soup)

    def _extract_metascore(self, soup: BeautifulSoup, html: str) -> Optional[float]:
        nd = _parse_next_data(html)
        from_next = _extract_from_next(nd) if nd else {}
        return from_next.get("metascore") or _metascore_from_soup(soup)

    def scrape_movie_page(self, imdb_id: str) -> Dict[str, Any]:
        """Scrape IMDb title page for rating, review count, and metascore."""
        self._rate_limit()
        iid = _norm_imdb_id(imdb_id)
        url = f"{IMDB_BASE}/title/{iid}/"
        result: Dict[str, Any] = {
            "imdb_id": iid,
            "url": url,
            "scraped_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        try:
            t0 = datetime.now(timezone.utc)
            response = self.session.get(url, timeout=25)
            result["http_status"] = response.status_code
            logger.info("GET %s status=%s t=%s", url, response.status_code, t0.isoformat().replace("+00:00", "Z"))
            if response.status_code != 200 or not response.text or len(response.text) < 5000:
                result["error"] = f"Non-200 or small body: status={response.status_code} len={len(response.text or '')}"
                return result
            soup = BeautifulSoup(response.text, "lxml")
            result["imdb_rating"] = self._extract_rating(soup, response.text)
            result["num_user_reviews"] = self._extract_review_count(soup, response.text)
            result["metascore"] = self._extract_metascore(soup, response.text)
            return result
        except requests.RequestException as e:
            logger.error("Error scraping %s: %s", iid, e)
            return {"imdb_id": iid, "error": str(e)}

    def _save_scrape(self, d: Dict[str, Any]) -> None:
        RAW_IMDB.mkdir(parents=True, exist_ok=True)
        iid = d.get("imdb_id", "unknown")
        p = RAW_IMDB / f"{iid}.json"
        with p.open("w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        logger.info("Saved IMDb scrape to %s", p)

    def scrape_multiple_movies(self, imdb_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch scrape title pages and save one JSON per IMDb id."""
        out: List[Dict[str, Any]] = []
        for iid in imdb_ids:
            one = self.scrape_movie_page(iid)
            self._save_scrape(one)
            out.append(one)
        return out


def check_robots_txt() -> bool:
    return IMDbScraper(delay=SCRAPE_DELAY).check_robots_txt()


def scrape_movie_page(imdb_id: str) -> Dict[str, Any]:
    return IMDbScraper(delay=SCRAPE_DELAY).scrape_movie_page(imdb_id)


def scrape_multiple_movies(imdb_ids: List[str], delay: float = SCRAPE_DELAY) -> List[Dict[str, Any]]:
    return IMDbScraper(delay=delay).scrape_multiple_movies(imdb_ids)

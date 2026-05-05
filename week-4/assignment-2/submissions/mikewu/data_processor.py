"""
Load TMDB and IMDb JSON, merge on IMDb id, clean, and save processed outputs.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "logs" / "pipeline.log"
RAW_TMDB = BASE_DIR / "data" / "raw" / "tmdb"
RAW_IMDB = BASE_DIR / "data" / "raw" / "imdb"
PROCESSED = BASE_DIR / "data" / "processed"

logger = logging.getLogger("data_processor")
if not logger.handlers:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _fmt = logging.Formatter("%(asctime)sZ - %(name)s - %(levelname)s - %(message)s")
    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fh.setFormatter(_fmt)
    _sh = logging.StreamHandler()
    _sh.setFormatter(_fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(_fh)
    logger.addHandler(_sh)
    logger.propagate = False


def load_raw_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Load all ``movie_*.json`` from ``data/raw/tmdb`` and all ``tt*.json`` from
    ``data/raw/imdb``.
    """
    tmdb: List[Dict[str, Any]] = []
    if RAW_TMDB.exists():
        for p in sorted(RAW_TMDB.glob("movie_*.json")):
            with p.open(encoding="utf-8") as f:
                tmdb.append(json.load(f))
    imdb: List[Dict[str, Any]] = []
    if RAW_IMDB.exists():
        for p in sorted(RAW_IMDB.glob("tt*.json")):
            with p.open(encoding="utf-8") as f:
                imdb.append(json.load(f))
    logger.info("Loaded %s TMDB records, %s IMDb scrape records", len(tmdb), len(imdb))
    return tmdb, imdb


def _norm_imdb(s: Optional[str]) -> Optional[str]:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return None
    t = str(s).strip()
    if not t:
        return None
    if not t.startswith("tt"):
        t = f"tt{t.lstrip()}"
    return t


def merge_data(tmdb_data: List[Dict[str, Any]], imdb_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Left-merge TMDB rows with IMDb scrapes on ``imdb_id``."""
    if not tmdb_data:
        return pd.DataFrame()
    tdf = pd.json_normalize(tmdb_data, sep="_")
    tdf["imdb_id"] = tdf["imdb_id"].map(_norm_imdb) if "imdb_id" in tdf.columns else None
    if not imdb_data:
        tdf["imdb_rating"] = None
        tdf["num_user_reviews"] = None
        tdf["metascore"] = None
        return tdf
    idf = pd.json_normalize(imdb_data, sep="_")
    idf["imdb_id"] = idf["imdb_id"].map(_norm_imdb) if "imdb_id" in idf.columns else None
    idf = idf.drop_duplicates(subset=["imdb_id"], keep="last")
    keep = ["imdb_id", "imdb_rating", "num_user_reviews", "metascore", "http_status", "error"]
    cols = [c for c in keep if c in idf.columns]
    idf = idf[cols]
    out = tdf.merge(idf, on="imdb_id", how="left", suffixes=("", "_imdb"))
    return out


def _parse_date(s: Any) -> Optional[pd.Timestamp]:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return None
    t = str(s).strip()
    if not t:
        return None
    try:
        return pd.to_datetime(t, errors="coerce")
    except Exception:
        return None


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """De-duplicate, coerce types, and standardize rating / date columns."""
    if df.empty:
        return df
    d = df.copy()
    if "imdb_id" in d.columns:
        d["imdb_id"] = d["imdb_id"].map(_norm_imdb)
    if "imdb_id" in d.columns:
        d = d.drop_duplicates(subset=["imdb_id"], keep="first")
    else:
        d = d.drop_duplicates()
    for col in ("tmdb_vote_average", "imdb_rating"):
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    for col in ("tmdb_vote_count", "num_user_reviews", "budget", "revenue", "runtime"):
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    if "metascore" in d.columns:
        d["metascore"] = pd.to_numeric(d["metascore"], errors="coerce")
    if "release_date" in d.columns:
        d["release_date_parsed"] = d["release_date"].map(_parse_date)
        d["release_year"] = d["release_date_parsed"].dt.year
    if "genres" in d.columns:

        def _g(x: Any) -> str:
            if isinstance(x, list):
                return "|".join(str(i) for i in x)
            if x is None or (isinstance(x, float) and pd.isna(x)):
                return ""
            return str(x)

        d["genres_str"] = d["genres"].map(_g)
    if "production_companies" in d.columns:

        def _c(x: Any) -> str:
            if isinstance(x, list):
                return "|".join(str(i) for i in x)
            if x is None or (isinstance(x, float) and pd.isna(x)):
                return ""
            return str(x)

        d["production_companies_str"] = d["production_companies"].map(_c)
    if "cast" in d.columns:

        def _cast(x: Any) -> str:
            if not isinstance(x, list):
                return ""
            names = []
            for c in x:
                if isinstance(c, dict) and c.get("name"):
                    names.append(str(c["name"]))
            return "|".join(names)

        d["cast_top5"] = d["cast"].map(_cast)
    if "crew" in d.columns:

        def _crew(x: Any) -> str:
            if not isinstance(x, list):
                return ""
            parts = []
            for c in x:
                if isinstance(c, dict) and c.get("name") and c.get("job"):
                    parts.append(f"{c.get('name')} ({c.get('job')})")
            return "|".join(parts)

        d["crew_top5"] = d["crew"].map(_crew)
    d = d.sort_values(by="tmdb_id", ascending=True) if "tmdb_id" in d.columns else d
    return d


def save_processed_data(df: pd.DataFrame, output_dir: str) -> None:
    """Write ``movies_merged.json`` and ``movies_merged.csv`` under *output_dir*."""
    o = Path(output_dir)
    o.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": o / "movies_merged.json",
        "csv": o / "movies_merged.csv",
    }
    df2 = df.copy()
    for col in list(df2.columns):
        s = df2[col]
        if pd.api.types.is_datetime64tz_dtype(s):
            df2[col] = s.dt.tz_convert("UTC").dt.tz_localize(None)
    for col in list(df2.columns):
        s = df2[col]
        if s.dtype == object and s.map(lambda v: isinstance(v, (list, dict))).any():
            df2[col] = s.map(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
    df2.to_csv(paths["csv"], index=False, encoding="utf-8")
    with paths["json"].open("w", encoding="utf-8") as f:
        f.write(df2.to_json(orient="records", date_format="iso", indent=2, default_handler=str))
    logger.info("Wrote %s and %s", paths["csv"], paths["json"])


def load_merged_table(path: Optional[Path] = None) -> pd.DataFrame:
    p = path or (PROCESSED / "movies_merged.csv")
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)

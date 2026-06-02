"""
AutoRisk data collection — single-file pipeline.

Pulls NHTSA recall + complaint data for every (year, make, model) in scope,
folds trim variants together, and writes one CSV ready for modeling.

Stages
------
  1. For each (year, make), enumerate models from NHTSA's catalog API.
  2. For each (year, make, model), pull recalls + complaints.
  3. Build a row of counts + per-component-category breakdowns.
  4. Merge trim variants into base models (NHTSA complaints API does
     fuzzy match on model names — different trims return identical
     complaints, so MAX-aggregation is the right dedup).
  5. Write data/processed/vehicle_risk_features.csv.

Cache
-----
Every API response is cached as JSON under data/raw/. Re-running picks up
where it left off; --no-cache wipes and rebuilds.

Examples
--------
    # Full collection (default scope, ~60-90 min on first run)
    python src/collect_data.py

    # Pilot (~5 min) — sanity check the pipeline
    python src/collect_data.py --years 2020 2021 --makes Toyota Ford --delay 0.5

    # Force re-fetch (ignore cache)
    python src/collect_data.py --no-cache
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
YEARS_DEFAULT = list(range(2015, 2025))            # 2015–2024 inclusive
MAKES_DEFAULT = [
    "Ford", "Chevrolet", "GMC", "Jeep",            # domestic
    "Toyota", "Honda", "Nissan", "Subaru", "Mazda",  # japanese
    "Hyundai", "Kia",                              # korean
    "Volkswagen",                                  # european
    "Tesla",                                       # ev-only
]

BRAND_CATEGORY = {
    "Ford":       "domestic_ice",
    "Chevrolet":  "domestic_ice",
    "GMC":        "domestic_ice",
    "Jeep":       "domestic_ice",
    "Toyota":     "japanese_ice",
    "Honda":      "japanese_ice",
    "Nissan":     "japanese_ice",
    "Subaru":     "japanese_ice",
    "Mazda":      "japanese_ice",
    "Hyundai":    "korean_ice",
    "Kia":        "korean_ice",
    "Volkswagen": "european_ice",
    "Tesla":      "ev_only",
}

# Component string keyword → coarse category. Order matters: more specific first.
COMPONENT_RULES = [
    ("restraint",  ["AIR BAG", "SEAT BELT"]),
    ("brake",      ["BRAKE"]),
    ("electrical", ["ELECTRICAL", "EXTERIOR LIGHTING", "VISIBILITY", "WIPER"]),
    ("engine",     ["ENGINE"]),
    ("powertrain", ["POWER TRAIN", "POWERTRAIN", "TRANSMISSION", "DRIVETRAIN"]),
    ("fuel",       ["FUEL"]),
    ("steering",   ["STEERING"]),
    ("suspension", ["SUSPENSION", "TIRES", "WHEELS"]),
    ("structure",  ["STRUCTURE", "SEATS", "EXTERIOR"]),
]
CATEGORIES = [c for c, _ in COMPONENT_RULES] + ["other"]

API_BASE   = "https://api.nhtsa.gov"
USER_AGENT = "AutoRisk-StudentProject/1.0 (UCLA STAT 418)"

CACHE_DIR  = Path("data/raw")
OUTPUT_CSV = Path("data/processed/vehicle_risk_features.csv")
CURRENT_YEAR = datetime.now().year

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("autorisk")


# --------------------------------------------------------------------------- #
# HTTP layer: cache + retry + rate limit
# --------------------------------------------------------------------------- #
_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})


def _cache_path(namespace: str, key: str) -> Path:
    sub = CACHE_DIR / namespace
    sub.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(key.encode()).hexdigest()[:16]
    safe = key.replace("/", "_").replace(" ", "_")[:60]
    return sub / f"{safe}__{h}.json"


def _read_cache(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        log.warning("Corrupt cache, refetching: %s", path)
        return None


def fetch(namespace: str, key: str, url: str, params: dict,
          delay: float = 0.6, max_retries: int = 4) -> dict:
    """Cached + retrying GET. Returns parsed JSON dict (or {} on hard failure).

    Behavior:
      - Cache hit -> return cached JSON, no network, no sleep.
      - 200       -> cache + return, sleep `delay`s after.
      - 400 with body shape {"results": [...]} -> NHTSA's "no results" quirk;
        treat as empty success (cache + return).
      - 429 / 5xx -> exponential backoff + retry.
      - other     -> log and return {}.
    """
    cached = _read_cache(_cache_path(namespace, key))
    if cached is not None:
        return cached

    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            r = _session.get(url, params=params, timeout=20)
        except requests.RequestException as e:
            if attempt == max_retries:
                log.error("Network failed for %s: %s", url, e)
                return {}
            time.sleep(backoff)
            backoff *= 2
            continue

        if r.status_code == 200:
            data = r.json()
        elif r.status_code == 400:
            # NHTSA quirk: HTTP 400 with body
            #   {"Count":0,"Message":"Results returned successfully","results":[]}
            # is an empty success, not an error.
            try:
                data = r.json()
            except ValueError:
                data = None
            if not (isinstance(data, dict) and "results" in data):
                log.error("HTTP 400 (real) on %s: %s", url, r.text[:200])
                return {}
        elif r.status_code in (429, 500, 502, 503, 504):
            wait = float(r.headers.get("Retry-After") or backoff)
            log.warning("HTTP %d on %s — backing off %.1fs", r.status_code, url, wait)
            time.sleep(wait)
            backoff *= 2
            continue
        else:
            log.error("HTTP %d on %s: %s", r.status_code, url, r.text[:200])
            return {}

        _cache_path(namespace, key).write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        if delay > 0:
            time.sleep(delay)
        return data

    return {}


# --------------------------------------------------------------------------- #
# NHTSA endpoints
# --------------------------------------------------------------------------- #
def get_models(make: str, year: int, delay: float) -> list:
    """Models that NHTSA's safety datasets recognize for (make, year).

    Union of recall-catalog ('r') and complaint-catalog ('c') results — some
    vehicles only appear in one.
    """
    out = set()
    for issue in ("r", "c"):
        data = fetch(
            namespace="catalog_models",
            key=f"{make.lower()}__{year}__{issue}",
            url=f"{API_BASE}/products/vehicle/models",
            params={"modelYear": year, "make": make, "issueType": issue},
            delay=delay,
        )
        for r in data.get("results", []) or []:
            name = (r.get("model") or "").strip()
            if name:
                out.add(name)
    return sorted(out)


def get_recalls(make: str, model: str, year: int, delay: float) -> list:
    data = fetch(
        namespace="recalls",
        key=f"{make.lower()}__{model.lower()}__{year}",
        url=f"{API_BASE}/recalls/recallsByVehicle",
        params={"make": make, "model": model, "modelYear": year},
        delay=delay,
    )
    return data.get("results", []) or []


def get_complaints(make: str, model: str, year: int, delay: float) -> list:
    data = fetch(
        namespace="complaints",
        key=f"{make.lower()}__{model.lower()}__{year}",
        url=f"{API_BASE}/complaints/complaintsByVehicle",
        params={"make": make, "model": model, "modelYear": year},
        delay=delay,
    )
    return data.get("results", []) or []


# --------------------------------------------------------------------------- #
# Aggregation per (year, make, model)
# --------------------------------------------------------------------------- #
def categorize(component_str: str) -> set:
    """Map a NHTSA component string to {category, ...}.

    Records can list multiple comma-separated components; each is matched
    independently.
    """
    if not component_str:
        return {"other"}
    matched = set()
    for part in (p.strip() for p in component_str.upper().split(",") if p.strip()):
        for cat, kws in COMPONENT_RULES:
            if any(kw in part for kw in kws):
                matched.add(cat)
                break
    return matched or {"other"}


def count_by_category(records: list, field: str) -> dict:
    counts = {c: 0 for c in CATEGORIES}
    for r in records:
        for cat in categorize(r.get(field)):
            counts[cat] += 1
    return counts


def _truthy(v) -> bool:
    """NHTSA crash/fire flags can be bool *or* 'Yes'/'No' strings.
    `bool('No') is True` in Python, so we normalize defensively.
    """
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"yes", "true", "1", "y"}


def build_row(year: int, make: str, model: str, delay: float) -> dict:
    recalls    = get_recalls(make, model, year, delay)
    complaints = get_complaints(make, model, year, delay)

    rec_cats = count_by_category(recalls,    field="Component")
    cmp_cats = count_by_category(complaints, field="components")

    age = max(CURRENT_YEAR - year, 1)
    row = {
        "year":            year,
        "make":            make,
        "model":           model,
        "vehicle_age":     age,
        "brand_category":  BRAND_CATEGORY.get(make, "other"),
        "recall_count":    len(recalls),
        "complaint_count": len(complaints),
        "complaint_rate":  len(complaints) / age,
        "crash_count":     sum(1 for c in complaints if _truthy(c.get("crash"))),
        "fire_count":      sum(1 for c in complaints if _truthy(c.get("fire"))),
        "injury_count":    sum(int(c.get("numberOfInjuries") or 0) for c in complaints),
        "death_count":     sum(int(c.get("numberOfDeaths") or 0) for c in complaints),
    }
    for cat in CATEGORIES:
        row[f"recall_{cat}_count"]    = rec_cats.get(cat, 0)
        row[f"complaint_{cat}_count"] = cmp_cats.get(cat, 0)
    return row


# --------------------------------------------------------------------------- #
# Trim merge: collapse cab styles / seat configs / HEV-vs-HYBRID renames
# --------------------------------------------------------------------------- #
# WHY: NHTSA's complaint API does fuzzy/prefix matching on `model`. Asking
# for "F-150 SUPER CAB" returns the SAME complaint set as "F-150 SUPER CREW".
# Keeping every cab style as its own row 5x-counts every F-150 complaint.
# So we collapse to one row per (year, make, base_model) where:
#   - complaint_*  cols  -> MAX (rows are duplicates; max == real value)
#   - recall_*     cols  -> SUM (recalls API is strict; trims = different data)
#   - severity     cols  -> MAX (computed from complaints, same logic)

_FORD_CAB_PATTERNS = [
    r"\s+SUPER\s+CREW\s+DIESEL$",
    r"\s+SUPER\s+CAB\s+DIESEL$",
    r"\s+SUPERCAB\s+DIESEL$",
    r"\s+SUPER\s+CREW\s+HEV$",
    r"\s+SUPER\s+CREW$",
    r"\s+SUPER\s+CAB$",
    r"\s+SUPERCAB$",
    r"\s+CREW\s+CAB$",
    r"\s+REGULAR\s+CAB$",
    r"\s+TREMOR$",
]


def _normalize(make: str, model: str) -> str:
    out = re.sub(r"\s+", " ", model).strip()
    if make == "Ford":
        for pat in _FORD_CAB_PATTERNS:
            out = re.sub(pat, "", out, flags=re.IGNORECASE)
    elif make == "Tesla":
        out = re.sub(r"\s*\(ALL VARIANTS[^)]*\)", "", out, flags=re.IGNORECASE)
        out = re.sub(r"\s+\d+\s*-\s*SEAT$", "", out, flags=re.IGNORECASE)
    elif make in ("Hyundai", "Toyota"):
        out = re.sub(r"\bHEV\b", "HYBRID", out, flags=re.IGNORECASE)
        out = re.sub(r"\bEV\b", "ELECTRIC", out, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", out).strip()


def _agg_rule(col: str) -> str:
    if col.startswith("recall_") or col == "recall_count":
        return "sum"
    if col.startswith("complaint_") or col in {
        "complaint_count", "crash_count", "fire_count",
        "injury_count", "death_count",
    }:
        return "max"
    return "first"


def merge_trims(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse trim variants into one row per (year, make, base_model)."""
    df = df.copy()
    df["base_model"] = [_normalize(m, mo) for m, mo in zip(df["make"], df["model"])]

    agg = {c: _agg_rule(c) for c in df.columns
           if c not in ("year", "make", "model", "base_model")}

    grouped = df.groupby(["year", "make", "base_model"], as_index=False).agg(
        **{c: (c, agg[c]) for c in agg},
        n_trims=("model", "count"),
        merged_models=("model", lambda s: " | ".join(sorted(s.unique()))),
    )

    # complaint_count was MAX'd, not summed — recompute the rate to match.
    grouped["complaint_rate"] = (
        grouped["complaint_count"] / grouped["vehicle_age"].clip(lower=1)
    )

    front = ["year", "make", "base_model", "vehicle_age", "brand_category",
             "n_trims", "merged_models",
             "recall_count", "complaint_count", "complaint_rate",
             "crash_count", "fire_count", "injury_count", "death_count"]
    rest = [c for c in grouped.columns if c not in front]
    return grouped[front + rest].sort_values(
        ["year", "make", "base_model"]
    ).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #
def collect(years, makes, out_csv: Path, delay: float,
            no_cache: bool, max_models):
    if no_cache and CACHE_DIR.exists():
        log.warning("--no-cache: wiping %s", CACHE_DIR)
        shutil.rmtree(CACHE_DIR)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    started = time.time()
    log.info("Scope: %d years × %d makes (%s)",
             len(years), len(makes), ", ".join(makes))

    # Phase 1: enumerate models
    plan = []
    log.info("Phase 1/3: enumerating models from NHTSA catalog...")
    for year in years:
        for make in makes:
            names = get_models(make, year, delay)
            if max_models:
                names = names[:max_models]
            log.info("  %s %d: %d models", make, year, len(names))
            for name in names:
                plan.append((year, make, name))

    # Phase 2: per-vehicle pull
    log.info("Phase 2/3: pulling recalls + complaints for %d vehicles...",
             len(plan))
    rows = []
    for i, (year, make, model) in enumerate(plan, 1):
        try:
            rows.append(build_row(year, make, model, delay))
        except Exception as e:
            log.error("Skipping %s %s %s: %s", make, model, year, e)
        if i % 25 == 0 or i == len(plan):
            log.info("  progress: %d / %d", i, len(plan))

    if not rows:
        log.error("No data collected. Aborting.")
        return None

    raw_df = pd.DataFrame(rows).sort_values(
        ["year", "make", "model"]
    ).reset_index(drop=True)
    log.info("Collected %d raw (year, make, model) rows", len(raw_df))

    # Phase 3: merge trim variants
    log.info("Phase 3/3: merging trim variants...")
    merged = merge_trims(raw_df)
    reduction = (1 - len(merged) / len(raw_df)) * 100
    log.info("  merged %d -> %d rows (%.1f%% reduction)",
             len(raw_df), len(merged), reduction)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_csv, index=False)
    log.info("Done. %d rows -> %s (%.1f min)",
             len(merged), out_csv, (time.time() - started) / 60)
    return merged


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args():
    p = argparse.ArgumentParser(description="AutoRisk NHTSA data collection")
    p.add_argument("--years", type=int, nargs="+", default=YEARS_DEFAULT,
                   help=f"Model years (default: {YEARS_DEFAULT[0]}-{YEARS_DEFAULT[-1]})")
    p.add_argument("--makes", type=str, nargs="+", default=MAKES_DEFAULT,
                   help=f"Vehicle makes (default: {len(MAKES_DEFAULT)} makes)")
    p.add_argument("--out", type=Path, default=OUTPUT_CSV,
                   help=f"Output CSV path (default: {OUTPUT_CSV})")
    p.add_argument("--delay", type=float, default=0.6,
                   help="Seconds between *uncached* API calls (default 0.6)")
    p.add_argument("--no-cache", action="store_true",
                   help="Wipe and rebuild cache from scratch")
    p.add_argument("--max-models", type=int, default=None,
                   help="Cap models per (make, year) — useful for quick tests")
    return p.parse_args()


if __name__ == "__main__":
    a = parse_args()
    collect(
        years=a.years,
        makes=a.makes,
        out_csv=a.out,
        delay=a.delay,
        no_cache=a.no_cache,
        max_models=a.max_models,
    )

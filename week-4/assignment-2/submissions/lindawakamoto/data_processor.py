import os
import json
import pandas as pd
from typing import List, Dict, Tuple


# -----------------------------
# LOAD RAW DATA
# -----------------------------
def load_json_folder(folder: str) -> List[Dict]:
    data = []

    for file in os.listdir(folder):
        if not file.endswith(".json"):
            continue

        path = os.path.join(folder, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                obj = json.load(f)
                if isinstance(obj, dict):
                    data.append(obj)
        except Exception:
            continue

    return data


def load_raw_data() -> Tuple[List[Dict], List[Dict]]:
    base = os.path.dirname(os.path.abspath(__file__))

    tmdb_folder = os.path.join(base, "data", "raw", "tmdb")
    letterboxd_folder = os.path.join(base, "data", "raw", "letterboxd")

    tmdb_data = load_json_folder(tmdb_folder)
    letterboxd_data = load_json_folder(letterboxd_folder)

    print(f"Loaded TMDB: {len(tmdb_data)}")
    print(f"Loaded Letterboxd: {len(letterboxd_data)}")

    return tmdb_data, letterboxd_data


# -----------------------------
# NORMALIZATION
# -----------------------------
def normalize_title(title: str) -> str:
    if not title:
        return ""

    return (
        title.lower()
        .strip()
        .replace("the ", "")
        .replace("a ", "")
        .replace("an ", "")
    )


def extract_year(value):
    if not value:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str) and len(value) >= 4:
        try:
            return int(value[:4])
        except:
            return None

    return None


def to_float(x):
    try:
        return float(str(x).replace(",", "").strip())
    except:
        return None


# -----------------------------
# MERGE DATA (FIXED LOGIC)
# -----------------------------
def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
    # -----------------------------
    # INDEX TMDB BY TITLE
    # -----------------------------
    tmdb_index = {}

    for m in tmdb_data:
        title = normalize_title(m.get("title"))
        year = extract_year(m.get("release_date"))

        if not title:
            continue

        tmdb_index.setdefault(title, []).append({
            "title": m.get("title"),
            "year": year,
            "release_date": m.get("release_date"),
            "runtime": m.get("runtime"),
            "genres": m.get("genres"),
            "rating": m.get("rating"),
            "vote_count": m.get("vote_count"),
            "budget": m.get("budget"),
            "revenue": m.get("revenue"),
            "cast": m.get("cast", [])[:5],
            "crew": m.get("crew", [])[:5],
            "production_companies": m.get("production_companies", []),
            "language": m.get("language")
        })

    # -----------------------------
    # INDEX LETTERBOXD BY TITLE
    # -----------------------------
    lb_index = {}

    for m in letterboxd_data:
        title = normalize_title(m.get("title"))
        year = extract_year(m.get("year"))

        if not title:
            continue

        lb_index.setdefault(title, []).append(m)

    # -----------------------------
    # MERGE USING SCORING
    # -----------------------------
    merged = []

    for title, tmdb_list in tmdb_index.items():
        lb_list = lb_index.get(title, [])

        for t in tmdb_list:
            t_year = t.get("year")

            best = None
            best_score = -1

            for l in lb_list:
                l_year = extract_year(l.get("year"))

                score = 0

                # title already matched via dict key

                # year match boosts score strongly
                if t_year and l_year:
                    if t_year == l_year:
                        score += 10
                    else:
                        score += 2  # fallback weak match

                elif l_year is None:
                    score += 1

                if score > best_score:
                    best = l
                    best_score = score

            if best:
                merged.append({
                    "title": t.get("title"),
                    "year": t_year,

                    # TMDB
                    "release_date": t.get("release_date"),
                    "runtime": t.get("runtime"),
                    "genres": t.get("genres"),
                    "tmdb_rating": t.get("rating"),
                    "vote_count": t.get("vote_count"),
                    "budget": t.get("budget"),
                    "revenue": t.get("revenue"),
                    "cast": t.get("cast"),
                    "crew": t.get("crew"),
                    "production_companies": t.get("production_companies"),
                    "language": t.get("language"),

                    # Letterboxd
                    "letterboxd_rating": to_float(best.get("rating")),
                    "fan_count": best.get("fan_count"),
                    "letterboxd_url": best.get("url")
                })

    df = pd.DataFrame(merged)

    print(f"Merged rows: {len(df)}")

    return df


# -----------------------------
# CLEAN DATA
# -----------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    df["tmdb_rating"] = pd.to_numeric(df["tmdb_rating"], errors="coerce")
    df["letterboxd_rating"] = pd.to_numeric(df["letterboxd_rating"], errors="coerce")
    df["fan_count"] = pd.to_numeric(df["fan_count"], errors="coerce")

    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

    df = df.drop_duplicates(subset=["title", "year"])

    print(f"Final dataset size: {len(df)}")

    return df


# -----------------------------
# SAVE OUTPUT
# -----------------------------
def save_processed_data(df: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "processed_data.csv")
    json_path = os.path.join(output_dir, "processed_data.json")

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)

    print(f"Saved CSV → {csv_path}")
    print(f"Saved JSON → {json_path}")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    tmdb, letterboxd = load_raw_data()

    merged = merge_data(tmdb, letterboxd)

    cleaned = clean_data(merged)

    save_processed_data(cleaned, "data/processed")


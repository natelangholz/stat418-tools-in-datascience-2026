"""
Merge trim/body-style variants in AutoRisk processed data.

Input:
    data/processed/vehicle_risk_2020_2024_10brands.csv

Output:
    data/processed/vehicle_risk_features_merged.csv

Run:
    python src/merge.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("data/processed/vehicle_risk_2020_2024_10brands.csv")
DEFAULT_OUTPUT = Path("data/processed/vehicle_risk_features_merged.csv")


def normalize_model(make: str, model: str) -> str:
    """
    Convert trim/body-style variants into a base model name.

    Important rule:
    Only merge clear trim/body/cab/seat naming variants.
    Do NOT merge genuinely different vehicles or powertrains unless it is only
    a naming duplicate.
    """
    make = str(make).strip()
    out = str(model).upper().strip()
    out = re.sub(r"\s+", " ", out)

    # -------------------------
    # Generic cleanup
    # -------------------------
    out = re.sub(r"\s+\(.*?\)$", "", out).strip()
    out = re.sub(r"\s+WITH RECARO$", "", out)
    out = re.sub(r"\s+WITHOUT RECARO$", "", out)

    # -------------------------
    # Ford
    # -------------------------
    if make == "Ford":
        # Keep gas Mustang and Mach-E separate.
        if out.startswith("MUSTANG MACH-E"):
            return "MUSTANG MACH-E"
        if out.startswith("MUSTANG "):
            return "MUSTANG"

        # F-series cab / body variants.
        ford_patterns = [
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
            r"\s+SD$",
        ]
        for pat in ford_patterns:
            out = re.sub(pat, "", out)

        if out.startswith("TRANSIT CONNECT"):
            return "TRANSIT CONNECT"
        if out.startswith("TRANSIT"):
            return "TRANSIT"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Chevrolet
    # -------------------------
    if make == "Chevrolet":
        if out.startswith("CAMARO"):
            return "CAMARO"

        if out.startswith("EXPRESS CARGO"):
            return "EXPRESS CARGO"
        if out.startswith("EXPRESS PASSENGER"):
            return "EXPRESS PASSENGER"
        if out.startswith("EXPRESS CUTAWAY"):
            return "EXPRESS CUTAWAY"

        # Keep truck weight classes separate.
        if out.startswith("SILVERADO 1500 LTD"):
            return "SILVERADO 1500"
        if out.startswith("SILVERADO 1500"):
            return "SILVERADO 1500"
        if out.startswith("SILVERADO 2500"):
            return "SILVERADO 2500"
        if out.startswith("SILVERADO 3500"):
            return "SILVERADO 3500"
        if out.startswith("SILVERADO 4500"):
            return "SILVERADO 4500"
        if out.startswith("SILVERADO 5500"):
            return "SILVERADO 5500"
        if out.startswith("SILVERADO 6500"):
            return "SILVERADO 6500"

        if out.startswith("SUBURBAN"):
            return "SUBURBAN"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Honda
    # -------------------------
    if make == "Honda":
        if out.startswith("CIVIC"):
            return "CIVIC"

        if out.startswith("ACCORD"):
            if "HYBRID" in out:
                return "ACCORD HYBRID"
            return "ACCORD"

        if out.startswith("CR-V"):
            if "HYBRID" in out:
                return "CR-V HYBRID"
            return "CR-V"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Nissan
    # -------------------------
    if make == "Nissan":
        if out.startswith("FRONTIER"):
            return "FRONTIER"

        if out.startswith("TITAN XD"):
            return "TITAN XD"
        if out.startswith("TITAN"):
            return "TITAN"

        # Keep LEAF and LEAF PLUS separate unless you want full model-family merge.
        if out.startswith("LEAF PLUS"):
            return "LEAF PLUS"
        if out.startswith("LEAF"):
            return "LEAF"

        if out.startswith("NV3500 PASS"):
            return "NV3500 PASSENGER VAN"
        if out.startswith("NV3500 CARGO"):
            return "NV3500 CARGO VAN"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Hyundai
    # -------------------------
    if make == "Hyundai":
        out = re.sub(r"\bHEV\b", "HYBRID", out)
        out = re.sub(r"\bPHEV\b", "PLUG-IN HYBRID", out)
        out = re.sub(r"\bEV\b", "ELECTRIC", out)

        if out.startswith("ELANTRA HEV"):
            return "ELANTRA HYBRID"
        if out.startswith("SONATA HEV"):
            return "SONATA HYBRID"
        if out.startswith("TUCSON HEV"):
            return "TUCSON HYBRID"
        if out.startswith("TUCSON PHEV"):
            return "TUCSON PLUG-IN HYBRID"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Kia
    # -------------------------
    if make == "Kia":
        out = re.sub(r"\bHEV\b", "HYBRID", out)
        out = re.sub(r"\bPHEV\b", "PLUG-IN HYBRID", out)
        out = re.sub(r"\bEV\b", "ELECTRIC", out)

        if out == "NIRO EV":
            return "NIRO ELECTRIC"
        if out == "NIRO PHEV":
            return "NIRO PLUG-IN HYBRID"
        if out == "SORENTO PHEV":
            return "SORENTO PLUG-IN HYBRID"
        if out == "SPORTAGE PHEV":
            return "SPORTAGE PLUG-IN HYBRID"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Toyota
    # -------------------------
    if make == "Toyota":
        out = re.sub(r"\bHEV\b", "HYBRID", out)
        out = re.sub(r"\bPHEV\b", "PLUG-IN HYBRID", out)
        out = re.sub(r"\bEV\b", "ELECTRIC", out)

        # Keep normal / hybrid / prime separate.
        if out.startswith("RAV4 PRIME"):
            return "RAV4 PRIME"
        if out.startswith("RAV4 HYBRID"):
            return "RAV4 HYBRID"
        if out.startswith("RAV4"):
            return "RAV4"

        if out.startswith("CAMRY HYBRID"):
            return "CAMRY HYBRID"
        if out.startswith("CAMRY"):
            return "CAMRY"

        if out.startswith("COROLLA HYBRID"):
            return "COROLLA HYBRID"
        if out.startswith("COROLLA"):
            return "COROLLA"

        return re.sub(r"\s+", " ", out).strip()

    # -------------------------
    # Tesla
    # -------------------------
    if make == "Tesla":
        out = re.sub(r"\s*\(ALL VARIANTS[^)]*\)", "", out)
        out = re.sub(r"\s+\d+\s*-\s*SEAT$", "", out)
        return re.sub(r"\s+", " ", out).strip()

    # Default: return cleaned model name.
    return re.sub(r"\s+", " ", out).strip()


def choose_model_column(df: pd.DataFrame) -> str:
    """
    Your current processed file already has base_model.
    If a future file has raw model instead, use model.
    """
    if "model" in df.columns:
        return "model"
    if "base_model" in df.columns:
        return "base_model"
    raise ValueError("Input CSV must contain either 'model' or 'base_model' column.")


def combine_strings(series: pd.Series) -> str:
    """Combine unique non-empty model strings with |."""
    values = []
    for x in series.dropna().astype(str):
        parts = [p.strip() for p in x.split("|") if p.strip()]
        values.extend(parts)
    return " | ".join(sorted(set(values)))


def agg_rule(col: str) -> str:
    """
    Aggregation rules when merging rows.

    recall_*:
        sum, because recalls are stricter and trim-specific recalls can differ.

    complaint_* and severity counts:
        max, because NHTSA complaint API can return duplicate complaint sets
        for trim/body variants. Summing would overcount.

    identifiers / categories:
        first.
    """
    if col == "recall_count" or col.startswith("recall_"):
        return "sum"

    if (
        col == "complaint_count"
        or col.startswith("complaint_")
        or col in ["crash_count", "fire_count", "injury_count", "death_count"]
    ):
        return "max"

    if col == "n_trims":
        return "sum"

    return "first"


def merge_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    model_col = choose_model_column(df)

    # Make sure these are clean strings.
    df["make"] = df["make"].astype(str).str.strip()
    df[model_col] = df[model_col].astype(str).str.strip()

    # New normalized model name.
    df["merged_base_model"] = [
        normalize_model(make, model)
        for make, model in zip(df["make"], df[model_col])
    ]

    # If current file already has merged_models, preserve it.
    if "merged_models" not in df.columns:
        df["merged_models"] = df[model_col]

    # If current file has no n_trims, create it.
    if "n_trims" not in df.columns:
        df["n_trims"] = 1

    group_keys = ["year", "make", "merged_base_model"]

    exclude = set(group_keys + ["base_model", "model"])
    agg_cols = [c for c in df.columns if c not in exclude]

    named_aggs = {}

    for col in agg_cols:
        if col == "merged_models":
            named_aggs[col] = (col, combine_strings)
        elif col == "merged_base_model":
            continue
        else:
            named_aggs[col] = (col, agg_rule(col))

    merged = df.groupby(group_keys, as_index=False).agg(**named_aggs)

    # Rename merged_base_model back to base_model because eda.py expects base_model.
    merged = merged.rename(columns={"merged_base_model": "base_model"})

    # Recompute complaint_rate after complaint_count max aggregation.
    if "complaint_count" in merged.columns and "vehicle_age" in merged.columns:
        merged["complaint_rate"] = merged["complaint_count"] / merged["vehicle_age"].clip(lower=1)

    # Put important columns first.
    front = [
        "year",
        "make",
        "base_model",
        "vehicle_age",
        "brand_category",
        "n_trims",
        "merged_models",
        "recall_count",
        "complaint_count",
        "complaint_rate",
        "crash_count",
        "fire_count",
        "injury_count",
        "death_count",
    ]

    front = [c for c in front if c in merged.columns]
    rest = [c for c in merged.columns if c not in front]

    merged = merged[front + rest].sort_values(["year", "make", "base_model"]).reset_index(drop=True)

    return merged


def parse_args():
    parser = argparse.ArgumentParser(description="Merge AutoRisk trim variants.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")

    df = pd.read_csv(args.input)
    print(f"Loaded: {args.input}")
    print(f"Before merge: {len(df)} rows")

    merged = merge_data(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)

    print(f"After merge:  {len(merged)} rows")
    print(f"Saved: {args.output}")

    print("\nRows by make after merge:")
    print(merged["make"].value_counts().sort_index())


if __name__ == "__main__":
    main()
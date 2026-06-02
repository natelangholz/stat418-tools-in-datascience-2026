"""
EDA + proposal-ready figures for AutoRisk.

Reads (in priority order):
    data/processed/vehicle_risk_features_merged.csv   (preferred — trim-deduped)
    data/processed/vehicle_risk_features.csv          (fallback — raw)

Writes:
    data/processed/vehicle_risk_features_labeled.csv  (adds `risk_label`)
    figures/*.png   (7 charts ready to drop into the proposal slides)

Run:
    python src/eda.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("eda")

INPUT_CSV_MERGED = Path("data/processed/vehicle_risk_features_merged.csv")
INPUT_CSV_RAW = Path("data/processed/vehicle_risk_features.csv")
OUTPUT_CSV = Path("data/processed/vehicle_risk_features_labeled.csv")
FIG_DIR = Path("figures")

sns.set_theme(style="whitegrid", context="talk")


def add_risk_label(df, top_q=0.30):
    """Binary label: 1 if complaint_rate is in the top `top_q` quantile.

    NOTE on methodology:
        - The label is derived from `complaint_rate`.
        - The MODEL must therefore NOT use complaint_count / complaint_rate
          / per-component complaint counts as features.
        - Allowed feature columns are listed in SAFE_FEATURES below.
    """
    df = df.copy()
    threshold = df["complaint_rate"].quantile(1 - top_q)
    df["risk_label"] = (df["complaint_rate"] >= threshold).astype(int)
    df["risk_threshold"] = threshold
    return df


SAFE_FEATURES = [
    "year",
    "vehicle_age",
    "make",
    "brand_category",
    "recall_count",
    "recall_restraint_count",
    "recall_brake_count",
    "recall_electrical_count",
    "recall_engine_count",
    "recall_powertrain_count",
    "recall_fuel_count",
    "recall_steering_count",
    "recall_suspension_count",
    "recall_structure_count",
    "recall_other_count",
]
LABEL_COL = "risk_label"


def drop_empty_rows(df):
    before = len(df)
    df = df[~((df["recall_count"] == 0) & (df["complaint_count"] == 0))].copy()
    log.info("Dropped %d zero-data rows (%d -> %d)", before - len(df), before, len(df))
    return df


def _save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / name
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("wrote %s", out)
    return out


def fig_dataset_summary(df):
    fig, ax = plt.subplots(figsize=(11, 5))
    counts = df.groupby(["make", "year"]).size().unstack(fill_value=0)
    counts.plot(kind="bar", stacked=True, ax=ax, colormap="viridis", width=0.85)
    ax.set_title("Dataset coverage: # base_models per make x year")
    ax.set_ylabel("# (year, base_model) rows")
    ax.set_xlabel("Make")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Year", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    _save(fig, "01_dataset_coverage.png")


def fig_recall_distribution(df):
    fig, ax = plt.subplots(figsize=(11, 5))
    order = df.groupby("make")["recall_count"].median().sort_values().index
    sns.boxplot(data=df, x="make", y="recall_count", order=order, ax=ax, palette="Set2")
    ax.set_title("Recall count distribution by make")
    ax.set_ylabel("Recalls per (year, base_model)")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "02_recall_distribution.png")


def fig_complaint_by_year(df):
    fig, ax = plt.subplots(figsize=(11, 5))
    grp = df.groupby(["year", "brand_category"])["complaint_count"].mean().reset_index()
    sns.lineplot(data=grp, x="year", y="complaint_count", hue="brand_category",
                 marker="o", ax=ax)
    ax.set_title("Mean complaints per base_model, by year and brand_category")
    ax.set_ylabel("Mean complaint_count")
    ax.set_xlabel("Model year")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=10)
    _save(fig, "03_complaint_by_year.png")


def fig_top_components(df):
    cat_cols = [c for c in df.columns if c.startswith("complaint_") and c.endswith("_count")
                and c != "complaint_count"]
    totals = df[cat_cols].sum().sort_values(ascending=True)
    totals.index = [c.replace("complaint_", "").replace("_count", "") for c in totals.index]
    fig, ax = plt.subplots(figsize=(9, 5))
    totals.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_title("Total complaints by component category")
    ax.set_xlabel("# complaints (across all vehicles)")
    _save(fig, "04_top_components.png")


def fig_label_distribution(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    counts = df[LABEL_COL].value_counts().sort_index()
    counts.index = ["Not High", "High"]
    counts.plot(kind="bar", ax=ax, color=["#9ecae1", "#e6550d"])
    ax.set_title("Label distribution (top 30% complaint_rate -> High)")
    ax.set_ylabel("# vehicles")
    for i, v in enumerate(counts.values):
        ax.text(i, v, str(int(v)), ha="center", va="bottom")
    _save(fig, "05_label_distribution.png")


def fig_label_rate_by_make(df):
    fig, ax = plt.subplots(figsize=(9, 7))
    rate = df.groupby("make")[LABEL_COL].mean().sort_values()
    rate.plot(kind="barh", ax=ax, color="coral")
    ax.set_title("High-risk rate by make")
    ax.set_xlabel("P(High risk)")
    for i, v in enumerate(rate.values):
        ax.text(v, i, f" {v:.2f}", va="center")
    _save(fig, "06_label_rate_by_make.png")


def fig_label_rate_by_brand_category(df):
    fig, ax = plt.subplots(figsize=(9, 5))
    rate = df.groupby("brand_category").agg(
        high_rate=(LABEL_COL, "mean"),
        n=(LABEL_COL, "size"),
    ).sort_values("high_rate")
    rate["high_rate"].plot(kind="barh", ax=ax, color="indianred")
    ax.set_title("High-risk rate by brand_category")
    ax.set_xlabel("P(High risk)")
    ax.set_ylabel("")
    for i, (cat, row) in enumerate(rate.iterrows()):
        ax.text(row["high_rate"], i, f" {row['high_rate']:.2f}  (n={int(row['n'])})", va="center")
    _save(fig, "07_label_rate_by_brand_category.png")


def main():
    if INPUT_CSV_MERGED.exists():
        input_csv = INPUT_CSV_MERGED
        log.info("Using MERGED CSV (trim-deduped): %s", input_csv)
    elif INPUT_CSV_RAW.exists():
        input_csv = INPUT_CSV_RAW
        log.warning("Merged CSV not found. Using RAW CSV: %s", input_csv)
        log.warning("  -> Run `python src/merge_trims.py` first for cleaner data.")
    else:
        raise SystemExit(
            f"Neither {INPUT_CSV_MERGED} nor {INPUT_CSV_RAW} exists. "
            "Run `python src/collect_data.py` first."
        )

    df = pd.read_csv(input_csv)
    log.info("Loaded %d rows, %d cols from %s", len(df), df.shape[1], input_csv)

    df = drop_empty_rows(df)

    print("\n=== DATASET SUMMARY ===")
    print(df.describe(include="all").T[["count", "mean", "min", "max"]].head(20))
    print("\n=== MISSINGNESS ===")
    miss = df.isna().sum()
    print(miss[miss > 0] if (miss > 0).any() else "  (none)")
    print(f"\n=== ROWS PER MAKE ===\n{df['make'].value_counts()}")
    print(f"\n=== ROWS PER BRAND_CATEGORY ===\n{df['brand_category'].value_counts()}")

    df = add_risk_label(df, top_q=0.30)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    log.info("wrote labeled CSV -> %s", OUTPUT_CSV)

    print("\n=== LABEL ===")
    print(df[LABEL_COL].value_counts(normalize=True).rename("share"))

    fig_dataset_summary(df)
    fig_recall_distribution(df)
    fig_complaint_by_year(df)
    fig_top_components(df)
    fig_label_distribution(df)
    fig_label_rate_by_make(df)
    fig_label_rate_by_brand_category(df)

    print("\nDone. Figures in figures/, labeled data at", OUTPUT_CSV)


if __name__ == "__main__":
    main()

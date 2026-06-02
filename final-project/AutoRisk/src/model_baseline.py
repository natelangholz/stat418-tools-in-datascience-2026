"""
Baseline modeling for AutoRisk.

Input:
    data/processed/vehicle_risk_features_labeled.csv

Outputs:
    data/processed/model_baseline_metrics.csv
    figures/08_confusion_matrix_random_forest.png
    figures/09_feature_importance_random_forest.png
    figures/10_model_comparison.png

Run:
    python src/model_baseline.py

Notes:
    risk_label is created from complaint_rate in eda.py.
    Therefore, complaint_count, complaint_rate, and complaint component counts
    are NOT used as model features to avoid data leakage.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
INPUT_CSV = Path("data/processed/vehicle_risk_features_labeled.csv")
METRICS_CSV = Path("data/processed/model_baseline_metrics.csv")
FIG_DIR = Path("figures")


# ---------------------------------------------------------------------
# Safe features
# ---------------------------------------------------------------------
# Do NOT include:
#   complaint_count
#   complaint_rate
#   complaint_*_count
#   crash_count
#   fire_count
#   injury_count
#   death_count
#
# Because risk_label is based on complaint_rate.
# Using complaint-related columns would leak the answer into the model.
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


def load_data() -> pd.DataFrame:
    if not INPUT_CSV.exists():
        raise SystemExit(
            f"Input file not found: {INPUT_CSV}\n"
            "Run src/eda.py first to create vehicle_risk_features_labeled.csv."
        )

    df = pd.read_csv(INPUT_CSV)

    missing_cols = [c for c in SAFE_FEATURES + [LABEL_COL] if c not in df.columns]
    if missing_cols:
        raise SystemExit(f"Missing columns in input CSV: {missing_cols}")

    df = df.dropna(subset=[LABEL_COL]).copy()
    df[LABEL_COL] = df[LABEL_COL].astype(int)

    print(f"Loaded {len(df)} rows from {INPUT_CSV}")
    print("\nLabel distribution:")
    print(df[LABEL_COL].value_counts())
    print("\nLabel share:")
    print(df[LABEL_COL].value_counts(normalize=True))

    return df


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    categorical_features = [
        c for c in SAFE_FEATURES
        if df[c].dtype == "object" or c in ["make", "brand_category"]
    ]

    numeric_features = [
        c for c in SAFE_FEATURES
        if c not in categorical_features
    ]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )

    return preprocessor


def get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """
    Get feature names after preprocessing.
    This is used for Random Forest feature importance.
    """
    feature_names = []

    for name, transformer, cols in preprocessor.transformers_:
        if name == "remainder":
            continue

        if name == "num":
            feature_names.extend(cols)

        elif name == "cat":
            onehot = transformer.named_steps["onehot"]
            encoded = onehot.get_feature_names_out(cols)
            feature_names.extend(encoded)

    return list(feature_names)


def evaluate_model(name: str, model, X_train, X_test, y_train, y_test) -> dict:
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
        "f1": f1_score(y_test, preds, zero_division=0),
    }

    print(f"\n=== {name} ===")
    print(metrics)
    print("\nClassification report:")
    print(classification_report(y_test, preds, target_names=["Not High", "High"]))

    return metrics


def save_confusion_matrix(model, X_test, y_test, filename: str):
    preds = model.predict(X_test)
    cm = confusion_matrix(y_test, preds)

    labels = ["Not High", "High"]

    fig, ax = plt.subplots(figsize=(5.8, 4.8))

    # Use a softer single-color map
    im = ax.imshow(cm, cmap="Blues")

    ax.set_title("Random Forest Confusion Matrix", fontsize=15, pad=12)
    ax.set_xlabel("Predicted label", fontsize=12)
    ax.set_ylabel("True label", fontsize=12)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_yticklabels(labels, fontsize=11)

    # Add counts and row percentages
    row_sums = cm.sum(axis=1, keepdims=True)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            pct = cm[i, j] / row_sums[i, 0] if row_sums[i, 0] else 0
            text = f"{cm[i, j]}\n({pct:.0%})"
            color = "white" if cm[i, j] > cm.max() * 0.55 else "black"
            ax.text(
                j,
                i,
                text,
                ha="center",
                va="center",
                fontsize=13,
                fontweight="bold",
                color=color,
            )

    # Remove heavy borders
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xticks(np.arange(-0.5, 2, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 2, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=10)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / filename
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved confusion matrix: {out}")

def save_feature_importance(model, filename: str, top_n: int = 12):
    """
    Save Random Forest feature importance chart.
    """
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    feature_names = get_feature_names(preprocessor)
    importances = classifier.feature_importances_

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importances,
        }
    ).sort_values("importance", ascending=False)

    # Clean feature labels for slides
    importance_df["feature_clean"] = (
        importance_df["feature"]
        .str.replace("recall_", "Recall: ", regex=False)
        .str.replace("_count", "", regex=False)
        .str.replace("brand_category_", "Brand: ", regex=False)
        .str.replace("make_", "Make: ", regex=False)
        .str.replace("_", " ", regex=False)
        .str.title()
    )

    top = importance_df.head(top_n).sort_values("importance", ascending=True)

    fig, ax = plt.subplots(figsize=(8.5, 5.8))

    bars = ax.barh(top["feature_clean"], top["importance"])

    ax.set_title("Top Predictive Features", fontsize=16, pad=12)
    ax.set_xlabel("Random Forest importance", fontsize=12)
    ax.set_ylabel("")

    ax.tick_params(axis="y", labelsize=10)
    ax.tick_params(axis="x", labelsize=10)

    # Light vertical grid only
    ax.xaxis.grid(True, linestyle="--", alpha=0.35)
    ax.yaxis.grid(False)

    # Remove top/right/left borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.003,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.3f}",
            va="center",
            fontsize=9,
        )

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / filename
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved feature importance: {out}")

    importance_csv = Path("data/processed/random_forest_feature_importance.csv")
    importance_csv.parent.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(importance_csv, index=False)
    print(f"Saved feature importance CSV: {importance_csv}")


def save_model_comparison(metrics_df: pd.DataFrame):
    plot_df = metrics_df.set_index("model")[["accuracy", "precision", "recall", "f1"]]

    # Long format for easier plotting
    long_df = (
        plot_df.reset_index()
        .melt(id_vars="model", var_name="metric", value_name="score")
    )

    metric_order = ["accuracy", "precision", "recall", "f1"]
    model_order = list(plot_df.index)

    x = np.arange(len(metric_order))
    width = 0.34

    fig, ax = plt.subplots(figsize=(8.5, 5.2))

    for idx, model_name in enumerate(model_order):
        values = [
            long_df[
                (long_df["model"] == model_name)
                & (long_df["metric"] == metric)
            ]["score"].iloc[0]
            for metric in metric_order
        ]

        offset = (idx - 0.5) * width
        bars = ax.bar(x + offset, values, width, label=model_name)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.015,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_title("Baseline Model Performance", fontsize=16, pad=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_ylim(0, 1.05)

    ax.set_xticks(x)
    ax.set_xticklabels(["Accuracy", "Precision", "Recall", "F1"], fontsize=11)

    ax.yaxis.grid(True, linestyle="--", alpha=0.35)
    ax.xaxis.grid(False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(frameon=False, loc="lower right", fontsize=10)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "10_model_comparison_clean.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved model comparison: {out}")


def main():
    df = load_data()

    X = df[SAFE_FEATURES].copy()
    y = df[LABEL_COL].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    preprocessor = build_preprocessor(df)

    logistic_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    random_forest_model = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(df)),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=None,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    metrics = []

    metrics.append(
        evaluate_model(
            "Logistic Regression",
            logistic_model,
            X_train,
            X_test,
            y_train,
            y_test,
        )
    )

    metrics.append(
        evaluate_model(
            "Random Forest",
            random_forest_model,
            X_train,
            X_test,
            y_train,
            y_test,
        )
    )

    metrics_df = pd.DataFrame(metrics)
    METRICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(METRICS_CSV, index=False)

    print(f"\nSaved metrics: {METRICS_CSV}")
    print(metrics_df)

    save_confusion_matrix(
        random_forest_model,
        X_test,
        y_test,
        "08_confusion_matrix_clean.png",
    )

    save_feature_importance(
        random_forest_model,
        "09_feature_importance_clean.png",
        top_n=12,
    )

    save_model_comparison(metrics_df)

    print("\nDone.")
    print("Generated:")
    print(f"  {METRICS_CSV}")
    print("  figures/08_confusion_matrix_random_forest.png")
    print("  figures/09_feature_importance_random_forest.png")
    print("  figures/10_model_comparison.png")


if __name__ == "__main__":
    main()
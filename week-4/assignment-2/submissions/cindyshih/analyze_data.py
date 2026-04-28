import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("data/analysis", exist_ok=True)

df = pd.read_csv("data/processed/processed_movies.csv")


def add_correlation_line(x, y):
    """Add a best-fit line to a scatter plot."""
    slope = y.cov(x) / x.var()
    intercept = y.mean() - slope * x.mean()
    line_y = slope * x + intercept
    plt.plot(x, line_y)


# -----------------------------
# 1. Rating Analysis
# -----------------------------

# Rating Correlation

rating_df = df[["title", "tmdb_rating", "letterboxd_rating"]].dropna()

# Remove invalid/outlier values
rating_df = rating_df[
    (rating_df["tmdb_rating"] > 0) &     # remove 0 ratings
    (rating_df["letterboxd_rating"] > 0) # optional but safe
]

rating_correlation = rating_df["tmdb_rating"].corr(rating_df["letterboxd_rating"])

x = rating_df["tmdb_rating"]
y = rating_df["letterboxd_rating"]

plt.figure(figsize=(7, 5))
plt.scatter(x, y)
add_correlation_line(x, y)
plt.title(f"TMDB Rating vs Letterboxd Rating (r = {rating_correlation:.3f})")
plt.xlabel("TMDB Rating (0-10)")
plt.ylabel("Letterboxd Rating (0-5)")
plt.tight_layout()
plt.savefig("data/analysis/rating_correlation.png")
plt.close()


# Rating Distributions

plt.figure(figsize=(7, 5))
plt.hist(df["tmdb_rating"].dropna(), bins=12, alpha=0.6, label="TMDB (0-10)")
plt.hist(df["letterboxd_rating"].dropna(), bins=12, alpha=0.6, label="Letterboxd (0-5)")
plt.title("Distribution of Ratings on Each Platform")
plt.xlabel("Rating")
plt.ylabel("Number of Movies")
plt.legend()
plt.tight_layout()
plt.savefig("data/analysis/rating_distributions.png")
plt.close()


# -----------------------------
# 2. Genre Analysis
# -----------------------------

genre_rows = []

for _, row in df.iterrows():
    if pd.notna(row["genres"]):
        genres = row["genres"].split(", ")

        for genre in genres:
            genre_rows.append({
                "genre": genre,
                "tmdb_rating": row["tmdb_rating"],
                "letterboxd_rating": row["letterboxd_rating"]
            })

genre_df = pd.DataFrame(genre_rows)

# scale ratings to 0-10 for better comparison
genre_df["letterboxd_rating_scaled"] = genre_df["letterboxd_rating"] * 2

avg_rating_by_genre = (
    genre_df.groupby("genre")[["tmdb_rating", "letterboxd_rating_scaled"]]
    .mean()
    .sort_values("tmdb_rating", ascending=False)
    .head(10)
)

avg_rating_by_genre.plot(kind="bar", figsize=(9, 5))

plt.title("Average Ratings by Genre (TMDB vs Letterboxd, 0-10 Scale)")
plt.xlabel("Genre")
plt.ylabel("Average Rating (0-10 Scale)")
plt.xticks(rotation=45, ha="right")
plt.legend(["TMDB", "Letterboxd scaled (0-10)"])
plt.tight_layout()
plt.savefig("data/analysis/average_rating_by_genre.png")
plt.close()

# -----------------------------
# 3. Financial Analysis
# -----------------------------

finance_df = df[(df["budget"] > 0) & (df["revenue"] > 0)].copy()
budget_revenue_correlation = finance_df["budget"].corr(finance_df["revenue"])

x = finance_df["budget"]
y = finance_df["revenue"]

plt.figure(figsize=(7, 5))
plt.scatter(x, y)
add_correlation_line(x, y)
plt.title(f"Budget vs Revenue (r = {budget_revenue_correlation:.3f})")
plt.xlabel("Budget")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig("data/analysis/budget_vs_revenue.png")
plt.close()


top_genres = genre_df["genre"].value_counts().head(10)

avg_rating_by_genre = (
    genre_df.groupby("genre")[["tmdb_rating", "letterboxd_rating"]]
    .mean()
    .sort_values("tmdb_rating", ascending=False)
    .head(10)
)

finance_df["profit"] = finance_df["revenue"] - finance_df["budget"]
most_profitable = finance_df.sort_values("profit", ascending=False).head(10)

# -----------------------------
# Summary Report
# -----------------------------

with open("data/analysis/summary_report.txt", "w") as f:
    f.write("Movie Data Analysis Summary Report\n")
    f.write("==================================\n\n")

    f.write("1. Rating Analysis\n")
    f.write("------------------\n")
    f.write(f"Number of movies with both TMDB and Letterboxd ratings: {len(rating_df)}\n")
    f.write(f"Correlation between TMDB and Letterboxd ratings: {rating_correlation:.3f}\n")
    f.write(f"Average TMDB rating: {df['tmdb_rating'].mean():.2f}\n")
    f.write(f"Average Letterboxd rating: {df['letterboxd_rating'].mean():.2f}\n")
    f.write("TMDB uses a 0-10 scale, while Letterboxd uses a 0-5 scale.\n\n")

    f.write("2. Genre Analysis\n")
    f.write("-----------------\n")
    f.write("Top 10 most common genres:\n")
    f.write(top_genres.to_string())
    f.write("\n\n")

    f.write("Top 10 genres by average ratings on both platforms:\n")
    f.write(avg_rating_by_genre.to_string())
    f.write("\n\n")

    f.write("3. Financial Analysis\n")
    f.write("---------------------\n")
    f.write(f"Number of movies with valid budget and revenue data: {len(finance_df)}\n")
    f.write(f"Correlation between budget and revenue: {budget_revenue_correlation:.3f}\n\n")

    f.write("Top 10 most profitable movies:\n")
    f.write(most_profitable[["title", "budget", "revenue", "profit"]].to_string(index=False))
    f.write("\n\n")

    f.write("Visualizations Created\n")
    f.write("----------------------\n")
    f.write("1. rating_correlation.png\n")
    f.write("2. rating_distributions.png\n")
    f.write("3. average_rating_by_genre.png\n")
    f.write("4. budget_vs_revenue.png\n")
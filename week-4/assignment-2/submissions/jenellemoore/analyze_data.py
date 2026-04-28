import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# Load, Prepare and Clean
def load_data():
    """Load the processed movie data."""
    return pd.read_csv("data/processed/processed_movies.csv")

def prepare_data(df):
    df = df.copy()

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    numeric_columns = [
        "tmdb_rating",
        "letterboxd_rating",
        "tmdb_vote_count",
        "letterboxd_fans",
        "budget",
        "revenue",
        "runtime"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def clean_genre_text(genre_text):
    """
    Turns a genre string like:
    ["Action", "Adventure", "Drama"]

    into:
    Action, Adventure, Drama
    """
    if pd.isna(genre_text):
        return []

    genre_text = str(genre_text)

    genre_text = genre_text.replace("[", "")
    genre_text = genre_text.replace("]", "")
    genre_text = genre_text.replace('"', "")
    genre_text = genre_text.replace("'", "")

    genres = genre_text.split(",")

    clean_genres = []

    for genre in genres:
        genre = genre.strip()

        if genre != "":
            clean_genres.append(genre)

    return clean_genres

# Analyze Data
def analyze_ratings(df):
    """Compare TMDB and Letterboxd ratings."""

    # Letterboxd is out of 5, TMDB is out of 10
    # So multiply Letterboxd by 2 to compare them fairly
    df["letterboxd_rating_10"] = df["letterboxd_rating"] * 2

    # Only use rows where both ratings exist
    ratings_df = df[
        (df["tmdb_rating"] > 0) &
        (df["letterboxd_rating"] > 0)
    ]

    correlation = ratings_df["tmdb_rating"].corr(ratings_df["letterboxd_rating_10"])

    return ratings_df, correlation

# Rating Analysis
def rating_analysis(df):
    valid_ratings = df[
        (df["tmdb_rating"].notna()) &
        (df["letterboxd_rating"].notna()) &
        (df["letterboxd_rating"] > 0)
    ]

    correlation = valid_ratings["tmdb_rating"].corr(valid_ratings["letterboxd_rating"])

    plt.figure()
    plt.scatter(valid_ratings["tmdb_rating"], valid_ratings["letterboxd_rating"])
    plt.xlabel("TMDB Rating 0-10")
    plt.ylabel("Letterboxd Rating 0-5")
    plt.title("TMDB vs Letterboxd Ratings")
    plt.savefig("visualizations/rating_correlation.png")
    plt.close()

    plt.figure()
    df["tmdb_rating"].dropna().hist()
    plt.xlabel("TMDB Rating")
    plt.ylabel("Number of Movies")
    plt.title("Distribution of TMDB Ratings")
    plt.savefig("visualizations/tmdb_rating_distribution.png")
    plt.close()

    # Runtime vs TMDB Rating chart
    plt.figure()
    plt.scatter(df["runtime"], df["tmdb_rating"])
    plt.xlabel("Runtime in Minutes")
    plt.ylabel("TMDB Rating")
    plt.title("Runtime vs TMDB Rating")
    plt.savefig("visualizations/runtime_vs_tmdb_rating.png")
    plt.close()


    return correlation

def genre_analysis(df):
    genre_rows = []

    for index, row in df.iterrows():
        genres = clean_genre_text(row["genres"])

        for genre in genres:
            genre_rows.append({
                "genre": genre,
                "tmdb_rating": row["tmdb_rating"],
                "letterboxd_rating": row["letterboxd_rating"]
            })

    genre_df = pd.DataFrame(genre_rows)

    most_common_genres = genre_df["genre"].value_counts()

    average_ratings_by_genre = (
        genre_df
        .groupby("genre")["tmdb_rating"]
        .mean()
        .sort_values(ascending=False)
    )

    most_common_genres.head(10).plot(kind="bar")
    plt.xlabel("Genre")
    plt.ylabel("Number of Movies")
    plt.title("Most Common Genres")
    plt.tight_layout()
    plt.savefig("visualizations/most_common_genres.png")
    plt.close()

    average_ratings_by_genre.head(10).plot(kind="bar")
    plt.xlabel("Genre")
    plt.ylabel("Average TMDB Rating")
    plt.title("Average TMDB Rating by Genre")
    plt.tight_layout()
    plt.savefig("visualizations/average_rating_by_genre.png")
    plt.close()

    return most_common_genres, average_ratings_by_genre

# Financial analysis (budget and revenue)
def financial_analysis(df):
    financial_df = df[
        (df["budget"] > 0) &
        (df["revenue"] > 0)
    ].copy()

    financial_df["profit"] = financial_df["revenue"] - financial_df["budget"]

    budget_revenue_corr = financial_df["budget"].corr(financial_df["revenue"])

    plt.figure()
    plt.scatter(financial_df["budget"], financial_df["revenue"])
    plt.xlabel("Budget")
    plt.ylabel("Revenue")
    plt.title("Budget vs Revenue")
    plt.savefig("visualizations/budget_vs_revenue.png")
    plt.close()

    most_profitable = financial_df.sort_values("profit", ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    plt.barh(most_profitable["title"], most_profitable["profit"])
    plt.xlabel("Profit")
    plt.ylabel("Movie")
    plt.title("Top 10 Most Profitable Movies")
    plt.tight_layout()
    plt.savefig("visualizations/top_10_most_profitable.png")
    plt.close()

    most_profitable_table = most_profitable[
        ["title", "budget", "revenue", "profit"]
    ]

    return budget_revenue_corr, most_profitable_table

# Number of movies per year and average rating 
def temporal_analysis(df):
    movies_by_year = df["year"].value_counts().sort_index()

    plt.figure()
    movies_by_year.plot(kind="bar")
    plt.xlabel("Year")
    plt.ylabel("Number of Movies")
    plt.title("Movies Collected by Year")
    plt.tight_layout()
    plt.savefig("visualizations/movies_by_year.png")
    plt.close()

    rating_by_year = df.groupby("year")["tmdb_rating"].mean()

    plt.figure()
    rating_by_year.plot()
    plt.xlabel("Year")
    plt.ylabel("Average TMDB Rating")
    plt.title("Average TMDB Rating by Year")
    plt.tight_layout()
    plt.savefig("visualizations/average_rating_by_year.png")
    plt.close()

    return movies_by_year, rating_by_year

def write_summary_report(
    correlation,
    most_common_genres,
    average_ratings_by_genre,
    budget_revenue_corr,
    most_profitable,
    movies_by_year
):
    with open("analysis_summary_report.txt", "w") as file:
        file.write("Movie Data Analysis Summary\n")
        file.write("===========================\n\n")

        file.write("1. Rating Analysis\n")
        file.write(f"The correlation between TMDB and Letterboxd ratings is {correlation:.2f}.\n\n")
        file.write("I also compared movie runtime with TMDB rating to see whether longer movies tend to receive higher or lower ratings.\n")
        file.write("This visualization helps show whether runtime appears related to audience rating patterns in the dataset.\n\n")

        file.write("2. Genre Analysis\n")
        file.write("Most common genres:\n")
        file.write(most_common_genres.head(10).to_string())
        file.write("\n\nAverage TMDB rating by genre:\n")
        file.write(average_ratings_by_genre.head(10).to_string())
        file.write("\n\n")

        file.write("3. Financial Analysis\n")
        file.write(f"The correlation between budget and revenue is {budget_revenue_corr:.2f}.\n")
        file.write("Most profitable movies:\n")
        file.write(most_profitable.to_string(index=False))
        file.write("\n\n")

        file.write("4. Temporal Analysis\n")
        file.write("Most common release years in this dataset:\n")
        file.write(movies_by_year.sort_values(ascending=False).head(10).to_string())
        file.write("\n\n")

        file.write("Visualizations created:\n")
        file.write("- visualizations/rating_correlation.png\n")
        file.write("- visualizations/tmdb_rating_distribution.png\n")
        file.write("- visualizations/most_common_genres.png\n")
        file.write("- visualizations/average_rating_by_genre.png\n")
        file.write("- visualizations/budget_vs_revenue.png\n")
        file.write("- visualizations/top_10_most_profitable.png\n")
        file.write("- visualizations/movies_by_year.png\n")
        file.write("- visualizations/runtime_vs_tmdb_rating.png\n")

def main():
    Path("visualizations").mkdir(exist_ok=True)

    df = load_data()
    df = prepare_data(df)

    correlation = rating_analysis(df)

    most_common_genres, average_ratings_by_genre = genre_analysis(df)

    budget_revenue_corr, most_profitable = financial_analysis(df)

    movies_by_year, rating_by_year = temporal_analysis(df)

    write_summary_report(
        correlation,
        most_common_genres,
        average_ratings_by_genre,
        budget_revenue_corr,
        most_profitable,
        movies_by_year
    )

    print("Analysis complete.")
    print("Charts saved in the visualizations folder.")
    print("Summary report saved as analysis_summary_report.txt.")

if __name__ == "__main__":
    main()
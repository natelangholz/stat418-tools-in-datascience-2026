import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Set visual style
sns.set_theme(style="whitegrid")

def load_processed_data(file_path: str = "data/processed/movies_processed.json") -> pd.DataFrame:
    """Loads the processed dataset."""
    try:
        df = pd.read_json(file_path)
        # Ensure year is numeric for analysis
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def rating_analysis(df: pd.DataFrame, output_dir: str):
    """Answers: Correlation and Distribution of ratings."""
    print("--- Running Rating Analysis ---")

    has_lb = "rating_lb" in df.columns and df["rating_lb"].notna().any()

    # 1. Correlation (only possible when Letterboxd data is present)
    correlation = None
    if has_lb:
        correlation = df["vote_average"].corr(df["rating_lb"])
        print(f"Correlation between TMDB and Letterboxd: {correlation:.2f}")
    else:
        print("Letterboxd ratings not available — skipping correlation")

    # 2. Visualization
    plt.figure(figsize=(10, 6))
    sns.kdeplot(df["vote_average"].dropna(), label="TMDB (0-10)", fill=True)
    if has_lb:
        sns.kdeplot(df["rating_lb"].dropna(), label="Letterboxd (Scaled 0-10)", fill=True)
    title = "Distribution of Ratings: TMDB vs Letterboxd" if has_lb else "Distribution of TMDB Ratings"
    plt.title(title)
    plt.xlabel("Rating Score")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "rating_distribution.png"))
    plt.close()

    return {"rating_correlation": correlation}

def genre_analysis(df: pd.DataFrame, output_dir: str):
    """Answers: Most common genres and Average ratings by genre."""
    print("--- Running Genre Analysis ---")
    
    # Data often stores genres as a list or comma-separated string
    # Explode genres into individual rows for counting
    if 'genres' in df.columns:
        # Assuming genres is a list of strings
        s = df['genres'].dropna().apply(lambda g: g if isinstance(g, list) else []).explode()
        s = s[s != ""].dropna()
        s.name = 'genre'
        genre_df = df.drop('genres', axis=1).join(s)
        
        # 1. Most Common Genres
        genre_counts = genre_df['genre'].value_counts().head(10)
        
        # 2. Average Ratings by Genre
        avg_genre_rating = genre_df.groupby('genre')['vote_average'].mean().sort_values(ascending=False).head(10)

        # Visualization
        plt.figure(figsize=(12, 6))
        sns.barplot(x=genre_counts.values, y=genre_counts.index,
                    hue=genre_counts.index, palette="viridis", legend=False)
        plt.title('Top 10 Most Common Genres')
        plt.xlabel('Number of Movies')
        plt.savefig(os.path.join(output_dir, "genre_counts.png"))
        plt.close()

        return {
            "top_genre": genre_counts.index[0],
            "highest_rated_genre": avg_genre_rating.index[0]
        }
    return {}

def temporal_analysis(df: pd.DataFrame, output_dir: str):
    """Answers: Rating trends over time and Most productive years."""
    print("--- Running Temporal Analysis ---")
    
    # 1. Most productive years
    yearly_counts = df['year'].value_counts().sort_index()

    # 2. Rating trends (rolling average)
    yearly_ratings = df.groupby('year')['vote_average'].mean()

    # Visualization
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=yearly_ratings.index, y=yearly_ratings.values, marker='o', color='teal')
    plt.title('Average TMDB Rating Trend Over Years')
    plt.xlabel('Year')
    plt.ylabel('Avg Rating')
    plt.savefig(os.path.join(output_dir, "temporal_trends.png"))
    plt.close()

    return {"most_productive_year": int(yearly_counts.idxmax())}

def generate_summary_report(stats: dict):
    """Prints a consolidated summary report to the console."""
    print("\n" + "="*30)
    print("   MOVIE DATA SUMMARY REPORT")
    print("="*30)
    corr = stats.get('rating_correlation')
    corr_str = f"{corr:.2f}" if corr is not None else "N/A (no Letterboxd data)"
    print(f"Platform Correlation:  {corr_str}")
    print(f"Dominant Genre:        {stats.get('top_genre', 'N/A')}")
    print(f"Highest Rated Genre:   {stats.get('highest_rated_genre', 'N/A')}")
    print(f"Most Productive Year:  {stats.get('most_productive_year', 'N/A')}")
    print("="*30)
    print("Visualizations saved to 'data/reports/visuals/'")

if __name__ == "__main__":
    # Setup paths
    processed_file = "data/processed/movies_processed.json"
    output_viz_dir = "data/reports/visuals/"
    if not os.path.exists(output_viz_dir):
        os.makedirs(output_viz_dir)

    # Run Pipeline
    df_movies = load_processed_data(processed_file)
    
    if not df_movies.empty:
        summary_stats = {}
        
        # Execute analyses
        summary_stats.update(rating_analysis(df_movies, output_viz_dir))
        summary_stats.update(genre_analysis(df_movies, output_viz_dir))
        summary_stats.update(temporal_analysis(df_movies, output_viz_dir))
        
        # Report
        generate_summary_report(summary_stats)
    else:
        print("Analysis failed: No data found.")
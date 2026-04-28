'''
analyze_data.py - analysis

1. Loads processed movie data from CSV
2. Conducts rating analysis (correlation/distribution between TMDB and Letterboxd)
3. Conducts genre analysis (most common genres and average ratings by genre)
4. Conducts temporal analysis (rating trends and most productive years)
5. Generate 4 visualizations
6. Generate summary report

Key Functions:
def load_processed_data() -> pd.DataFrame
def rating_analysis(df) -> List[Dict]
def genre_analysis(df) -> List[Dict]
def temporal_analysis(df) -> List[Dict]
def generate_visualizations(df: pd.DataFrame)
def generate_summary(rating_results: Dict, genre_results: Dict, temporal_results: Dict)
def run_pipeline()
'''

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import logging
from typing import Dict, List

class DataAnalyzer:
    def __init__(self):
        os.makedirs('logs', exist_ok=True)
        os.makedirs(os.path.join('data', 'processed'), exist_ok=True)
        os.makedirs(os.path.join('data', 'analysis'), exist_ok=True)

        logging.basicConfig(
            filename=os.path.join('logs', 'analyze_data.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_processed_data(self) -> pd.DataFrame:
        """Load processed movie data from CSV"""
        filepath = os.path.join('data', 'processed', 'processed_movies.csv')
        try:
            df = pd.read_csv(filepath)
            logging.info(f'Loaded processed data: {len(df)} records')
            return df
        except Exception as e:
            logging.error(f'Error loading processed data: {e}')
            return pd.DataFrame()
        
    def rating_analysis(self, df) -> Dict:
        """Analyze correlation and distribution between TMDB and Letterboxd ratings"""
        results = {}

        if 'tmdb_rating' not in df.columns or 'letterboxd_rating' not in df.columns:
            logging.warning('Rating columns missing, skipping rating analysis')
            return results

        dist_df = df.copy()
        try:
            #Analyze correlation
            corr = dist_df['tmdb_rating'].corr(dist_df['letterboxd_rating'])
            results['correlation'] = round(corr,3)

            #Analyze distribution by statistical values
            stat_labels = dist_df['tmdb_rating'].describe().index.tolist()
            tmdb_stats = dist_df['tmdb_rating'].describe().values.tolist()
            letterboxd_stats = dist_df['letterboxd_rating'].describe().values.tolist()
            for i, stat in enumerate(stat_labels):
                results[f'tmdb_{stat}'] = round(tmdb_stats[i],3)
                results[f'letterboxd_{stat}'] = round(letterboxd_stats[i],3)
            logging.info(f'Successfully analyzed TMDB vs Letterboxd distributions: r={corr:.3f}.')
            return results
        except Exception as e:
            logging.error(f'Error analyzing ratings: {e}')
            return results
    
    def genre_analysis(self, df) -> Dict:
        """Analyze most common genres and average ratings by genre"""
        results = {}

        if 'genres' not in df.columns:
            logging.warning('Genre column missing, skipping genre analysis')
            return results
        
        genre_df = df.copy()

        #Clean genres column for genre analysis
        try:
            #Convert comma-separated string to list for explode                                                                                                                           
            genre_df['genres'] = genre_df['genres'].apply(            
                lambda x: x.split(', ') if isinstance(x, str) else x                                                                                                                      
            )
            #Explode genre list to rows of subset columns -> one row per movie-genre pair
            genre_df = genre_df.explode('genres') 

            #Extract genre name from each genre dictionary
            genre_df['genre_name'] = genre_df['genres'].apply(
                lambda x: x.get('name') if isinstance(x,dict) else x
            )

            #Drop rows with missing/empty genres
            genre_df = genre_df.dropna(subset=['genre_name'])
        except Exception as e:
            logging.error(f'Error cleaning genres column for genre analysis: {e}')
            return results

        #Genre analysis

        #Analyze most common genres
        try:
            genre_counts = genre_df['genre_name'].value_counts()
            results['top_genres'] = genre_counts.head(10).to_dict()
            logging.info(f'Successfully analyzed top genres')
        except Exception as e:
            logging.error(f'Error analyzing top genres: {e}')
            return results
        
        #Analyze average ratings by genre
        if 'tmdb_rating' not in df.columns or 'letterboxd_rating' not in df.columns:
            logging.warning('Rating columns missing, skipping average ratings by genre analysis')
            return results
        try:
            tmdb_ave = genre_df.groupby('genre_name')['tmdb_rating'].mean().sort_values(ascending=False)
            letterboxd_ave = genre_df.groupby('genre_name')['letterboxd_rating'].mean().sort_values(ascending=False)
            results['avg_tmdb_by_genre'] = tmdb_ave.round(3).to_dict()
            results['avg_letterboxd_by_genre'] = letterboxd_ave.round(3).to_dict()
            logging.info(f'Successfully analyzed average ratings by genre')
            return results
        except Exception as e:
            logging.error(f'Error analyzing average rating by genre: {e}')
            return results

    def temporal_analysis(self, df) -> List[Dict]:
        """Analyze rating trends over time and most productive years"""
        results = {}

        if 'release_year' not in df.columns:
            logging.warning('Release year column missing, skipping temporal analysis')
            return results

        temp_df = df.copy()

        #Filter to rows with a valid release year
        try:
            temp_df = temp_df[temp_df['release_year'].notna()]
            temp_df['release_year'] = temp_df['release_year'].astype(int)
        except Exception as e:
            logging.error(f'Error cleaning release_year column for temporal analysis: {e}')
            return results

        #Start temporal analysis
        movies_per_yr = temp_df['release_year'].value_counts().sort_index()
        if 'tmdb_rating' not in df.columns or 'letterboxd_rating' not in df.columns:
            logging.warning('Rating columns missing, skipping average rating trends analysis')
            return results
        try:
            tmdb_by_yr = temp_df.groupby('release_year')['tmdb_rating'].mean().round(3)
            letterboxd_by_yr = temp_df.groupby('release_year')['letterboxd_rating'].mean().round(3)
            results['tmdb_rating_by_year'] = tmdb_by_yr.to_dict()
            results['letterboxd_rating_by_year'] = letterboxd_by_yr.to_dict()
            results['most_productive_year'] = int(movies_per_yr.idxmax())
            logging.info(f'Temporal analysis: {len(movies_per_yr)} years covered')
            return results
        except Exception as e:
            logging.error(f'Error analyzing temporal trends: {e}')
            return results
        
    def generate_visualizations(self, df: pd.DataFrame):
        """Generate visualizations"""

        #Visualization 1: rating distributions side by side
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        if 'tmdb_rating' in df.columns:
            df['tmdb_rating'].dropna().hist(bins=20, ax=axes[0], color='steelblue', edgecolor='white')
            axes[0].set_title('TMDB Rating Distribution')
            axes[0].set_xlabel('Rating (0-10)')
            axes[0].set_ylabel('Count')

        if 'letterboxd_rating' in df.columns:
            df['letterboxd_rating'].dropna().hist(bins=20, ax=axes[1], color='goldenrod', edgecolor='white')
            axes[1].set_title('Letterboxd Rating Distribution')
            axes[1].set_xlabel('Rating (0-5)')
            axes[1].set_ylabel('Count')

        plt.tight_layout()
        path = os.path.join('data', 'analysis','rating_distributions.png')
        try:
            plt.savefig(path)
            logging.info(f'Saved rating distribution visualization: {path}')
        except Exception as e:
            logging.error(f'Error saving {path}: {e}')
        plt.close()

        #Visualization 2: TMDB vs Letterboxd rating correlation
        if 'tmdb_rating' in df.columns and 'letterboxd_rating' in df.columns:
            scatter_df = df[['tmdb_rating','letterboxd_rating']].dropna()
            plt.figure(figsize=(8, 6))
            plt.scatter(scatter_df['tmdb_rating'], scatter_df['letterboxd_rating'], alpha=0.5, color='steelblue')
            plt.xlabel('TMDB Rating (0-10)')
            plt.ylabel('Letterboxd Rating (0-5)')
            plt.title('TMDB vs Letterboxd Rating Correlation')
            path = os.path.join('data', 'analysis','rating_correlation.png')
            try:
                plt.savefig(path)
                logging.info(f'Saved visualization: {path}')
            except Exception as e:
                logging.error(f'Error saving {path}: {e}')
            plt.close()
        
        #Visualization 3: most common genres bar plot
        genre_results = self.genre_analysis(df)
        top_genres = genre_results.get('top_genres', {})
        if top_genres:
            plt.figure(figsize=(10, 6))
            plt.bar(top_genres.keys(), top_genres.values(), color='steelblue', edgecolor='white')
            plt.title('Most Common Genres')
            plt.xlabel('Genre')
            plt.ylabel('Number of Movies')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            path = os.path.join('data', 'analysis','genre_distribution.png')
            try:
                plt.savefig(path)
                logging.info(f'Saved visualization: {path}')
            except Exception as e:
                logging.error(f'Error saving {path}: {e}')
            plt.close()

        #Visualization 4: average TMDB and Letterboxd ratings by year
        temporal_results = self.temporal_analysis(df)
        tmdb_by_yr = temporal_results.get('tmdb_rating_by_year', {})
        letterboxd_by_yr = temporal_results.get('letterboxd_rating_by_year', {})
        if tmdb_by_yr or letterboxd_by_yr:
            plt.figure(figsize=(12, 5))
            if tmdb_by_yr:
                plt.plot(list(tmdb_by_yr.keys()), list(tmdb_by_yr.values()), color='steelblue', marker='o', markersize=4, label='TMDB (0-10)')
            if letterboxd_by_yr:
                plt.plot(list(letterboxd_by_yr.keys()), list(letterboxd_by_yr.values()), color='goldenrod', marker='o', markersize=4, label='Letterboxd (0-5)')
            plt.title('Average Ratings by Year')
            plt.xlabel('Year')
            plt.ylabel('Average Rating')
            plt.legend()
            plt.tight_layout()
            path = os.path.join('data', 'analysis','ratings_by_year.png')
            try:
                plt.savefig(path)
                logging.info(f'Saved visualization: {path}')
            except Exception as e:
                logging.error(f'Error saving {path}: {e}')
            plt.close()

    
    def generate_summary(self, rating_results: Dict, genre_results: Dict, temporal_results: Dict):
        """Generate summary report"""
        lines = [
            'Movie Data Analysis - Summary Report',
            '=' * 40,
            '',
            '--- Rating Analysis ---',
        ]

        if rating_results:
            lines += [
                f"TMDB mean rating:            {rating_results.get('tmdb_mean', 'N/A')}",
                f"Letterboxd mean rating:      {rating_results.get('letterboxd_mean', 'N/A')}",
                f"TMDB std deviation:          {rating_results.get('tmdb_std', 'N/A')}",
                f"Letterboxd std deviation:    {rating_results.get('letterboxd_std', 'N/A')}",
                f"TMDB-Letterboxd correlation: {rating_results.get('correlation', 'N/A')}",
            ]

        lines += ['', '--- Genre Analysis ---']

        if genre_results:
            top_genres = genre_results.get('top_genres', {})
            if top_genres:
                top_genre = list(top_genres.keys())[0]
                lines.append(f"Most common genre: {top_genre} ({top_genres[top_genre]} movies)")
                lines.append('Top 5 genres by count:')
                for genre, count in list(top_genres.items())[:5]:
                    lines.append(f"  {genre}: {count}")
            avg_tmdb = genre_results.get('avg_tmdb_by_genre', {})
            if avg_tmdb:
                top_rated = list(avg_tmdb.keys())[0]
                lines.append(f"Highest rated genre (TMDB avg): {top_rated} ({avg_tmdb[top_rated]})")
            avg_letterboxd = genre_results.get('avg_letterboxd_by_genre', {})
            if avg_letterboxd:
                top_rated_letterboxd = list(avg_letterboxd.keys())[0]
                lines.append(f"Highest rated genre (Letterboxd avg): {top_rated_letterboxd} ({avg_letterboxd[top_rated_letterboxd]})")

        lines += ['', '--- Temporal Analysis ---']

        if temporal_results:
            most_productive = temporal_results.get('most_productive_year')
            if most_productive:
                lines.append(f"Most productive year: {most_productive}")
            tmdb_by_yr = temporal_results.get('tmdb_rating_by_year', {})
            if tmdb_by_yr:
                best_yr = max(tmdb_by_yr, key=tmdb_by_yr.get)
                lines.append(f"Highest rated year (TMDB avg): {best_yr} ({tmdb_by_yr[best_yr]})")
            letterboxd_by_yr = temporal_results.get('letterboxd_rating_by_year', {})
            if letterboxd_by_yr:
                best_yr_letterboxd = max(letterboxd_by_yr, key=letterboxd_by_yr.get)
                lines.append(f"Highest rated year (Letterboxd avg): {best_yr_letterboxd} ({letterboxd_by_yr[best_yr_letterboxd]})")

        report_path = os.path.join('data', 'analysis','summary_report.txt')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            logging.info(f'Saved summary report to {report_path}')
        except Exception as e:
            logging.error(f'Error saving summary report: {e}')

    def run_analysis(self, num_items: int = 50):
        """Run data analysis pipeline"""
        df = self.load_processed_data()
        if df.empty:
            logging.error('No data loaded to analyze, interrupting pipeline run')
            return

        rating_results = self.rating_analysis(df)
        genre_results = self.genre_analysis(df)
        temporal_results = self.temporal_analysis(df)

        self.generate_visualizations(df)
        self.generate_summary(rating_results, genre_results, temporal_results)

        logging.info('Pipeline completed successfully')

if __name__ == '__main__':                                                                                                                                                                      
    DataAnalyzer().run_analysis()     
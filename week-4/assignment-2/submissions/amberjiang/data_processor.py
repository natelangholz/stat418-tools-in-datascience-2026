'''
data_processor.py - data processing

1. Loads data from both sources
2. Merges data on common identifiers (movie title and year)
3. Cleans and validates data
4. Handles missing values appropriately
5. Standardizes formats (dates, ratings)
6. Removes duplicates
7. Saves processed data as CSV and JSON

Key Functions:
def load_raw_data() -> Tuple[List[Dict], List[Dict]]
def merge_data(tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame
def clean_data(df: pd.DataFrame) -> pd.DataFrame
def save_processed_data(df: pd.DataFrame, output_dir: str)
'''

import pandas as pd
import json
import os 
import logging
from typing import Dict, List, Tuple

class DataProcessor:
    def __init__(self):
        os.makedirs('logs', exist_ok=True)
        os.makedirs(os.path.join('data', 'raw', 'tmdb'), exist_ok=True)
        os.makedirs(os.path.join('data', 'raw', 'letterboxd'), exist_ok=True)
        os.makedirs(os.path.join('data', 'processed'), exist_ok=True)

        logging.basicConfig(
            filename=os.path.join('logs', 'data_processor.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def load_raw_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Load raw TMDB and Letterboxd data from JSON files"""

        tmdb_path = os.path.join('data', 'raw', 'tmdb', 'tmdb_movie_data.json')
        letterboxd_path = os.path.join('data', 'raw', 'letterboxd', 'letterboxd_scraped_data.json')

        #Load data from TMDB 
        try:
            with open(tmdb_path, 'r', encoding = 'utf-8') as f:
                tmdb_data = json.load(f)
            logging.info(f'Successfully loaded TMDB data: {len(tmdb_data)} records')
        except Exception as e:
            logging.error(f'Error loading TMDB data: {e}')
            tmdb_data = []
        
        #Load data from Letterboxd
        try:
            with open(letterboxd_path, 'r', encoding = 'utf-8') as f:
                letterboxd_data = json.load(f)
            logging.info(f'Successfully loaded Letterboxd data: {len(letterboxd_data)} records')
        except Exception as e:
            logging.error(f'Error loading Letterboxd data: {e}')
            letterboxd_data = []
        
        return tmdb_data, letterboxd_data
    
    def merge_data(self, tmdb_data: List[Dict], letterboxd_data: List[Dict]) -> pd.DataFrame:
        """Merge TMDB and Letterboxd data on title and release year"""
        tmdb_rows = []
        for movie in tmdb_data:
            name = movie.get('name',{})
            details = movie.get('details',{})
            credits = movie.get('credits',{})

            crew = credits.get('crew',[])
            director = next((cr.get('name') for cr in crew if cr.get('job') == 'Director'),None)

            cast = credits.get('cast', [])
            top_cast = ', '.join(ca.get('name','') for ca in cast[:3])

            genres = ', '.join(g.get('name','') for g in details.get('genres',[]))

            release_date = details.get('release_date')
            release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None

            row = {
                'tmdb_id': details.get('id'),
                'title': details.get('title'),
                'release_year': release_year,
                'release_date': release_date,
                'runtime': details.get('runtime'),
                'tmdb_rating': details.get('vote_average'),
                'tmdb_vote_count': details.get('vote_count'),
                'budget': details.get('budget'),
                'revenue': details.get('revenue'),
                'genres': genres,
                'overview': details.get('overview'),
                'director': director,
                'top_cast': top_cast,
                'popularity': details.get('popularity'),
            }
            tmdb_rows.append(row)

        tmdb_df = pd.DataFrame(tmdb_rows)
        letterboxd_df = pd.DataFrame(letterboxd_data)
        letterboxd_df = letterboxd_df.rename(columns={'year': 'release_year'})
        merged_df = tmdb_df.merge(letterboxd_df, on=['title', 'release_year'], how='left')
        logging.info(f'Merged TMDB and Letterboxd data: {len(merged_df)} records')

        return merged_df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate merged data"""
        initial_count = len(df)

        #Remove duplicates on title and release year
        df = df.drop_duplicates(subset=['title', 'release_year'])
        logging.info(f'Removed {initial_count - len(df)} duplicate records')

        #Drop records with no title
        df = df.dropna(subset=['title'])

        #Standardize release date to datetime
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

        #Standardize ratings to float
        df['tmdb_rating'] = pd.to_numeric(df['tmdb_rating'], errors='coerce').clip(0,10)
        if 'rating' in df.columns:
            df = df.rename(columns={'rating': 'letterboxd_rating'})
            df['letterboxd_rating'] = pd.to_numeric(df['letterboxd_rating'], errors='coerce').clip(0,5)

        #Handle missing values
        df['budget'] = df['budget'].replace(0, None)
        df['revenue'] = df['revenue'].replace(0, None)
        df['director'] = df['director'].fillna('Unknown')
        df['overview'] = df['overview'].fillna('')
        df['top_cast'] = df['top_cast'].fillna('')

        #Rename fan count
        if 'num_fans' in df.columns:
            df = df.rename(columns={'num_fans': 'letterboxd_fans'})

        #Drop rows that failed scraping and remove flag column
        if 'scraped_successfully' in df.columns:
            df = df[df['scraped_successfully'] != False]
            df = df.drop(columns=['scraped_successfully'])

        #Ensure numeric runtime
        df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')

        logging.info(f'Cleaned and validated data: {len(df)} records remaining')
        return df
        
    def save_processed_data(self, df: pd.DataFrame, output_dir: str = os.path.join('data', 'processed')):
        """Save processed data as CSV and JSON"""
        os.makedirs(output_dir, exist_ok=True)

        csv_path = os.path.join(output_dir, 'processed_movies.csv')
        json_path = os.path.join(output_dir, 'processed_movies.json')

        try:
            df.to_csv(csv_path, index=False)
            logging.info(f'Saved processed data to {csv_path}: {len(df)} records')
        except Exception as e:
            logging.error(f'Error saving to CSV: {e}')

        try:
            df_json = df.copy()
            if 'release_date' in df_json.columns:
                df_json['release_date'] = df_json['release_date'].astype(str) # convert datetime to string for JSON
            df_json.to_json(json_path, orient='records', indent=4)
            logging.info(f'Saved processed data to {json_path}: {len(df)} records')
        except Exception as e:
            logging.error(f'Error saving to JSON: {e}')

if __name__ == '__main__':                                                                                                                                                                      
    processor = DataProcessor()
    tmdb_data, letterboxd_data = processor.load_raw_data()
    df = processor.merge_data(tmdb_data=tmdb_data, letterboxd_data=letterboxd_data)
    cleaned_df = processor.clean_data(df=df)                                                                                                                                                    
    processor.save_processed_data(df=cleaned_df)

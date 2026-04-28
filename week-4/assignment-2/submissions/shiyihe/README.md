# Assignment 2: Movie Data Collection & Analysis Pipeline

## Overview

This project builds a simple movie data collection and analysis pipeline. The pipeline collects movie data from the TMDB API and an IMDb-related movie dataset, processes the raw data, and generates basic analysis results and visualizations.

The goal is to practice API data collection, web data collection, data cleaning, and simple exploratory analysis.

## Data Sources

### TMDB API
The TMDB API was used to collect popular movie data, including movie title, release date, rating, vote count, and popularity.

### IMDb-related Movie Dataset
An IMDb-related movie dataset was collected from a public movie dataset source. It includes movie title, genre, year, score, votes, budget, and gross revenue.

## Setup Instructions

Create a `.env` file in the project folder:

```bash
TMDB_API_KEY=your_tmdb_api_key_here

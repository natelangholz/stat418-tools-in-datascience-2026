# Furniture Product Launch Advisor

This project is a data and machine learning application that predicts whether an IKEA furniture product is likely to receive high consumer interest.

The project collects real product data from IKEA, trains a machine learning model, and exposes the model through a deployed Streamlit web app and a deployed FastAPI endpoint.

## Deployed Services

Streamlit App:

https://ikea-advisor.streamlit.app/

FastAPI Model API:

https://ikea-product-interest-api.onrender.com

FastAPI Docs:

https://ikea-product-interest-api.onrender.com/docs

## Project Motivation

Furniture retailers manage large product catalogs, but it is difficult to know which products will attract consumer interest before launch.

This project uses observable product-level features such as price, category, rating, and product page information to estimate whether a furniture product is likely to receive high customer engagement.

The final application is designed as a product launch decision-support tool. It helps users evaluate launch risk, compare products against category benchmarks, and test pricing scenarios.

## Data Collection

Data was collected from IKEA US product category pages and product detail pages using Python web scraping.

Main data collection steps:

1. Scrape IKEA category pages to collect product URLs.
2. Visit individual product detail pages.
3. Extract product name, category, price, rating, review count, and page text length.
4. Save the raw and cleaned datasets as CSV files.

Final dataset summary:

* Products: 398
* Product categories: 10
* Median review count: 168
* Average rating: 4.32

## Target Definition

Consumer interest is not directly observable from IKEA product pages, so this project uses review count as a proxy for customer engagement.

The binary target variable is defined as:

high_interest = 1 if review_count is above the dataset median

high_interest = 0 otherwise

This creates a balanced classification problem and avoids using review count directly as a model feature.

## Feature Engineering

The final model uses these features:

* category
* price
* rating
* name_length
* page_text_length

The category feature is one-hot encoded. Numerical features are used by the model after preprocessing.

## Modeling

Two models were compared:

1. Logistic Regression

Accuracy: 0.82

Precision: 0.804

Recall: 0.84

F1: 0.82

2. Random Forest

Accuracy: 0.89

Precision: 0.88

Recall: 0.90

F1: 0.889

The Random Forest model performed best on the held-out test set.

Test set summary:

* Test set size: 100 products
* Correct predictions: 89
* False positives: 6
* False negatives: 5

## Model Interpretability

Random Forest feature importance showed that the strongest predictors were:

1. price
2. page_text_length
3. rating

Page text length may act as a proxy for product maturity and information richness because more established products often have more detailed descriptions and customer-facing content.

## Application Features

The deployed Streamlit app includes:

* Product interest prediction
* 0 to 100 interest score
* Category benchmark comparison
* Business recommendation
* Pricing what-if analysis
* Price sensitivity analysis

The interest score is calculated as:

Interest Score = predicted probability of high-interest class times 100

For example, if the model predicts a 0.73 probability of high interest, the app displays an interest score of 73.

## API Usage

Health check:

curl https://ikea-product-interest-api.onrender.com/health

Prediction example:

curl -X POST "https://ikea-product-interest-api.onrender.com/predict" 
-H "Content-Type: application/json" 
-d '{"category":"bookcases","price":79,"rating":4.6,"name_length":3,"page_text_length":2400}'

Example response:

{
"prediction": "high_interest",
"probability_high_interest": 0.951243696990786,
"interest_score": 95
}

## Solution Architecture

The solution has two main parts.

Training pipeline:

1. IKEA website
2. BeautifulSoup scraper
3. Cleaned product dataset
4. Feature engineering
5. Random Forest model training
6. Saved model artifact

Deployed system:

1. User opens the Streamlit Cloud app
2. User enters product characteristics
3. Streamlit sends a prediction request to the FastAPI model API
4. FastAPI loads the trained Random Forest model
5. The API returns prediction JSON
6. Streamlit displays the interest score, benchmark information, and business recommendation

The architecture diagram is included in this directory as:

architecture_diagram.png

## How to Run Locally

Install dependencies:

pip install -r requirements.txt

Run the Streamlit app:

streamlit run app.py

Run the FastAPI service:

uvicorn api:app --reload

Open local API docs:

http://127.0.0.1:8000/docs

## Docker

A Dockerfile is included for containerizing the FastAPI model API.

Build the Docker image:

docker build -t ikea-product-interest-api .

Run the container:

docker run -p 8000:8000 ikea-product-interest-api

Then open:

http://127.0.0.1:8000/docs

## File Overview

Important files:

* ikea_final_scraper.py: collects product URLs from IKEA category pages
* product_page_scraper.py: scrapes product detail pages
* build_final_model_dataset.py: builds the final modeling dataset
* train_final_model.py: trains and evaluates machine learning models
* app.py: Streamlit web application
* api.py: FastAPI model endpoint
* ikea_interest_model.pkl: trained Random Forest model
* architecture_diagram.png: solution architecture diagram
* requirements.txt: Python dependencies
* Dockerfile: containerization file for the API

## AI Assistant Usage

AI assistants, including ChatGPT and Cursor, were used during development for:

* debugging web scraping failures
* identifying target leakage
* improving feature engineering ideas
* generating visualization code
* improving application design and business framing
* refining the final presentation structure

All final model evaluation, interpretation, and project decisions were manually reviewed and verified.

## Challenges and Lessons Learned

The first version of the project used rank_in_category to define the target and also included rank-based variables as model features. This caused target leakage and inflated model performance.

The target was later redefined using review count, and leakage-related features were removed.

The project also showed that business value comes not only from prediction accuracy, but from turning predictions into actionable recommendations. The final app focuses on product launch decisions, category benchmarking, and pricing analysis.

## Future Work

Future improvements include:

* collecting data from more furniture retailers
* using product images as model features
* predicting continuous review count instead of binary interest
* adding SHAP explanations
* improving pricing optimization
* adding automated testing and CI/CD


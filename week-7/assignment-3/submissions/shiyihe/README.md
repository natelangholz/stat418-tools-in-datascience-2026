# Assignment 3 - FastAPI ML Service

## Project Idea

For this assignment I built a small FastAPI application that serves a machine learning model.

I used the `mtcars` dataset and trained a simple Random Forest model to predict whether a car has relatively high MPG or not.

The API supports:
- single prediction
- batch prediction
- model info
- health checks
- API key authentication
- rate limiting

I also added a Dockerfile and deployment files for Cloud Run.

---

## Model

Dataset:
- mtcars.csv

Model:
- RandomForestClassifier

Features used:
- wt
- hp
- cyl

Target:
```text
high_mpg = 1 if mpg > median mpg

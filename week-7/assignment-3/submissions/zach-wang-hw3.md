# Assignment 3 — Zach Wang

**Course:** STAT 418 — Tools in Data Science (Spring 2026)

## Standalone Repository

[https://github.com/ArcherX0X/mtcars-fastapi-api](https://github.com/ArcherX0X/mtcars-fastapi-api)

## Deployed API

[https://mtcars-fastapi-api-886054929408.us-central1.run.app](https://mtcars-fastapi-api-886054929408.us-central1.run.app)

## Predictors Used

The model uses two predictors:

- `wt` — vehicle weight (1000 lbs)
- `hp` — gross horsepower

Response variable: `mpg` (miles per gallon)

Model: `LinearRegression` (scikit-learn), R² = 0.79

## Example API Call

```bash
curl -X POST "https://mtcars-fastapi-api-886054929408.us-central1.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "hp": 110}'
```

Response:

```json
{
  "predicted_mpg": 22.56,
  "predictors": {"wt": 2.62, "hp": 110.0}
}
```

# MTCARS FastAPI API

A containerized machine learning API that predicts vehicle fuel economy (`mpg`) from weight and horsepower using linear regression on the classic `mtcars` dataset.

Use this file as the main `README.md` when you copy the project to your **standalone GitHub repo**. Keep the course repo `README.md` as the assignment instructions.

## Model

- **Response:** `mpg` (miles per gallon)
- **Predictors:** `wt` (weight in 1000 lbs), `hp` (horsepower)
- **Algorithm:** scikit-learn `LinearRegression`
- **Artifact:** `models/model.pkl` (includes fitted model and feature metadata)

Retrain anytime with:

```bash
python scripts/train_model.py
```

## Repository structure

```text
├── app/main.py           # FastAPI application
├── models/model.pkl      # Trained model artifact
├── scripts/train_model.py
├── tests/test_api.py
├── mtcars.csv
├── Dockerfile
├── requirements.txt
└── submissions/          # Course repo submission link
```

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_model.py
python -m app.main
```

The API listens on `http://0.0.0.0:8080`. If port 8080 is in use, run:

```bash
PORT=8081 python -m app.main
```

## API endpoints

| Method | Path       | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/`        | API info and endpoint links          |
| GET    | `/health`  | Liveness check (API process running) |
| GET    | `/ready`   | Readiness check (model loaded)       |
| POST   | `/predict` | Predict `mpg` from `wt` and `hp`     |
| GET    | `/docs`    | Interactive OpenAPI documentation    |

### Example request

```bash
curl -X POST "http://localhost:8081/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "hp": 110}'
```

Example response:

```json
{"predicted_mpg": 23.57}
```

### Example health / ready

```bash
curl http://localhost:8081/health
curl http://localhost:8081/ready
```

Invalid input (wrong type or missing fields) returns HTTP `422` with validation details. If the model file is missing, `/ready` and `/predict` return HTTP `503`.

## Run with Podman

```bash
podman build -t mtcars-fastapi .
podman run --rm -p 8080:8080 mtcars-fastapi
```

## Deploy to Google Cloud Run

Prerequisites: [Google Cloud SDK](https://cloud.google.com/sdk/docs/install), a GCP project, and Artifact Registry enabled.

```bash
export PROJECT_ID=your-gcp-project
export REGION=us-central1
export IMAGE=mtcars-fastapi

gcloud auth configure-docker ${REGION}-docker.pkg.dev

podman build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/mtcars/${IMAGE}:latest .
podman push ${REGION}-docker.pkg.dev/${PROJECT_ID}/mtcars/${IMAGE}:latest

gcloud run deploy mtcars-fastapi \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/mtcars/${IMAGE}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080
```

**Deployed API URL:** `https://YOUR-SERVICE-URL.run.app` _(replace after deployment)_

## Configuration

| Variable     | Default              | Description        |
|--------------|----------------------|--------------------|
| `MODEL_PATH` | `models/model.pkl`   | Path to model file |
| `PORT`       | `8080`               | Uvicorn port       |

## Tests

```bash
pytest tests/ -v
```

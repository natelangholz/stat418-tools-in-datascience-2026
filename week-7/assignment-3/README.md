# MTCARS FastAPI API

A small, reproducible machine learning API that predicts vehicle fuel economy (`mpg`) from weight and horsepower using linear regression on the classic `mtcars` dataset.

This project includes the dataset, training workflow, saved model artifact, FastAPI application, automated tests, and a Podman-ready container build.

## Model

- **Response:** `mpg` (miles per gallon)
- **Predictors:** `wt` (vehicle weight in 1000 lbs) and `hp` (gross horsepower)
- **Algorithm:** scikit-learn `LinearRegression`
- **Training data:** `mtcars.csv`
- **Artifact:** `models/model.pkl`

Retrain the model with:

```bash
python scripts/train_model.py
```

## Repository Structure

```text
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── models/
│   └── model.pkl            # Trained model artifact
├── scripts/
│   └── train_model.py       # Reproducible training workflow
├── tests/
│   └── test_api.py          # API tests
├── mtcars.csv               # Dataset
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── submissions/             # Course submission markdown
```

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_model.py
python -m app.main
```

The API listens on `http://localhost:8080`. If port 8080 is in use, run:

```bash
PORT=8081 python -m app.main
```

## API Endpoints

| Method | Path       | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/`        | API info and endpoint links          |
| GET    | `/health`  | Liveness check                       |
| GET    | `/ready`   | Readiness check for loaded model     |
| POST   | `/predict` | Predict `mpg` from `wt` and `hp`     |
| GET    | `/docs`    | Interactive OpenAPI documentation    |

### Example Request

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "hp": 110}'
```

Example response:

```json
{"predicted_mpg": 23.57}
```

### Health and Readiness

```bash
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

Invalid input, such as missing predictors or wrong types, returns HTTP `422` with validation details. If the model file is unavailable, `/ready` and `/predict` return HTTP `503`.

## Run with Podman

```bash
podman build -t mtcars-fastapi .
podman run --rm -p 8080:8080 mtcars-fastapi
```

Then call:

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "hp": 110}'
```

## Deploy to Google Cloud Run

Prerequisites: Google Cloud SDK, a GCP project, Artifact Registry enabled, and a Docker/Podman credential helper configured for Google Artifact Registry.

Create an Artifact Registry repository once:

```bash
export PROJECT_ID=your-gcp-project
export REGION=us-central1

gcloud artifacts repositories create mtcars \
  --repository-format=docker \
  --location=${REGION} \
  --description="MTCARS FastAPI images"
```

Build, push, and deploy:

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

**Deployed API URL:** `https://mtcars-fastapi-854033632163.us-central1.run.app`

## Configuration

| Variable     | Default              | Description        |
|--------------|----------------------|--------------------|
| `MODEL_PATH` | `models/model.pkl`   | Path to model file |
| `PORT`       | `8080`               | Uvicorn port       |

## Tests

```bash
pytest tests/ -v
```

The tests cover `/health`, `/ready`, successful predictions, invalid input, missing fields, and missing model behavior.

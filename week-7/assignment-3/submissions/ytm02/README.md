# Assignment 3: Iris Species Classifier API

UCLA STAT418 — Yutong Ma (ytm02)

## Overview

A production-ready FastAPI application that serves a RandomForest classifier predicting Iris flower species from 4 measurements. Features API key authentication, rate limiting, batch predictions, health checks, and container deployment to Google Cloud Run.

## Model

- **Algorithm**: RandomForestClassifier (100 trees, sklearn)
- **Dataset**: UCI Iris (150 samples, 4 features, 3 classes)
- **Accuracy**: 100% on test set (30 samples)
- **Classes**: setosa, versicolor, virginica
- **Features**: sepal_length, sepal_width, petal_length, petal_width (all in cm)

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness check |
| GET | `/ready` | No | Readiness check (model loaded?) |
| GET | `/v1/model/info` | Yes | Model metadata |
| POST | `/v1/predict` | Yes | Single prediction (100/min) |
| POST | `/v1/predict/batch` | Yes | Batch prediction up to 100 (20/min) |

## Setup (Local)

### 1. Install dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set API_KEY
```

### 3. Run the API

```bash
uvicorn main:app --reload --port 8080
```

API docs available at: http://localhost:8080/docs

**Live deployment:** https://iris-classifier-api-589990931603.us-central1.run.app

## Authentication

Include the API key in every protected request as a header:

```
api-key: your_api_key_here
```

## Example Requests

### Health check
```bash
curl http://localhost:8080/health
```

### Single prediction
```bash
curl -X POST http://localhost:8080/v1/predict \
  -H "Content-Type: application/json" \
  -H "api-key: your_api_key_here" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

### Batch prediction
```bash
curl -X POST http://localhost:8080/v1/predict/batch \
  -H "Content-Type: application/json" \
  -H "api-key: your_api_key_here" \
  -d '{"instances": [[5.1,3.5,1.4,0.2],[6.3,3.3,6.0,2.5]]}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | (required) | Secret key for authentication |
| `MODEL_PATH` | `model.pkl` | Path to the serialized model |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MAX_BATCH_SIZE` | `100` | Max instances per batch request |
| `PORT` | `8080` | Port for the server |

## Testing

```bash
pytest tests/ -v --rootdir=.
```

All 15 tests pass covering: health, readiness, model info, single prediction, batch prediction, auth, and input validation.

## Container (Podman)

```bash
# Build
podman build -t iris-api .

# Run locally
podman run -p 8080:8080 -e API_KEY=test123 iris-api

# Test
curl http://localhost:8080/health
```

## Cloud Run Deployment

```bash
cd deployment
chmod +x deploy.sh
GCP_PROJECT_ID=your-project-id ./deploy.sh
```

See `deployment/deploy.sh` for full deployment steps.

## Directory Structure

```
submissions/ytm02/
├── main.py              # FastAPI app
├── models.py            # Pydantic request/response models
├── auth.py              # API key authentication
├── config.py            # Environment-based configuration
├── model.pkl            # Trained RandomForest model
├── requirements.txt
├── Dockerfile           # Multi-stage build
├── .dockerignore
├── .env.example
├── README.md
├── API_DOCUMENTATION.md
├── tests/
│   ├── conftest.py
│   └── test_api.py      # 15 tests, all passing
└── deployment/
    ├── deploy.sh
    └── cloud-run-config.yaml
```

## Known Limitations

- Iris dataset is small (150 samples); real production models need larger datasets
- Cloud Run cold starts may cause latency on first request
- CORS is set to `allow_origins=["*"]` — restrict in production

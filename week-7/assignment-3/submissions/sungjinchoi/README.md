# Player Market Value API

Production FastAPI service that predicts soccer player market values from
performance stats. Containerized with Podman, deployed to Google Cloud Run.

**Live service:** https://market-value-api-348858993647.us-central1.run.app
Interactive docs: https://market-value-api-348858993647.us-central1.run.app/docs

## Model

RandomForest regressor trained on 2,013 players from the top 5 European
leagues (market values EUR 50k to EUR 200M).

- **Target:** log market value
- **Features (7):** age, appearances, goals, assists, minutes, yellow_cards, red_cards
- **Test R2:** 0.59
- **Test MAE:** EUR 8.25M

Confidence is derived from the spread of the RandomForest trees: when the
trees agree, confidence is near 1.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | no | Liveness check |
| GET | `/ready` | no | Readiness check (503 until model loaded) |
| POST | `/v1/predict` | yes | Single prediction |
| POST | `/v1/predict/batch` | yes | Batch prediction (max 100) |
| GET | `/v1/model/info` | yes | Model metadata |

Interactive docs are served at `/docs`.

## Setup (Local)

```bash
uv pip install -r requirements.txt

cp .env.example .env
# edit .env and set API_KEY

python train_model.py        # produces model.pkl
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

## Authentication

Protected endpoints require an `api-key` header matching the `API_KEY`
environment variable.

- Missing header -> `403`
- Wrong key -> `401`

## Example Requests

### curl

```bash
curl -X POST http://localhost:8000/v1/predict \
  -H "Content-Type: application/json" \
  -H "api-key: your_api_key" \
  -d '{"features": [24, 38, 12, 7, 3100, 4, 0]}'
```

Response:

```json
{
  "prediction": 52340000.0,
  "confidence": 0.83,
  "model_version": "v1.0",
  "request_id": "f1c2..."
}
```

### Python

```python
import requests

resp = requests.post(
    "http://localhost:8000/v1/predict",
    headers={"api-key": "your_api_key"},
    json={"features": [24, 38, 12, 7, 3100, 4, 0]},
)
print(resp.json())
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `changeme` | Key required for protected endpoints |
| `MODEL_PATH` | `model.pkl` | Path to the model bundle |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_BATCH_SIZE` | `100` | Max instances per batch request |
| `PORT` | `8080` | Port the server binds to |

## Testing

```bash
pytest tests/ -v
```

Covers all endpoints: health, readiness, auth, validation, single and
batch prediction, model info.

## Containerization

```bash
# Build
podman build -t market-value-api .

# Run locally
podman run -p 8080:8080 -e API_KEY=test123 market-value-api

# Test
curl http://localhost:8080/health
```

The Dockerfile uses a multi-stage build (Python 3.11-slim, `uv` for
installs) and runs as a non-root user.

## Deployment (Cloud Run)

```bash
# 1. Store the API key in Secret Manager
echo -n "your_api_key" | gcloud secrets create market-value-api-key --data-file=-

# 2. Build, push, and deploy
PROJECT_ID=your-project ./deployment/deploy.sh
```

The deploy script builds with Podman, pushes to GCR, and deploys to Cloud
Run with 2Gi memory, 2 CPU, max 10 instances, and the API key pulled from
Secret Manager.

## Project Structure

```
.
├── main.py                  FastAPI application
├── models.py                Pydantic request/response models
├── auth.py                  API key authentication
├── config.py                Settings from environment
├── train_model.py           Trains and saves model.pkl
├── model.pkl                Trained model bundle
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
├── tests/test_api.py
└── deployment/
    ├── deploy.sh
    └── cloud-run-config.yaml
```

## Known Limitations

- The model explains ~59% of value variance. Market value also depends on
  contract length, reputation, and transfer rumors, which are not features here.
- Trained only on top-5-league players. Predictions outside that population
  (other leagues, youth players) are unreliable.
- Confidence reflects model agreement, not a calibrated probability.

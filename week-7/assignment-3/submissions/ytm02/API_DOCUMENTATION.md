# API Documentation — Iris Species Classifier

Base URL (local): `http://localhost:8080`  
Base URL (Cloud Run): `https://iris-classifier-api-589990931603.us-central1.run.app`

---

## Authentication

Protected endpoints require an API key in the request header:

```
api-key: <your_api_key>
```

Missing header → `422 Unprocessable Entity`  
Wrong key → `401 Unauthorized`

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| POST `/v1/predict` | 100 requests/minute per IP |
| POST `/v1/predict/batch` | 20 requests/minute per IP |

Exceeded → `429 Too Many Requests`

---

## Endpoints

### GET /health
Liveness probe — no auth required.

**Response 200:**
```json
{"status": "healthy"}
```

---

### GET /ready
Readiness probe — returns 503 if model is not loaded.

**Response 200:**
```json
{"status": "ready", "model_loaded": true}
```

**Response 503:**
```json
{"detail": "Model not loaded"}
```

---

### GET /v1/model/info
Returns metadata about the loaded model. Requires auth.

**Response 200:**
```json
{
  "name": "RandomForestClassifier",
  "version": "v1.0",
  "description": "Iris species classifier trained on the UCI Iris dataset (150 samples).",
  "features": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
  "classes": ["setosa", "versicolor", "virginica"],
  "accuracy": 1.0
}
```

---

### POST /v1/predict
Predict species for a single flower measurement. Requires auth.

**Request body:**
```json
{
  "features": [5.1, 3.5, 1.4, 0.2],
  "model_version": "v1"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `features` | `float[]` | Yes | Exactly 4 non-negative values (sepal_length, sepal_width, petal_length, petal_width) |
| `model_version` | `string` | No | Defaults to `"v1"` |

**Response 200:**
```json
{
  "prediction": 0.0,
  "predicted_class": "setosa",
  "confidence": 1.0,
  "model_version": "v1.0",
  "request_id": "a1b2c3d4-..."
}
```

**Error responses:**
- `401` — Invalid API key
- `422` — Wrong number of features, negative values, or missing field
- `503` — Model not loaded

---

### POST /v1/predict/batch
Predict species for multiple flowers at once. Max 100 instances. Requires auth.

**Request body:**
```json
{
  "instances": [
    [5.1, 3.5, 1.4, 0.2],
    [6.3, 3.3, 6.0, 2.5],
    [5.9, 3.0, 4.2, 1.5]
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instances` | `float[][]` | Yes | 1–100 arrays, each with exactly 4 features |

**Response 200:**
```json
{
  "predictions": [0.0, 2.0, 1.0],
  "predicted_classes": ["setosa", "virginica", "versicolor"],
  "count": 3,
  "model_version": "v1.0"
}
```

**Error responses:**
- `401` — Invalid API key
- `422` — Empty list, wrong feature count, or batch > 100
- `503` — Model not loaded

---

## Error Codes Summary

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Invalid or missing API key |
| 422 | Input validation failed |
| 429 | Rate limit exceeded |
| 500 | Internal prediction error |
| 503 | Model not loaded |

---

## Interactive Docs

FastAPI auto-generates interactive documentation:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

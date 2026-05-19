# API Documentation

Base URL (local): `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI), `/redoc`

## Authentication

Protected endpoints require an `api-key` header.

```
api-key: your_api_key
```

| Situation | Status | Body |
|-----------|--------|------|
| Header missing | `403` | `{"detail": "Missing API key"}` |
| Wrong key | `401` | `{"detail": "Invalid API key"}` |
| Valid key | `200` | endpoint response |

## Rate Limiting

Limits are applied per client IP.

| Endpoint | Limit |
|----------|-------|
| `/v1/predict` | 100 / minute |
| `/v1/predict/batch` | 20 / minute |

Exceeding a limit returns `429 Too Many Requests`.

## Feature Vector

All prediction endpoints take a 7-value feature vector, in this exact order:

| Index | Feature | Description |
|-------|---------|-------------|
| 0 | age | Player age in years |
| 1 | appearances | Matches played this season |
| 2 | goals | Goals scored |
| 3 | assists | Assists |
| 4 | minutes | Minutes played |
| 5 | yellow_cards | Yellow cards |
| 6 | red_cards | Red cards |

All values must be non-negative.

---

## GET /health

Liveness probe. No authentication.

**Response `200`**

```json
{"status": "healthy"}
```

---

## GET /ready

Readiness probe. No authentication. Returns `503` until the model is loaded.

**Response `200`**

```json
{"status": "ready"}
```

**Response `503`**

```json
{"detail": "Model not loaded"}
```

---

## POST /v1/predict

Single prediction. Requires authentication.

**Request body**

```json
{
  "features": [24, 38, 12, 7, 3100, 4, 0],
  "model_version": "v1"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| features | float[7] | yes | See feature vector above |
| model_version | string | no | Defaults to `v1` |

**Response `200`**

```json
{
  "prediction": 52340000.0,
  "confidence": 0.83,
  "model_version": "v1.0",
  "request_id": "f1c2e8a0-..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| prediction | float | Predicted market value in EUR |
| confidence | float | Tree-agreement score in [0, 1] |
| model_version | string | Model version that served the request |
| request_id | string | Unique ID for tracing/logging |

---

## POST /v1/predict/batch

Batch prediction. Requires authentication. Max 100 instances.

**Request body**

```json
{
  "instances": [
    [24, 38, 12, 7, 3100, 4, 0],
    [29, 30, 2, 4, 2400, 6, 1]
  ]
}
```

**Response `200`**

```json
{
  "predictions": [52340000.0, 18750000.0],
  "count": 2,
  "model_version": "v1.0"
}
```

---

## GET /v1/model/info

Model metadata. Requires authentication.

**Response `200`**

```json
{
  "model_version": "v1.0",
  "model_type": "RandomForestRegressor",
  "target": "log_market_value",
  "features": ["age", "appearances", "goals", "assists", "minutes", "yellow_cards", "red_cards"],
  "n_features": 7,
  "n_train": 1610,
  "metrics": {"r2": 0.59, "mae_eur": 8250000.0}
}
```

---

## Error Codes

| Status | Meaning | Example cause |
|--------|---------|---------------|
| `200` | Success | — |
| `401` | Unauthorized | Wrong API key |
| `403` | Forbidden | Missing `api-key` header |
| `422` | Validation error | Wrong feature count, negative value, batch > 100 |
| `429` | Too many requests | Rate limit exceeded |
| `500` | Internal error | Prediction failure |
| `503` | Service unavailable | Model not loaded |

**Validation error `422` example**

```json
{
  "detail": [
    {
      "loc": ["body", "features"],
      "msg": "features must have exactly 7 values (age, appearances, goals, assists, minutes, yellow_cards, red_cards)",
      "type": "value_error"
    }
  ]
}
```

## Authentication Flow

```
Client                          API
  |  POST /v1/predict             |
  |  header: api-key              |
  | ----------------------------> |
  |                               |  verify_api_key()
  |                               |   - missing -> 403
  |                               |   - wrong   -> 401
  |                               |   - valid   -> continue
  |                               |  model.predict()
  |  <--------------------------- |
  |  200 PredictionResponse       |
```

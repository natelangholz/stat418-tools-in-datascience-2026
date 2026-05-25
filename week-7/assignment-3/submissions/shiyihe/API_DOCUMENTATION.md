# API Documentation

## Base URL

For local testing I used:

http://127.0.0.1:8000

---

## Authentication

Most endpoints require an API key in the request header.

Example:

api-key: test123

---

## GET /health

Simple health check endpoint to make sure the API server is running.

Example response:

{
  "status": "healthy"
}

---

## GET /ready

Checks whether the ML model has been loaded successfully.

Example response:

{
  "status": "ready"
}

---

## POST /v1/predict

Makes a single prediction using three input features.

Feature order:

[wt, hp, cyl]

Example request:

{
  "features": [3.0, 110.0, 6]
}

Example response:

{
  "prediction": 1.0,
  "confidence": 0.97,
  "model_version": "v1.0",
  "request_id": "uuid"
}

---

## POST /v1/predict/batch

Makes predictions for multiple rows at once.

Example request:

{
  "instances": [
    [3.0, 110.0, 6],
    [2.2, 90.0, 4]
  ]
}

Example response:

{
  "predictions": [1.0, 1.0],
  "confidences": [0.97, 1.0],
  "count": 2,
  "model_version": "v1.0"
}

---

## GET /v1/model/info

Returns metadata about the trained model.

Example response:

{
  "model_version": "v1.0",
  "features": ["wt", "hp", "cyl"],
  "target": "high_mpg",
  "model_type": "RandomForestClassifier"
}

---

## Error Codes

200 = success

401 = missing or invalid API key

422 = invalid request input

429 = rate limit exceeded

500 = internal server error

---

## Swagger Docs

FastAPI automatically generates API docs here:

http://127.0.0.1:8000/docs

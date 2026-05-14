"""Tests for the Iris Species Classifier API."""
import pytest
from fastapi.testclient import TestClient

# conftest.py sets API_KEY and MODEL_PATH before this import
from main import app  # noqa: E402

HEADERS = {"api-key": "test123"}


@pytest.fixture(scope="module")
def client():
    """Start app with lifespan (loads model) for the whole test module."""
    with TestClient(app) as c:
        yield c


# ── Health & Readiness ────────────────────────────────────────────────────────
def test_health_check(client):
    """GET /health returns 200 and status=healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check(client):
    """GET /ready returns 200 when model is loaded."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


# ── Model Info ────────────────────────────────────────────────────────────────
def test_model_info_authenticated(client):
    """GET /v1/model/info returns model metadata with valid key."""
    response = client.get("/v1/model/info", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "features" in data
    assert len(data["features"]) == 4
    assert len(data["classes"]) == 3


def test_model_info_no_auth(client):
    """GET /v1/model/info returns 422 without api-key header."""
    response = client.get("/v1/model/info")
    assert response.status_code == 422


def test_model_info_wrong_key(client):
    """GET /v1/model/info returns 401 with wrong api-key."""
    response = client.get("/v1/model/info", headers={"api-key": "wrongkey"})
    assert response.status_code == 401


# ── Single Prediction ─────────────────────────────────────────────────────────
def test_predict_setosa(client):
    """POST /v1/predict correctly classifies a setosa sample."""
    response = client.post(
        "/v1/predict",
        json={"features": [5.1, 3.5, 1.4, 0.2]},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "setosa"
    assert 0.0 <= data["confidence"] <= 1.0
    assert "request_id" in data
    assert data["model_version"] == "v1.0"


def test_predict_virginica(client):
    """POST /v1/predict correctly classifies a virginica sample."""
    response = client.post(
        "/v1/predict",
        json={"features": [6.3, 3.3, 6.0, 2.5]},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["predicted_class"] == "virginica"


def test_predict_no_auth(client):
    """POST /v1/predict returns 422 without api-key header."""
    response = client.post("/v1/predict", json={"features": [5.1, 3.5, 1.4, 0.2]})
    assert response.status_code == 422


def test_predict_wrong_key(client):
    """POST /v1/predict returns 401 with wrong api-key."""
    response = client.post(
        "/v1/predict",
        json={"features": [5.1, 3.5, 1.4, 0.2]},
        headers={"api-key": "wrongkey"},
    )
    assert response.status_code == 401


def test_predict_empty_features(client):
    """POST /v1/predict returns 422 when features list is empty."""
    response = client.post(
        "/v1/predict",
        json={"features": []},
        headers=HEADERS,
    )
    assert response.status_code == 422


def test_predict_wrong_feature_count(client):
    """POST /v1/predict returns 422 when feature count != 4."""
    response = client.post(
        "/v1/predict",
        json={"features": [1.0, 2.0]},
        headers=HEADERS,
    )
    assert response.status_code == 422


def test_predict_negative_features(client):
    """POST /v1/predict returns 422 for negative feature values."""
    response = client.post(
        "/v1/predict",
        json={"features": [-1.0, 3.5, 1.4, 0.2]},
        headers=HEADERS,
    )
    assert response.status_code == 422


# ── Batch Prediction ──────────────────────────────────────────────────────────
def test_batch_predict_success(client):
    """POST /v1/predict/batch returns correct count and predictions."""
    response = client.post(
        "/v1/predict/batch",
        json={"instances": [
            [5.1, 3.5, 1.4, 0.2],
            [6.3, 3.3, 6.0, 2.5],
            [5.9, 3.0, 4.2, 1.5],
        ]},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["predictions"]) == 3
    assert len(data["predicted_classes"]) == 3


def test_batch_predict_empty(client):
    """POST /v1/predict/batch returns 422 for empty instances list."""
    response = client.post(
        "/v1/predict/batch",
        json={"instances": []},
        headers=HEADERS,
    )
    assert response.status_code == 422


def test_batch_predict_no_auth(client):
    """POST /v1/predict/batch returns 422 without api-key header."""
    response = client.post(
        "/v1/predict/batch",
        json={"instances": [[5.1, 3.5, 1.4, 0.2]]},
    )
    assert response.status_code == 422

"""Endpoint tests for the market value prediction API."""
import os
import sys

import pytest
from fastapi.testclient import TestClient

# Make the app importable when tests run from the tests/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("API_KEY", "test123")

from main import app  # noqa: E402

AUTH = {"api-key": "test123"}
# age, appearances, goals, assists, minutes, yellow_cards, red_cards
SAMPLE = [24, 38, 12, 7, 3100, 4, 0]


@pytest.fixture(scope="module")
def client():
    """Provide a TestClient that runs startup events (model loading)."""
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Health check returns 200 and a healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check(client):
    """Readiness check returns 200 once the model is loaded."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_predict_success(client):
    """A valid authenticated prediction returns value, confidence, and id."""
    response = client.post("/v1/predict", json={"features": SAMPLE}, headers=AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert data["prediction"] > 0
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["request_id"]


def test_predict_no_auth(client):
    """A prediction without an API key is rejected with 403."""
    response = client.post("/v1/predict", json={"features": SAMPLE})
    assert response.status_code == 403


def test_predict_wrong_auth(client):
    """A prediction with a wrong API key is rejected with 401."""
    response = client.post("/v1/predict", json={"features": SAMPLE}, headers={"api-key": "wrong"})
    assert response.status_code == 401


def test_predict_invalid_input(client):
    """An empty feature list fails validation with 422."""
    response = client.post("/v1/predict", json={"features": []}, headers=AUTH)
    assert response.status_code == 422


def test_predict_wrong_feature_count(client):
    """A feature list of the wrong length fails validation with 422."""
    response = client.post("/v1/predict", json={"features": [1, 2, 3]}, headers=AUTH)
    assert response.status_code == 422


def test_predict_batch_success(client):
    """A valid batch request returns one prediction per instance."""
    response = client.post(
        "/v1/predict/batch",
        json={"instances": [SAMPLE, SAMPLE, SAMPLE]},
        headers=AUTH,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["predictions"]) == 3


def test_predict_batch_no_auth(client):
    """A batch request without an API key is rejected with 403."""
    response = client.post("/v1/predict/batch", json={"instances": [SAMPLE]})
    assert response.status_code == 403


def test_predict_batch_too_large(client):
    """A batch larger than 100 instances fails validation with 422."""
    response = client.post(
        "/v1/predict/batch",
        json={"instances": [SAMPLE] * 101},
        headers=AUTH,
    )
    assert response.status_code == 422


def test_model_info(client):
    """The model info endpoint returns version and feature metadata."""
    response = client.get("/v1/model/info", headers=AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data["model_version"]
    assert data["n_features"] == 7
    assert len(data["features"]) == 7


def test_model_info_no_auth(client):
    """The model info endpoint requires authentication."""
    response = client.get("/v1/model/info")
    assert response.status_code == 403

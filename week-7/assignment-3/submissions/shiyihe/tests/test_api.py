import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app, load_model

load_model()

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_predict_success():
    response = client.post(
        "/v1/predict",
        json={"features": [3.0, 110.0, 6]},
        headers={"api-key": "test123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "model_version" in data
    assert "request_id" in data


def test_batch_predict_success():
    response = client.post(
        "/v1/predict/batch",
        json={
            "instances": [
                [3.0, 110.0, 6],
                [2.2, 90.0, 4],
            ]
        },
        headers={"api-key": "test123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 2
    assert len(data["predictions"]) == 2
    assert len(data["confidences"]) == 2


def test_model_info_success():
    response = client.get(
        "/v1/model/info",
        headers={"api-key": "test123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["model_version"] == "v1.0"
    assert data["features"] == ["wt", "hp", "cyl"]
    assert data["target"] == "high_mpg"


def test_predict_no_auth():
    response = client.post(
        "/v1/predict",
        json={"features": [3.0, 110.0, 6]},
    )
    assert response.status_code in [401, 403]


def test_predict_invalid_input():
    response = client.post(
        "/v1/predict",
        json={"features": [3.0, 110.0]},
        headers={"api-key": "test123"},
    )
    assert response.status_code == 422

"""API tests for the MTCARS FastAPI application."""

from pathlib import Path

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LinearRegression

from app.main import MODEL_PATH, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure a minimal model artifact exists for tests."""
    model_path = tmp_path / "model.pkl"
    training_features = pd.DataFrame(
        [[2.62, 110], [3.5, 150]],
        columns=["wt", "hp"],
    )
    artifact = {
        "model": LinearRegression().fit(training_features, [21.0, 18.0]),
        "features": ["wt", "hp"],
        "target": "mpg",
    }
    joblib.dump(artifact, model_path)
    monkeypatch.setattr("app.main.MODEL_PATH", model_path)
    monkeypatch.setattr("app.main._model_artifact", None)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["features"] == "wt,hp"
    assert body["target"] == "mpg"


def test_predict_success() -> None:
    response = client.post(
        "/predict",
        json={"wt": 2.62, "hp": 110},
    )
    assert response.status_code == 200
    body = response.json()
    assert "predicted_mpg" in body
    assert isinstance(body["predicted_mpg"], float)


def test_predict_invalid_type() -> None:
    response = client.post(
        "/predict",
        json={"wt": "heavy", "hp": 110},
    )
    assert response.status_code == 422


def test_predict_missing_field() -> None:
    response = client.post("/predict", json={"wt": 2.62})
    assert response.status_code == 422


def test_ready_model_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    missing = Path("/nonexistent/model.pkl")
    monkeypatch.setattr("app.main.MODEL_PATH", missing)
    monkeypatch.setattr("app.main._model_artifact", None)

    response = client.get("/ready")
    assert response.status_code == 503

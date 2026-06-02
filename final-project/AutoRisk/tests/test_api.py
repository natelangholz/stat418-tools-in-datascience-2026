"""
Unit tests for AutoRisk Flask API
Run: pytest tests/test_api.py -v
"""
import sys
from pathlib import Path

import pytest

# Allow importing from api/
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import main as api_main

# Point LABELED_CSV to the actual data location (repo root / data / processed)
_REPO_ROOT = Path(__file__).parent.parent
api_main.LABELED_CSV = _REPO_ROOT / "data" / "processed" / "vehicle_risk_features_labeled.csv"

from main import app, load_everything


@pytest.fixture(scope="module")
def client():
    load_everything()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["model"] == "random_forest"
    assert data["test_accuracy"] > 0.7
    assert data["test_f1"] > 0.5


def test_vehicles(client):
    r = client.get("/vehicles")
    assert r.status_code == 200
    data = r.get_json()
    assert "vehicles" in data
    assert data["count"] > 0


def test_makes(client):
    r = client.get("/makes")
    assert r.status_code == 200
    data = r.get_json()
    assert "makes" in data
    assert len(data["makes"]) > 0


def test_predict_valid(client):
    payload = {
        "year": 2022,
        "make": "Toyota",
        "recall_count": 3,
        "recall_electrical_count": 1,
        "recall_brake_count": 0,
        "recall_restraint_count": 1,
        "recall_engine_count": 0,
        "recall_powertrain_count": 1,
        "recall_fuel_count": 0,
        "recall_steering_count": 0,
        "recall_suspension_count": 0,
        "recall_structure_count": 0,
        "recall_other_count": 0,
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert "high_risk_probability" in data
    assert "prediction" in data
    assert "label" in data
    assert 0.0 <= data["high_risk_probability"] <= 1.0
    assert data["prediction"] in (0, 1)
    assert data["label"] in ("high-risk", "low-risk")


def test_predict_missing_year(client):
    r = client.post("/predict", json={"make": "Honda"})
    assert r.status_code == 400


def test_vehicle_stats_valid(client):
    # Get a real vehicle from the dataset first
    vehicles = client.get("/vehicles").get_json()["vehicles"]
    v = vehicles[0]
    r = client.get(f"/vehicles/stats?year={v['year']}&make={v['make']}&model={v['base_model']}")
    assert r.status_code == 200


def test_vehicle_stats_not_found(client):
    r = client.get("/vehicles/stats?year=2022&make=FakeMake&model=FAKEMODEL")
    assert r.status_code == 404


def test_models_for_make(client):
    r = client.get("/models?make=Toyota&year=2022")
    assert r.status_code == 200
    data = r.get_json()
    assert "models" in data

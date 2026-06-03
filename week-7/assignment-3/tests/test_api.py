from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_success():
    payload = {
        "cyl": 4,
        "hp": 100,
        "wt": 2.5,
        "gear": 5,
        "am": 0
    }
    response = client.post("/predict", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert "predicted_mpg" in data
    assert isinstance(data["predicted_mpg"], float)
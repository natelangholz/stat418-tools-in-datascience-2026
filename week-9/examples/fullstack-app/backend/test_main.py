from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint_returns_real_iris_prediction_and_cached_flag():
    response = client.post(
        "/predict",
        json={"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in {"setosa", "versicolor", "virginica"}
    assert body["cached"] is False
    assert body["sepal_length"] == 5.1
    assert body["petal_width"] == 0.2


def test_predict_endpoint_uses_cache_on_repeat_request():
    payload = {"sepal_length": 6.0, "sepal_width": 2.9, "petal_length": 4.5, "petal_width": 1.5}

    first = client.post("/predict", json=payload)
    second = client.post("/predict", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["prediction"] == second.json()["prediction"]
    assert second.json()["cached"] is True


def test_history_endpoint_tracks_predictions():
    client.post(
        "/predict",
        json={"sepal_length": 6.7, "sepal_width": 3.1, "petal_length": 4.7, "petal_width": 1.5},
    )

    response = client.get("/history")
    assert response.status_code == 200

    body = response.json()
    assert "requests" in body
    assert len(body["requests"]) >= 1
    latest = body["requests"][-1]
    assert latest["prediction"] in {"setosa", "versicolor", "virginica"}
    assert "cached" in latest


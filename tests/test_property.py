from fastapi.testclient import TestClient

from property.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"ready": True}


def test_analyze_success():
    r = client.post("/analyze", json={"domain": "example.com"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["domains"]) >= 1


def test_analyze_failure():
    r = client.post("/analyze", json={"domain": "invalid"})
    assert r.status_code == 400

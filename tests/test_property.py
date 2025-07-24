from fastapi.testclient import TestClient

from services.property.app import app

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


def test_analyze_with_url():
    r = client.post("/analyze", json={"domain": "http://www.Example.COM/page"})
    assert r.status_code == 200
    data = r.json()
    assert any("example.com" in d for d in data["domains"])


def test_analyze_failure():
    r = client.post("/analyze", json={"domain": "invalid"})
    assert r.status_code == 400


def test_options_analyze():
    r = client.options(
        "/analyze",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.status_code == 200

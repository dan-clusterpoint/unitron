from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze():
    r = client.post("/analyze", json={"url": "https://example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["url"] == "https://example.com"
    assert data["martech"] == {}
    assert data["cms"] == []
    assert data["degraded"] is False


def test_generate_merges_martech():
    payload = {
        "url": "https://example.com",
        "martech": {"core": ["Google Analytics"]},
        "martech_manual": [{"category": "analytics", "vendor": "Segment"}],
        "cms": ["WordPress"],
    }
    r = client.post("/generate", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["martech"] == ["Segment", "Google Analytics"]
    assert data["cms"] == ["WordPress"]

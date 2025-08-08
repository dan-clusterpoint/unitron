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
    # Enrichment fields should always be present, even if empty
    assert "industry" in data
    assert "location" in data
    assert "logoUrl" in data
    assert "tagline" in data


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
    assert r.headers["access-control-allow-origin"] == "*"
    allowed = r.headers["access-control-allow-headers"]
    assert "Content-Type" in allowed
    assert "Authorization" in allowed
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"


def test_options_respects_ui_origin(monkeypatch):
    monkeypatch.setenv("UI_ORIGIN", "http://ui.example")
    import importlib
    import services.property.app as prop

    prop = importlib.reload(prop)
    local_client = TestClient(prop.app)
    r = local_client.options(
        "/analyze",
        headers={
            "Origin": "http://ui.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://ui.example"

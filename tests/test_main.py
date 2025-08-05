from fastapi.testclient import TestClient
import httpx

import httpx
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def _set_mock_transport(monkeypatch, handler: httpx.MockTransport) -> None:
    class DummyClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            super().__init__(transport=handler, *args, **kwargs)

    monkeypatch.setattr(main, "httpx", main.httpx)
    monkeypatch.setattr(main.httpx, "AsyncClient", DummyClient)
    main.app.state.client = DummyClient()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/analyze"
        return httpx.Response(200, json={"domains": ["example.com"]})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/analyze", json={"url": "https://example.com"})
    assert r.status_code == 200
    assert r.json()["property"]["domains"] == ["example.com"]


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

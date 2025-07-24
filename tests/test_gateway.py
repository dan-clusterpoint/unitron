import asyncio
import time

import httpx
from fastapi.testclient import TestClient

import gateway.app as gateway_app

client = TestClient(gateway_app.app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200


def _set_mock_transport(monkeypatch, handler: httpx.MockTransport) -> None:
    class DummyClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            super().__init__(transport=handler, *args, **kwargs)

    monkeypatch.setattr(gateway_app.httpx, "AsyncClient", DummyClient)


def test_ready_waits_for_both_services(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/ready" and "martech" in str(request.url):
            await asyncio.sleep(0.1)
            return httpx.Response(200)
        if request.url.path == "/ready" and "property" in str(request.url):
            await asyncio.sleep(0.2)
            return httpx.Response(200)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    start = time.perf_counter()
    r = client.get("/ready")
    duration = time.perf_counter() - start
    assert r.status_code == 200
    data = r.json()
    assert data["ready"] is True
    assert data["martech"] == "ok"
    assert data["property"] == "ok"
    assert duration < 0.25  # should take about max(delay)

    metrics_data = client.get("/metrics").json()
    assert metrics_data["martech"]["success"] >= 1
    assert metrics_data["property"]["success"] >= 1
    assert metrics_data["martech"]["codes"]["200"] >= 1
    assert metrics_data["property"]["codes"]["200"] >= 1
    assert metrics_data["martech"]["codes"]["200"] >= 1
    assert metrics_data["property"]["codes"]["200"] >= 1


def test_ready_returns_false_when_unhealthy(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/ready" and "martech" in str(request.url):
            return httpx.Response(503)
        if request.url.path == "/ready" and "property" in str(request.url):
            return httpx.Response(200)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.get("/ready")
    assert r.status_code == 200
    data = r.json()
    assert data["ready"] is False
    assert data["martech"] == "degraded"
    assert data["property"] == "ok"


def test_analyze_success(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if "martech" in str(request.url):
            return httpx.Response(200, json={"core": ["GA"]})
        if "property" in str(request.url):
            return httpx.Response(200, json={"domains": ["example.com"]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/analyze", json={"url": "https://example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["property"]["domains"] == ["example.com"]
    assert data["martech"]["core"] == ["GA"]
    assert data["degraded"] is False

    metrics_data = client.get("/metrics").json()
    assert metrics_data["martech"]["success"] >= 1
    assert metrics_data["property"]["success"] >= 1


def test_analyze_failure_increments_metrics(monkeypatch):
    calls = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        if "property" in str(request.url):
            calls["count"] += 1
            return httpx.Response(500)
        return httpx.Response(200, json={"core": []})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    before = gateway_app.metrics["property"]["failure"]
    before_code = gateway_app.metrics["property"]["codes"].get("500", 0)
    r = client.post("/analyze", json={"url": "https://bad.com"})
    assert r.status_code == 502
    assert gateway_app.metrics["property"]["failure"] == before + 1
    assert (
        gateway_app.metrics["property"]["codes"].get("500", 0)
        == before_code + 1
    )
    assert calls["count"] >= 2


def test_analyze_degraded_when_service_unready(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if (
            "martech" in str(request.url)
            and request.url.path == "/analyze"
        ):
            return httpx.Response(503)
        if "property" in str(request.url):
            return httpx.Response(200, json={"domains": ["example.com"]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/analyze", json={"url": "https://example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["degraded"] is True
    assert data["property"]["domains"] == ["example.com"]
    assert data["martech"] is None


def test_metrics_endpoint(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "martech" in data and "property" in data


def test_analyze_error_detail_mentions_service(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if "martech" in str(request.url):
            return httpx.Response(500)
        if "property" in str(request.url):
            return httpx.Response(200, json={"domains": ["example.com"]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/analyze", json={"url": "https://example.com"})
    assert r.status_code == 502
    assert r.json()["detail"] == "martech service unavailable"

import asyncio
import time

import httpx
import pytest
from fastapi.testclient import TestClient

import services.gateway.app as gateway_app

client = TestClient(gateway_app.app)


def test_health():
    r = client.get("/health")
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
    assert data["cms"] == []
    assert data["degraded"] is False

    metrics_data = client.get("/metrics").json()
    assert metrics_data["martech"]["success"] >= 1
    assert metrics_data["property"]["success"] >= 1


def test_analyze_returns_top_level_cms(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if "martech" in str(request.url):
            return httpx.Response(200, json={"core": [], "cms": ["WordPress"]})
        if "property" in str(request.url):
            return httpx.Response(200, json={"domains": ["example.com"]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/analyze", json={"url": "https://example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["cms"] == ["WordPress"]
    assert data["martech"] == {"core": []}


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
    assert gateway_app.metrics["property"]["codes"].get("500", 0) == before_code + 1
    assert calls["count"] >= 2


def test_analyze_degraded_when_service_unready(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        if "martech" in str(request.url) and request.url.path == "/analyze":
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
    assert data["martech"] == {}
    assert data["cms"] == []


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


@pytest.mark.parametrize(
    "input_url,expected_url,expected_domain",
    [
        ("example.com", "https://example.com", "example.com"),
        ("www.foo.org/", "https://www.foo.org", "www.foo.org"),
    ],
)
def test_analyze_normalizes_url(monkeypatch, input_url, expected_url, expected_domain):
    captured: dict[str, dict] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        import json

        if "martech" in str(request.url):
            captured["martech"] = json.loads(request.content.decode())
            return httpx.Response(200, json={})
        if "property" in str(request.url):
            captured["property"] = json.loads(request.content.decode())
            return httpx.Response(200, json={"domains": [expected_domain]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/analyze", json={"url": input_url})
    assert r.status_code == 200
    assert captured["martech"]["url"] == expected_url
    assert captured["martech"]["force"] is False
    assert captured["property"]["domain"] == expected_domain


def test_generate_includes_manual_cms(monkeypatch):
    captured: dict[str, dict] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured["data"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post(
        "/generate",
        json={
            "url": "https://example.com",
            "martech": {},
            "cms": [],
            "cms_manual": "Drupal",
        },
    )
    assert r.status_code == 200
    assert captured["data"]["cms_manual"] == "Drupal"


def test_generate_omits_empty_manual(monkeypatch):
    captured: dict[str, dict] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured["data"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post(
        "/generate",
        json={"url": "https://example.com", "martech": {}, "cms": []},
    )
    assert r.status_code == 200
    assert "cms_manual" not in captured["data"]


def test_research_success(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(200, json={"out": True})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/research", json={"foo": 1})
    assert r.status_code == 200
    assert r.json() == {"result": {"out": True}, "degraded": False}
    assert captured["path"] == "/research"

    metrics_data = client.get("/metrics").json()
    assert metrics_data["insight"]["success"] >= 1


def test_research_degraded(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(503)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    before = gateway_app.metrics["insight"]["failure"]
    before_code = gateway_app.metrics["insight"]["codes"].get("503", 0)

    r = client.post("/research", json={"foo": "bar"})
    assert r.status_code == 200
    assert r.json()["degraded"] is True
    assert captured["path"] == "/research"
    assert gateway_app.metrics["insight"]["failure"] == before + 1
    assert gateway_app.metrics["insight"]["codes"].get("503", 0) == before_code + 1


def test_research_failure(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(500)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    before = gateway_app.metrics["insight"]["failure"]
    before_code = gateway_app.metrics["insight"]["codes"].get("500", 0)

    r = client.post("/research", json={"foo": "baz"})
    assert r.status_code == 502
    assert r.json()["detail"] == "insight service unavailable"
    assert captured["path"] == "/research"
    assert gateway_app.metrics["insight"]["failure"] == before + 1
    assert gateway_app.metrics["insight"]["codes"].get("500", 0) == before_code + 1


def test_insight_success(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(200, json={"insight": "Hi"})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/insight", json={"text": "Hello"})
    assert r.status_code == 200
    assert r.json() == {"result": {"insight": "Hi"}, "degraded": False}
    assert captured["path"] == "/generate-insights"


def test_insight_error_detail(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(400, text="bad input")

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/insight", json={"text": ""})
    assert r.status_code == 502
    assert r.json()["detail"] == "bad input"
    assert captured["path"] == "/generate-insights"


def test_generate_insight_and_personas_success(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    r = client.post("/generate-insight-and-personas", json={"foo": 1})
    assert r.status_code == 200
    assert r.json() == {"result": {"ok": True}, "degraded": False}
    assert captured["path"] == "/insight-and-personas"

    metrics_data = client.get("/metrics").json()
    assert metrics_data["insight"]["success"] >= 1


def test_generate_insight_and_personas_degraded(monkeypatch):
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(503)

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    before = gateway_app.metrics["insight"]["failure"]
    before_code = gateway_app.metrics["insight"]["codes"].get("503", 0)

    r = client.post("/generate-insight-and-personas", json={"foo": "bar"})
    assert r.status_code == 200
    assert r.json()["degraded"] is True
    assert captured["path"] == "/insight-and-personas"
    assert gateway_app.metrics["insight"]["failure"] == before + 1
    assert gateway_app.metrics["insight"]["codes"].get("503", 0) == before_code + 1


def test_insight_timeout(monkeypatch):
    recorded = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.05)
        return httpx.Response(400, text="slow")

    class RecordingClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            recorded["timeout"] = kwargs.get("timeout")
            super().__init__(transport=httpx.MockTransport(handler), *args, **kwargs)

    monkeypatch.setattr(gateway_app.httpx, "AsyncClient", RecordingClient)

    start = time.perf_counter()
    r = client.post("/insight", json={"text": "hi"})
    duration = time.perf_counter() - start
    assert r.status_code == 502
    assert r.json()["detail"] == "slow"
    assert recorded["timeout"] == 20
    assert duration >= 0.05


def test_research_timeout(monkeypatch):
    recorded = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.05)
        return httpx.Response(400, text="slow")

    class RecordingClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            recorded["timeout"] = kwargs.get("timeout")
            super().__init__(transport=httpx.MockTransport(handler), *args, **kwargs)

    monkeypatch.setattr(gateway_app.httpx, "AsyncClient", RecordingClient)

    start = time.perf_counter()
    r = client.post("/research", json={"topic": "ai"})
    duration = time.perf_counter() - start
    assert r.status_code == 502
    assert r.json()["detail"] == "slow"
    assert recorded["timeout"] == 20
    assert duration >= 0.05

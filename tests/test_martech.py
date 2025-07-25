import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi.testclient import TestClient

from services.martech.app import app, _extract_scripts
import os
import httpx
import pytest

client = TestClient(app)


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # type: ignore[override]
        if self.path == "/script.js":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"console.log('hi');")
        else:
            html = (
                "<script src='https://www.google-"
                "analytics.com/analytics.js'></script>"
                "<script src='/script.js'></script>"
            )
            self.send_response(200)
            self.end_headers()
            self.wfile.write(html.encode())


class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # type: ignore[override]
        if self.path == "/final":
            html = (
                "<script src='https://www.google-"
                "analytics.com/analytics.js'></script>"
            )
            self.send_response(200)
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == "/script.js":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"console.log('hi');")
        else:
            self.send_response(301)
            self.send_header("Location", "/final")
            self.end_headers()


def test_health():
    r = client.get('/health')
    assert r.status_code == 200


def test_ready_and_analyze():
    # spin up simple http server
    server = HTTPServer(('localhost', 0), SimpleHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        ready = client.get('/ready')
        assert ready.status_code == 200
        assert ready.json() == {'ready': True}

        os.environ['OUTBOUND_HTTP_PROXY'] = ''
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''

        resp = client.post(
            '/analyze',
            json={'url': f'http://localhost:{port}/', 'debug': True},
        )
        data = resp.json()
        assert resp.status_code == 200
        core = data['core']
        assert isinstance(core, dict)
        assert 'Google Analytics' in core
        assert 'confidence' in core['Google Analytics']
        assert 'debug' in data and 'scripts' in data['debug']
    finally:
        server.shutdown()


def test_analyze_follows_redirects():
    server = HTTPServer(("localhost", 0), RedirectHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        client.get("/ready")
        resp = client.post(
            "/analyze", json={"url": f"http://localhost:{port}/"}
        )
        assert resp.status_code == 200
        core = resp.json()["core"]
        assert isinstance(core, list)
        assert "Google Analytics" in core
    finally:
        server.shutdown()


def test_options_analyze():
    r = client.options(
        '/analyze',
        headers={
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'POST',
        },
    )
    assert r.status_code == 200


def test_analyze_handles_request_error(monkeypatch):
    client.get('/ready')

    def boom(*args, **kwargs):
        req = httpx.Request("GET", "http://example.com")
        raise httpx.RequestError("fail", request=req)

    monkeypatch.setattr("services.martech.app.analyze_url", boom)
    resp = client.post("/analyze", json={"url": "http://example.com"})
    assert resp.status_code == 503
    assert resp.json() == {"detail": "martech service unavailable"}


def _set_mock_client(
    monkeypatch, handler: httpx.MockTransport, hook=None
) -> None:
    class DummyClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            if hook is not None:
                hook(kwargs)
            super().__init__(transport=handler, *args, **kwargs)

    monkeypatch.setattr("services.martech.app.httpx.AsyncClient", DummyClient)


def _set_stub_client(monkeypatch, hook) -> None:
    class DummyClient:
        def __init__(self, *args, **kwargs):
            hook(kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):
            request = httpx.Request("GET", url)
            return httpx.Response(200, text="<html></html>", request=request)

    monkeypatch.setattr("services.martech.app.httpx.AsyncClient", DummyClient)


def test_diagnose_success(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    _set_mock_client(monkeypatch, transport)

    r = client.get("/diagnose")
    assert r.status_code == 200
    assert r.json() == {"success": True, "error": None}


def test_diagnose_failure(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.RequestError("fail", request=request)

    transport = httpx.MockTransport(handler)
    _set_mock_client(monkeypatch, transport)

    r = client.get("/diagnose")
    assert r.status_code == 200
    assert r.json() == {"success": False, "error": "fail"}


def test_proxy_usage(monkeypatch):
    captured = {}

    def hook(kwargs: dict) -> None:
        captured["proxies"] = kwargs.get("proxies")

    _set_stub_client(monkeypatch, hook)
    monkeypatch.setenv("OUTBOUND_HTTP_PROXY", "http://proxy.local")

    r = client.get("/diagnose")
    assert r.status_code == 200
    assert captured["proxies"] == {
        "http://": "http://proxy.local",
        "https://": "http://proxy.local",
    }


def test_analyze_uses_proxy(monkeypatch):
    client.get("/ready")

    captured = {}

    def hook(kwargs: dict) -> None:
        captured["proxies"] = kwargs.get("proxies")

    _set_stub_client(monkeypatch, hook)
    monkeypatch.setenv("OUTBOUND_HTTP_PROXY", "http://proxy.local")

    r = client.post("/analyze", json={"url": "http://example.com"})
    assert r.status_code == 200
    assert captured["proxies"] == {
        "http://": "http://proxy.local",
        "https://": "http://proxy.local",
    }


def test_diagnose_mocked_asyncclient_success(monkeypatch):
    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            request = httpx.Request("GET", url)
            return httpx.Response(200, request=request)

    monkeypatch.setattr("services.martech.app.httpx.AsyncClient", DummyClient)

    r = client.get("/diagnose")
    assert r.status_code == 200
    assert r.json() == {"success": True, "error": None}


def test_diagnose_mocked_asyncclient_failure(monkeypatch):
    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            req = httpx.Request("GET", url)
            raise httpx.RequestError("fail", request=req)

    monkeypatch.setattr("services.martech.app.httpx.AsyncClient", DummyClient)

    r = client.get("/diagnose")
    assert r.status_code == 200
    assert r.json() == {"success": False, "error": "fail"}


def test_fingerprints_endpoint():
    client.get("/ready")
    r = client.get("/fingerprints")
    assert r.status_code == 200
    data = r.json()
    assert "core" in data
    assert any(
        vendor.get("name") == "Google Analytics" for vendor in data["core"]
    )


@pytest.mark.asyncio
async def test_extract_scripts_parses_gtm(monkeypatch):
    html = "<script src='https://www.googletagmanager.com/gtm.js'></script>"

    async def fake_fetch(_client, _url):
        js = (
            "var s=document.createElement('script');"
            "s.src=\"https://cdn.example.com/inner.js\";"
        )
        return js, {}

    monkeypatch.setattr("services.martech.app._fetch", fake_fetch)

    dummy_client = object()
    urls, inline = await _extract_scripts(dummy_client, html)
    assert "https://www.googletagmanager.com/gtm.js" in urls
    assert "https://cdn.example.com/inner.js" in urls
    assert inline == []


def test_force_bypasses_cache(monkeypatch):
    calls = {"count": 0}

    async def fake_analyze_url(
        url: str,
        debug: bool = False,
        headless: bool = False,
    ):
        calls["count"] += 1
        return {"core": {"GA": {"confidence": 1.0, "evidence": {}}}}

    monkeypatch.setattr("services.martech.app.analyze_url", fake_analyze_url)

    r1 = client.post("/analyze", json={"url": "http://a.com"})
    assert r1.status_code == 200
    assert calls["count"] == 1

    r2 = client.post("/analyze", json={"url": "http://a.com"})
    assert r2.status_code == 200
    assert calls["count"] == 1

    r3 = client.post("/analyze", json={"url": "http://a.com", "force": True})
    assert r3.status_code == 200
    assert calls["count"] == 2

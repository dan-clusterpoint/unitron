import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi.testclient import TestClient

import services.martech.app
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

    async def boom_fetch(_client, _url):
        req = httpx.Request("GET", _url)
        raise httpx.RequestError("fail", request=req)

    monkeypatch.setattr("services.martech.app._fetch", boom_fetch)

    resp = client.post(
        "/analyze", json={"url": "http://example.com", "debug": True}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["network_error"] is True


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
        captured["proxy"] = kwargs.get("proxy")

    _set_stub_client(monkeypatch, hook)
    monkeypatch.setenv("OUTBOUND_HTTP_PROXY", "http://proxy.local")

    r = client.get("/diagnose")
    assert r.status_code == 200
    assert captured["proxy"] == "http://proxy.local"


def test_analyze_uses_proxy(monkeypatch):
    client.get("/ready")

    captured = {}

    def hook(kwargs: dict) -> None:
        captured["proxy"] = kwargs.get("proxy")

    _set_stub_client(monkeypatch, hook)
    monkeypatch.setenv("OUTBOUND_HTTP_PROXY", "http://proxy.local")

    r = client.post(
        "/analyze", json={"url": "http://example.com", "force": True}
    )
    assert r.status_code == 200
    assert captured["proxy"] == "http://proxy.local"


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
    assert "vendors" in data
    assert any(v.get("name") == "Google Analytics" for v in data["vendors"])


def test_fingerprints_debug():
    client.get("/ready")
    r = client.get("/fingerprints?debug=true")
    assert r.status_code == 200
    data = r.json()
    assert "core" in data
    assert "asset_host" in set(data["core"]["Google Analytics"])
    assert "Segment" in data["core"]


@pytest.mark.asyncio
async def test_extract_scripts_parses_gtm(monkeypatch):
    html = "<script src='https://www.googletagmanager.com/gtm.js'></script>"

    js_content = (
        "var s=document.createElement('script');"
        "s.src=\"https://cdn.example.com/inner.js\";"
    )

    async def fake_fetch(_client, _url):
        return js_content, {}, {}

    monkeypatch.setattr("services.martech.app._fetch", fake_fetch)

    dummy_client = object()
    urls, inline, external = await _extract_scripts(
        dummy_client, html, base_url="http://example.com"
    )
    assert "https://www.googletagmanager.com/gtm.js" in urls
    assert "https://cdn.example.com/inner.js" in urls
    assert inline == []
    assert external == [js_content]


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


def _start_local_server(script_map):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # type: ignore[override]
            path = self.path
            if path in script_map:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(script_map[path].encode())
            else:
                html = "".join(
                    f"<script src='{p}'></script>" for p in script_map.keys()
                )
                self.send_response(200)
                self.end_headers()
                self.wfile.write(html.encode())

    server = HTTPServer(("localhost", 0), Handler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


def test_local_scripts_detected(monkeypatch):
    server, port = _start_local_server(
        {
            "/ga.js": "ga('create','UA-1','auto');",
            "/segment.js": "analytics.load('XYZ');",
        }
    )
    try:
        monkeypatch.setenv("OUTBOUND_HTTP_PROXY", "")
        monkeypatch.setenv("HTTP_PROXY", "")
        monkeypatch.setenv("HTTPS_PROXY", "")
        client.get("/ready")
        resp = client.post(
            "/analyze",
            json={"url": f"http://localhost:{port}/"},
        )
        assert resp.status_code == 200
        data = resp.json()["core"]
        assert "Google Analytics" in data
        assert "Segment" in data
    finally:
        server.shutdown()


@pytest.mark.asyncio
async def test_analyze_url_detects_cms(monkeypatch):
    html = "<html>wp-content</html>"
    headers = {"X-Generator": "WordPress"}
    cookies = {"wordpress_test_cookie": "1"}

    async def fake_fetch(_client, _url):
        return html, headers, cookies

    async def fake_extract(_client, _html, base_url=None):
        return set(), [], []

    monkeypatch.setattr("services.martech.app._fetch", fake_fetch)
    monkeypatch.setattr("services.martech.app._extract_scripts", fake_extract)

    result = await services.martech.app.analyze_url(
        "http://example.com", debug=True
    )
    cms = result["cms"]
    assert "WordPress" in cms.get("uncategorized", {})


@pytest.mark.asyncio
async def test_analyze_url_wappalyzer(monkeypatch):
    try:
        __import__("Wappalyzer")  # noqa: WPS395
    except Exception:  # pragma: no cover - optional dependency
        pytest.skip("python-wappalyzer not available")
    html = "<script src='/wp-includes/wp-embed.min.js'></script>"
    headers: dict[str, str] = {}
    cookies: dict[str, str] = {}

    async def fake_fetch(_client, _url):
        return html, headers, cookies

    async def fake_extract(_client, _html, base_url=None):
        return set(), [], []

    monkeypatch.setattr("services.martech.app._fetch", fake_fetch)
    monkeypatch.setattr("services.martech.app._extract_scripts", fake_extract)
    monkeypatch.setattr("services.martech.app.cms_fingerprints", {})
    monkeypatch.setattr("services.martech.app.ENABLE_WAPPALYZER", True)

    result = await services.martech.app.analyze_url(
        "http://example.com", debug=True
    )
    cms = result["cms"]
    assert "WordPress" in cms.get("uncategorized", {})

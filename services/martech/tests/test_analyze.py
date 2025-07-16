import os
import sys
import httpx
import requests
from fastapi.testclient import TestClient
from httpx import Response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.martech import app as app_module


class FakeResponse:
    def __init__(self, text: str):
        self.text = text
        self.status_code = 200
        self.url = "https://example.com"
        self.headers = {}

    def raise_for_status(self):
        pass


def _patch_network(monkeypatch, html: str):
    async def fake_async_get(self, url, *a, **k):
        return Response(200, text=html, request=httpx.Request("GET", url))

    def fake_sync_get(self, url, *a, **k):
        return Response(200, text=html, request=httpx.Request("GET", url))

    monkeypatch.setattr("httpx.AsyncClient.get", fake_async_get, raising=False)
    monkeypatch.setattr("httpx.Client.get", fake_sync_get, raising=False)
    monkeypatch.setattr(
        "requests.get",
        lambda url, *a, **k: FakeResponse(html),
    )


class FakeApp:
    name = "jQuery"
    version = "3.6.0"


class FakeWapp:
    def analyze(self, page):
        return [FakeApp]


def test_analyze_jquery(monkeypatch):
    html = "<html><script src='https://code.jquery.com/jquery-3.6.0.min.js'></script></html>"
    _patch_network(monkeypatch, html)
    monkeypatch.setattr(app_module, "wappalyzer", FakeWapp())

    with TestClient(app_module.app) as client:
        resp = client.post("/analyze", json={"url": "https://example.com"})
    assert resp.status_code == 200
    tech_names = [t["name"] for t in resp.json().get("technologies", [])]
    assert "jQuery" in tech_names

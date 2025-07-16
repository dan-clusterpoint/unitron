import os
import sys
import httpx
import requests
from fastapi.testclient import TestClient
from httpx import Response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "martech")))

import services.gateway.gateway.app as gateway_module
from services.gateway.gateway.app import app as gateway_app
from services.gateway.gateway import models as gmodels
from services.martech import app as martech_app


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
        "requests.get", lambda url, *a, **k: FakeResponse(html)
    )


class FakeApp:
    name = "jQuery"
    version = "3.6.0"


class FakeWapp:
    def analyze(self, page):
        return [FakeApp]


def test_gateway_e2e(monkeypatch):
    html = "<html><script src='https://code.jquery.com/jquery-3.6.0.min.js'></script></html>"
    _patch_network(monkeypatch, html)
    monkeypatch.setattr(martech_app, "wappalyzer", FakeWapp())

    async def patched_martech_call(m: gmodels.MartechIn):
        async with httpx.AsyncClient(app=martech_app.app, base_url="http://martech") as ac:
            r = await ac.post("/analyze", json={"url": str(m.url)})
        data = r.json()
        return gmodels.GatewayMartechOut(
            core=data.get("core", {}).get("names", []),
            adjacent=data.get("adjacent", {}).get("names", []),
            broader=data.get("broader", {}).get("names", []),
            competitors=data.get("competitors", {}).get("names", []),
            technologies=data.get("technologies", []),
        )

    monkeypatch.setattr(gateway_module, "_martech_call", patched_martech_call)

    with TestClient(gateway_app) as client:
        resp = client.post("/analyze", json={"martech": {"url": "https://example.com"}})
    assert resp.status_code == 200
    data = resp.json()
    tech_names = [t["name"] for t in data["martech"]["technologies"]]
    assert "jQuery" in tech_names

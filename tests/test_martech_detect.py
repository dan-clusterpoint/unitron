import os
import sys
import pytest
from httpx import Response, Request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.martech.detector import detect, DetectionError

@pytest.mark.asyncio
async def test_detect_empty(monkeypatch):
    async def fake_get(self, url):
        return Response(200, text="", request=Request("GET", url))
    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    res = await detect("https://example.com")
    assert res["core"] == []
    assert res["adjacent"] == []
    assert res["broader"] == []
    assert res["competitors"] == []

@pytest.mark.asyncio
async def test_detect_google_analytics(monkeypatch):
    html = "<script>window.gtag('config', 'UA-XXXXX');</script>"
    async def fake_get(self, url):
        return Response(200, text=html, request=Request("GET", url))
    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    res = await detect("https://example.com")
    assert "google-analytics" in res["core"]

@pytest.mark.asyncio
async def test_detect_failure(monkeypatch):
    async def fake_get(self, url):
        raise Exception("network down")
    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    with pytest.raises(DetectionError):
        await detect("https://example.com")


@pytest.mark.asyncio
async def test_detect_adobe(monkeypatch):
    # load first 500 lines of adobe.com to simulate
    html = (
        '<script src="https://www.googletagmanager.com/gtm.js?id=GTM-ABC123"></script>'
        '<script src="https://www.google-analytics.com/analytics.js"></script>'
    )

    async def fake_get(self, url):
        return Response(200, text=html, request=Request("GET", url))

    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    res = await detect("https://www.adobe.com")
    assert "google-tag-manager" in res["core"]
    assert "google-analytics" in res["core"]


@pytest.mark.asyncio
async def test_detect_adobe_com(monkeypatch):
    # Simulate page with Adobe Analytics embed
    html = (
        '<script src="https://assets.adobedtm.com/launch-ENabcdef.min.js"></script>'
        '<script>var s=new AppMeasurement();</script>'
        '<script src="https://www.omniture.com/js/omniture.js"></script>'
    )

    async def fake_get(self, url):
        return Response(200, text=html)

    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    res = await detect("https://www.adobe.com")
    assert "adobe-analytics" in res["core"], f"Expected adobe-analytics in core, got {res['core']}"

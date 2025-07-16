import pytest
from httpx import Response, Request
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

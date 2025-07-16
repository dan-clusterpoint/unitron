import pytest
import httpx
from httpx import Response

from services.martech.detector import detect, DetectionError


# Basic empty page
@pytest.mark.asyncio
async def test_detect_empty(monkeypatch):
    async def fake_get(self, url):
        return Response(200, text="", request=httpx.Request("GET", url))
    monkeypatch.setattr("httpx.AsyncClient.get", fake_get, raising=False)
    res = await detect("https://example.com")
    assert res["core"]["vendors"] == []


# Adobe synthetic snippet
@pytest.mark.asyncio
async def test_detect_adobe(monkeypatch):
    html = '''
    <script src="https://assets.adobedtm.com/launch-ENabcd123.min.js"></script>
    <script>var s=new AppMeasurement();</script>
    '''
    async def fake_get(self, url):
        return Response(200, text=html, request=httpx.Request("GET", url))
    monkeypatch.setattr("httpx.AsyncClient.get", fake_get, raising=False)
    res = await detect("https://www.adobe.com")
    prods = [p["product"] for p in res["core"]["vendors"]]
    assert "adobe-analytics" in prods


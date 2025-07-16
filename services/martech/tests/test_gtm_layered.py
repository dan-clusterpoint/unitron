import pytest
from services.martech.detector import detect

# Lightweight response stub to satisfy both httpx and requests patches
class _Resp:
    def __init__(self, text, status_code=200, headers=None, url="https://example.com"):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}
        self.url = url
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

@pytest.mark.asyncio
async def test_detect_gtm_container(monkeypatch):
    # Primary HTML w/ GTM snippet, plus Launch script
    html_primary = '''
    <html><head>
      <script async src="https://www.googletagmanager.com/gtm.js?id=GTM-UNITRON"></script>
      <script src="https://assets.adobedtm.com/launch-ENabcd.min.js"></script>
    </head></html>'''

    # GTM JS containing GA & FB
    gtm_js = "https://www.google-analytics.com/analytics.js https://connect.facebook.net/en_US/fbevents.js"

    def fake_requests_get(url, timeout=10):
        if "gtm.js?id=GTM-UNITRON" in url:
            return _Resp(gtm_js, url=url)
        return _Resp(html_primary, url=url)

    async def fake_httpx_get(self, url):
        # all httpx fetches return primary html or sample script
        return _Resp(html_primary, url=url)

    monkeypatch.setattr("services.martech.detector.requests.get", fake_requests_get)
    monkeypatch.setattr("services.martech.detector.httpx.AsyncClient.get", fake_httpx_get, raising=False)

    buckets, dbg = await detect("https://example.com", return_debug=True)
    names_core = buckets["core"]["names"]
    assert "google-analytics" in names_core
    assert "adobe-analytics" in names_core or "google-tag-manager" in names_core
    assert dbg.get("gtm_id") == "GTM-UNITRON"

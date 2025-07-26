import pytest
from pathlib import Path
import httpx
import services.martech.app

from services.shared.fingerprint import load_fingerprints, match_fingerprints

CMS_FP = load_fingerprints(
    Path(__file__).resolve().parents[1] / "cms_fingerprints.yaml"
)


@pytest.fixture
def wordpress_page():
    html = (
        "<html><link href='/wp-content/style.css'>"
        "<meta name='generator' content='WordPress'>"
        "<script src='wp-emoji-release.min.js'></script></html>"
    )
    headers = {"X-Generator": "WordPress"}
    cookies = {"wordpress_test_cookie": "1"}
    return html, "https://example.com/wp-content/", headers, cookies, []


@pytest.fixture
def aem_page():
    html = (
        "<div class='aem-Grid' data-cq-data-path>"
        "<script src='/libs/granite/ui.js'></script></div>"
    )
    headers = {"Server": "Apache Sling"}
    cookies = {}
    resources = []
    return html, "https://example.com/", headers, cookies, resources


@pytest.fixture
def random_page():
    html = "<html>Hello</html>"
    return html, "https://example.com/", {}, {}, []


def test_match_wordpress(wordpress_page):
    html, url, headers, cookies, resources = wordpress_page
    result = match_fingerprints(html, url, headers, cookies, resources, CMS_FP)
    wp = result["oss_cms"].get("WordPress")
    assert wp is not None
    assert wp["confidence"] >= 1


def test_match_aem(aem_page):
    html, url, headers, cookies, resources = aem_page
    result = match_fingerprints(html, url, headers, cookies, resources, CMS_FP)
    aem = result["enterprise_cms"].get("Adobe Experience Manager (AEM)")
    assert aem is not None
    assert aem["confidence"] >= 1


def test_no_match(random_page):
    html, url, headers, cookies, resources = random_page
    result = match_fingerprints(html, url, headers, cookies, resources, CMS_FP)
    assert result == {}


@pytest.mark.asyncio
async def test_analyze_url_handles_fetch_error(monkeypatch):
    async def boom_fetch(_client, url):
        req = httpx.Request("GET", url)
        raise httpx.RequestError("fail", request=req)

    monkeypatch.setattr("services.martech.app._fetch", boom_fetch)

    result = await services.martech.app.analyze_url(
        "https://wp.example.com/wp-content/",
        debug=True,
    )
    cms = result["cms"]
    assert "WordPress" not in cms.get("oss_cms", {})
    assert result["network_error"] is True

import http.cookies

import pytest
import yaml
from pathlib import Path

from services.shared.utils import detect_vendors

FINGERPRINTS = yaml.safe_load(
    open(Path(__file__).resolve().parents[1] / "fingerprints.yaml")
)


@pytest.fixture
def segment_full():
    html = (
        "<script src='https://cdn.segment.com/analytics.js'></script>"
        "<script>analytics.load('XYZ');</script>"
    )
    cookies = {}
    for header in [
        "ajs_anonymous_id=abc; Path=/",
        "ajs_user_id=123; Path=/",
    ]:
        c = http.cookies.SimpleCookie()
        c.load(header)
        cookies.update({k: v.value for k, v in c.items()})
    return html, cookies


@pytest.fixture
def segment_partial():
    html = "<script>analytics.load('XYZ');</script>"
    c = http.cookies.SimpleCookie()
    c.load("ajs_anonymous_id=abc; Path=/")
    cookies = {k: v.value for k, v in c.items()}
    return html, cookies


@pytest.fixture
def random_page():
    html = "<script>analyticsLoader('foo');</script>"
    return html, {}


@pytest.fixture
def ga_gtm_url():
    html = (
        "<script src='https://www.googletagmanager.com/gtag/js?id=G-XYZ'>" "</script>"
    )
    return html, {}


@pytest.fixture
def ga_datalayer():
    html = "<script>window.dataLayer = window.dataLayer || [];</script>"
    return html, {}


@pytest.fixture
def ga_gtag():
    html = "<script>gtag('config','G-XYZ');</script>"
    return html, {}


@pytest.fixture
def adobe_satellite():
    html = "<script>window._satellite = window._satellite || {};</script>"
    return html, {}


@pytest.fixture
def hubspot():
    html = (
        "<script src='https://js.hs-analytics.net/analytics.js'></script>"
        "<script>_hsq.push(['track']);</script>"
    )
    return html, {}


@pytest.fixture
def meta_pixel():
    html = (
        "<script src='https://connect.facebook.net/en_US/"
        "fbevents.js'></script>"
        "<script>fbq('init','123');</script>"
    )
    return html, {}


@pytest.fixture
def ga_id():
    html = "<script>var id='G-ABCD123';</script>"
    return html, {}


@pytest.fixture
def hotjar_window():
    html = "<script>window.hotjar = window.hotjar || function(){};</script>"
    return html, {}


def test_detect_vendors_true_positive(segment_full):
    html, cookies = segment_full
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    seg = vendors["core"]["Segment"]
    assert seg["confidence"] > 0
    assert r"analytics\.load" in seg["evidence"]["html"][0]


def test_detect_vendors_partial(segment_partial):
    html, cookies = segment_partial
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    seg = vendors["core"]["Segment"]
    assert seg["confidence"] > 0
    assert "asset_host" not in seg["evidence"]


def test_detect_vendors_false_positive(random_page):
    html, cookies = random_page
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    assert vendors == {}


def test_detect_ga_via_gtm(ga_gtm_url):
    html, cookies = ga_gtm_url
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert ga["confidence"] > 0
    assert "asset_host" in ga["evidence"]


def test_detect_ga_via_datalayer(ga_datalayer):
    html, cookies = ga_datalayer
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert ga["confidence"] > 0
    assert r"window\.dataLayer" in ga["evidence"]["html"][0]


def test_detect_ga_via_gtag(ga_gtag):
    html, cookies = ga_gtag
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert ga["confidence"] > 0
    assert r"gtag\(" in ga["evidence"]["html"][0]


def test_detect_adobe_via_satellite(adobe_satellite):
    html, cookies = adobe_satellite
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    adobe = vendors["core"]["Adobe Analytics"]
    assert adobe["confidence"] > 0
    assert r"window\._satellite" in adobe["evidence"]["html"][0]


def test_detect_with_external_scripts():
    html = "<script src='/ga.js'></script><script src='/seg.js'></script>"
    vendors = detect_vendors(
        html,
        {},
        [],
        FINGERPRINTS,
        script_bodies=[
            "ga('create','UA-1','auto');",
            "analytics.load('XYZ');",
        ],
    )
    core = vendors["core"]
    assert "Google Analytics" in core
    assert "Segment" in core


def test_detect_hubspot(hubspot):
    html, cookies = hubspot
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    hs = vendors["core"]["HubSpot"]
    assert hs["confidence"] > 0


def test_detect_meta_pixel(meta_pixel):
    html, cookies = meta_pixel
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    mp = vendors["core"]["Meta Pixel"]
    assert mp["confidence"] > 0


def test_detect_ga_via_id(ga_id):
    html, cookies = ga_id
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert ga["confidence"] > 0


def test_detect_hotjar_via_window(hotjar_window):
    html, cookies = hotjar_window
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    hj = vendors["adjacent"]["Hotjar"]
    assert hj["confidence"] > 0

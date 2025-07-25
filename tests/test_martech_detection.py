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
        "<script src='https://www.googletagmanager.com/gtag/js?id=G-XYZ'>"
        "</script>"
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


def test_detect_vendors_true_positive(segment_full):
    html, cookies = segment_full
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    seg = vendors["core"]["Segment"]
    assert pytest.approx(1.0, abs=0.01) == seg["confidence"]
    assert r"analytics\.load" in seg["evidence"]["scripts"][0]


def test_detect_vendors_partial(segment_partial):
    html, cookies = segment_partial
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    seg = vendors["core"]["Segment"]
    assert pytest.approx(0.33, abs=0.01) == seg["confidence"]
    assert len(seg["evidence"]["hosts"]) == 0


def test_detect_vendors_false_positive(random_page):
    html, cookies = random_page
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    assert vendors == {}


def test_detect_ga_via_gtm(ga_gtm_url):
    html, cookies = ga_gtm_url
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert pytest.approx(0.31, abs=0.01) == ga["confidence"]
    assert len(ga["evidence"]["hosts"]) == 2


def test_detect_ga_via_datalayer(ga_datalayer):
    html, cookies = ga_datalayer
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert pytest.approx(0.08, abs=0.01) == ga["confidence"]
    assert r"window\.dataLayer" in ga["evidence"]["scripts"][0]


def test_detect_ga_via_gtag(ga_gtag):
    html, cookies = ga_gtag
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    ga = vendors["core"]["Google Analytics"]
    assert pytest.approx(0.08, abs=0.01) == ga["confidence"]
    assert r"gtag\(" in ga["evidence"]["scripts"][0]


def test_detect_adobe_via_satellite(adobe_satellite):
    html, cookies = adobe_satellite
    vendors = detect_vendors(html, cookies, [], FINGERPRINTS)
    adobe = vendors["core"]["Adobe Analytics"]
    assert pytest.approx(0.10, abs=0.01) == adobe["confidence"]
    assert r"window\._satellite" in adobe["evidence"]["scripts"][0]


def test_detect_with_external_scripts():
    html = "<script src='/ga.js'></script><script src='/seg.js'></script>"
    vendors = detect_vendors(
        html,
        {},
        [],
        FINGERPRINTS,
        script_bodies=["ga('create','UA-1','auto');", "analytics.load('XYZ');"],
    )
    core = vendors["core"]
    assert "Google Analytics" in core
    assert "Segment" in core

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
    assert pytest.approx(0.36, abs=0.01) == ga["confidence"]
    assert len(ga["evidence"]["hosts"]) == 2

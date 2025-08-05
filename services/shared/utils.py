from typing import Sequence
from functools import lru_cache
from Wappalyzer import Wappalyzer, WebPage


def ping() -> bool:
    return True


def normalize_url(url: str) -> str:
    """Return a cleaned version of ``url``.

    The hostname is lower‑cased and any trailing slash is removed. If no scheme
    is present ``https://`` is assumed.
    """
    from urllib.parse import urlparse, urlunparse

    cleaned = url.strip()
    if "://" not in cleaned:
        cleaned = "https://" + cleaned

    parsed = urlparse(cleaned)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    return urlunparse((scheme, netloc, path, "", "", ""))


@lru_cache(maxsize=1)
def _get_wappalyzer() -> Wappalyzer:
    """Return a cached ``Wappalyzer`` instance."""

    return Wappalyzer.latest()


def detect_vendors(
    html: str,
    cookies: dict[str, str],
    urls: Sequence[str] | None = None,
    fingerprints: dict[str, list[dict]] | None = None,
    script_bodies: Sequence[str] | None = None,
) -> dict[str, list[str]]:
    """Return detected technologies grouped by category.

    ``urls`` and ``fingerprints`` parameters are retained for backwards
    compatibility but ignored. ``script_bodies`` may contain additional
    JavaScript text which is appended to the HTML prior to analysis.
    """

    from bs4 import BeautifulSoup

    if script_bodies:
        html = "\n".join([html, *script_bodies])

    # Collect script URLs to mirror previous behaviour even though
    # python-wappalyzer does not currently use them.
    soup = BeautifulSoup(html, "html.parser")
    if urls:
        srcs = [*urls]
    else:
        srcs = []
    srcs.extend(
        tag.get("src") or "" for tag in soup.find_all("script") if tag.get("src")
    )

    webpage = WebPage("https://example.com", html, {})
    wappalyzer = _get_wappalyzer()
    try:
        detected = wappalyzer.analyze_with_categories(webpage)
    except Exception:
        detected = {}
    return {cat: sorted(techs) for cat, techs in detected.items()}

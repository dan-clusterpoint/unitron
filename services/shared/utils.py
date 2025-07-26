
from typing import Sequence
from .fingerprint import (
    DEFAULT_FINGERPRINTS,
    match_fingerprints,
)


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


def detect_vendors(
    html: str,
    cookies: dict[str, str],
    urls: Sequence[str] | None = None,
    fingerprints: dict[str, list[dict]] | None = None,
    script_bodies: Sequence[str] | None = None,
) -> dict[str, dict]:
    """Return detected analytics vendors with confidence scores and evidence.

    ``urls`` is an optional collection of additional resource URLs (script
    sources, image URLs, resource hints, etc.) that should be considered when
    matching vendor host fingerprints. ``script_bodies`` may contain additional
    JavaScript text (e.g. from externally hosted scripts) which will be matched
    against script patterns.
    """
    from bs4 import BeautifulSoup

    if fingerprints is None:
        fingerprints = DEFAULT_FINGERPRINTS

    soup = BeautifulSoup(html, "html.parser")
    srcs = [
        tag.get("src") or ""
        for tag in soup.find_all("script")
        if tag.get("src")
    ]
    if urls:
        srcs.extend(urls)

    if script_bodies:
        html = "\n".join([html, *script_bodies])

    return match_fingerprints(html, "", {}, cookies, srcs, fingerprints)

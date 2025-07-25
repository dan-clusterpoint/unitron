
from typing import Sequence


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
) -> dict[str, dict]:
    """Return detected analytics vendors with confidence scores and evidence.

    ``urls`` is an optional collection of additional resource URLs (script
    sources, image URLs, resource hints, etc.) that should be considered when
    matching vendor host fingerprints.
    """
    import re
    import yaml  # type: ignore
    from pathlib import Path
    from bs4 import BeautifulSoup

    fp_path = Path(__file__).resolve().parents[2] / "fingerprints.yaml"
    with open(fp_path) as f:
        fingerprints = yaml.safe_load(f)

    soup = BeautifulSoup(html, "html.parser")
    srcs = [tag.get("src", "") for tag in soup.find_all("script")]
    if urls:
        srcs.extend(urls)
    inline = [
        tag.string or ""
        for tag in soup.find_all("script")
        if not tag.get("src")
    ]

    results: dict[str, dict] = {}
    for bucket, vendors in fingerprints.items():
        bucket_hits: dict[str, dict] = {}
        for vendor in vendors:
            score = 0
            max_score = 0
            evidence: dict[str, list[str]] = {
                "hosts": [],
                "scripts": [],
                "cookies": [],
            }

            hosts = [re.compile(h, re.I) for h in vendor.get("hosts", [])]
            max_score += len(hosts) * 2
            for rx in hosts:
                if any(rx.search(src) for src in srcs):
                    evidence["hosts"].append(rx.pattern)
                    score += 2

            scripts = [re.compile(s, re.I) for s in vendor.get("scripts", [])]
            max_score += len(scripts)
            for rx in scripts:
                if any(rx.search(text) for text in inline):
                    evidence["scripts"].append(rx.pattern)
                    score += 1

            cookie_names = vendor.get("cookies", [])
            max_score += len(cookie_names) * 2
            for name in cookie_names:
                if name in cookies:
                    evidence["cookies"].append(name)
                    score += 2

            if score:
                confidence = round(score / max(max_score, 1), 2)
                bucket_hits[vendor["name"]] = {
                    "confidence": confidence,
                    "evidence": evidence,
                }

        if bucket_hits:
            results[bucket] = bucket_hits

    return results

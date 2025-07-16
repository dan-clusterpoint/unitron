import re
import logging
from typing import Dict, List
import httpx

log = logging.getLogger("martech.detector")

class DetectionError(Exception):
    pass

async def detect(url: str) -> Dict[str, List[str]]:
    """
    Fetch the page at `url` and apply simple signatures to build:
      - core
      - adjacent
      - broader
      - competitors
    """
    signatures = {
        "core": [
            # Inline GA
            (re.compile(r"gtag\("), "google-analytics"),
            (re.compile(r"analytics\.js"), "google-analytics"),
            # External GA script
            (
                re.compile(r"https?://www\.google-analytics\.com/analytics\.js"),
                "google-analytics",
            ),
            # Google Tag Manager script
            (
                re.compile(
                    r"https?://www\.googletagmanager\.com/gtm\.js\?id=GTM-[A-Z0-9]+"
                ),
                "google-tag-manager",
            ),
            # Adobe Analytics (AppMeasurement, Omniture, DTM, AEP Web SDK)
            (re.compile(r"AppMeasurement(\.js)?"), "adobe-analytics"),
            (re.compile(r"omniture"), "adobe-analytics"),
            (re.compile(r"https?://[^ ]*satelliteLib"), "adobe-analytics"),
            (
                re.compile(r"https?://[^ ]*experience\.adobedtm\.com"),
                "adobe-analytics",
            ),
        ],
        "adjacent": [
            (re.compile(r"https?://js\.hs-scripts\.com/"), "hubspot"),
            (re.compile(r"https?://.+\.mktoweb\.com/"), "marketo"),
        ],
        "broader": [
            (re.compile(r"https?://cdn\.segment\.com/"), "segment"),
        ],
        "competitors": [
            # Extend with your competitor patterns
        ],
    }
    result = {k: [] for k in signatures}
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code >= 400:
                raise httpx.HTTPStatusError("request failed", request=r.request, response=r)
            text = r.text[:1_000_000]  # cap at 1MB
            headers = " ".join(f"{k}:{v}" for k, v in r.headers.items())
        haystack = headers + "\n" + text
        for category, rules in signatures.items():
            for pattern, tag in rules:
                if pattern.search(haystack):
                    result[category].append(tag)
        # dedupe & sort
        for k in result:
            result[k] = sorted(set(result[k]))
        return result
    except Exception as e:
        log.exception("Detection failed for %s: %s", url, e)
        raise DetectionError(f"Failed to detect tech on {url}: {e}") from e

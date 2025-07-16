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
            (re.compile(r"gtag\("), "google-analytics"),
            (re.compile(r"analytics\.js"), "google-analytics"),
            (re.compile(r"GTM-[A-Z0-9]+"), "google-tag-manager"),
            (re.compile(r"s_code\.js"), "adobe-analytics"),
        ],
        "adjacent": [
            (re.compile(r"js\.hs-scripts\.com"), "hubspot"),
            (re.compile(r"mktow1"), "marketo"),
        ],
        "broader": [
            (re.compile(r"cdn\.segment\.com"), "segment"),
        ],
        "competitors": [
            # add competitor rules here
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

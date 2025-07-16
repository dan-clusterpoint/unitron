import re, logging, urllib.parse
from typing import Dict, List, Tuple, Any
import httpx

log = logging.getLogger("martech.detector")

class DetectionError(Exception):
    ...

# signature tuple: (compiled_regex, product, bucket, weight)
SIGS: List[Tuple[re.Pattern, str, str, float]] = []
_FLAGS = re.IGNORECASE

def _compile_sigs():
    global SIGS
    SIGS = [
        # Google Analytics / GTM
        (re.compile(r"gtag\s*\(", _FLAGS), "google-analytics", "core", 0.6),
        (re.compile(r"google-analytics\.com/analytics\.js", _FLAGS), "google-analytics", "core", 0.7),
        (re.compile(r"googletagmanager\.com/gtm\.js", _FLAGS), "google-tag-manager", "core", 0.8),

        # Adobe Analytics / Launch / AppMeasurement / DTM / Alloy
        (re.compile(r"appmeasurement(?:\.min)?\.js", _FLAGS), "adobe-analytics", "core", 0.9),
        (re.compile(r"adobedtm\.com/launch-", _FLAGS), "adobe-analytics", "core", 0.9),
        (re.compile(r"satellitelib", _FLAGS), "adobe-analytics", "core", 0.7),
        (re.compile(r"experience\.adobedtm\.com", _FLAGS), "adobe-analytics", "core", 0.8),
        (re.compile(r"omniture", _FLAGS), "adobe-analytics", "core", 0.4),
        (re.compile(r"alloy\.js", _FLAGS), "adobe-analytics", "core", 0.7),

        # HubSpot
        (re.compile(r"js\.hs-scripts\.com", _FLAGS), "hubspot", "adjacent", 0.8),
        # Marketo
        (re.compile(r"\.mktoweb\.com", _FLAGS), "marketo", "adjacent", 0.8),
        # Segment
        (re.compile(r"cdn\.segment\.com", _FLAGS), "segment", "broader", 0.8),
    ]

_compile_sigs()

SCRIPT_RE = re.compile(r"<script[^>]+src=['\"]([^'\"]+)['\"]", re.IGNORECASE)

async def _fetch_text(client: httpx.AsyncClient, url: str, limit: int) -> str:
    r = await client.get(url)
    r.raise_for_status()
    return r.text[:limit]

def _abs_url(base: str, maybe_rel: str) -> str:
    return urllib.parse.urljoin(base, maybe_rel)

def _scan(haystack: str) -> Dict[str, Dict[str, Any]]:
    """Return bucket->product->hit dict."""
    bucket_hits: Dict[str, Dict[str, Any]] = {}
    for pat, product, bucket, weight in SIGS:
        if pat.search(haystack):
            bucket_hits.setdefault(bucket, {})
            hit = bucket_hits[bucket].setdefault(product, {"product":product,"confidence":0.0,"evidence":[]})
            hit["confidence"] = max(hit["confidence"], weight)
            hit["evidence"].append(pat.pattern)
    return bucket_hits

async def detect(url: str, max_scripts: int = 20, return_debug: bool = False):
    """
    Multi-pass detection: fetch main HTML, extract script srcs, fetch a sample of each,
    run signatures across aggregate text. Returns (data[, debug]).
    """
    debug: Dict[str, Any] = {"primary_url": url, "scripts_fetched": [], "errors": []}
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers={"User-Agent":"UnitronMartechBot/0.2"}) as client:
            primary_html = await _fetch_text(client, url, 1_000_000)
            debug["primary_len"] = len(primary_html)

            scripts = SCRIPT_RE.findall(primary_html)[:max_scripts]
            abs_scripts = [_abs_url(url, s) for s in scripts]
            debug["scripts_found"] = abs_scripts

            bodies = [primary_html]
            for s in abs_scripts:
                try:
                    txt = await _fetch_text(client, s, 64_000)
                    bodies.append(txt)
                    debug["scripts_fetched"].append(s)
                except Exception as e:  # best-effort
                    debug["errors"].append(f"{s}: {e}")

    except Exception as e:
        log.exception("Primary fetch failed for %s: %s", url, e)
        raise DetectionError(f"primary fetch failed: {e}") from e

    haystack = "\n".join(bodies)
    bucket_hits = _scan(haystack)

    final = {"core":[], "adjacent":[], "broader":[], "competitors":[]}
    for bucket, prodmap in bucket_hits.items():
        final[bucket] = sorted(prodmap.values(), key=lambda d: d["confidence"], reverse=True)

    if return_debug:
        return final, debug
    return final

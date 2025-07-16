import re, logging, urllib.parse
from typing import Dict, List, Tuple, Any
import httpx, requests

try:
    from Wappalyzer import Wappalyzer, WebPage  # new package name >=1.2.0
except Exception:  # fallback to older lowercase package or missing module
    try:
        from wappalyzer import Wappalyzer, WebPage  # type: ignore
    except Exception:  # unavailable
        Wappalyzer = WebPage = None  # type: ignore

log = logging.getLogger("martech.detector")

class DetectionError(Exception):
    ...

_FLAGS = re.IGNORECASE

# Map Wappalyzer app names to (product, bucket)
WAPP_MAP = {
    "Adobe Analytics": ("adobe-analytics","core"),
    "Adobe Experience Platform Web SDK": ("adobe-analytics","core"),
    "Google Analytics": ("google-analytics","core"),
    "Google Tag Manager": ("google-tag-manager","core"),
    "HubSpot": ("hubspot","adjacent"),
    "Marketo": ("marketo","adjacent"),
    "Segment": ("segment","broader"),
    # extend as needed
}

# Regex fallback across aggregated text
REGEX_RULES = [
    (re.compile(r"appmeasurement(?:\.min)?\.js", _FLAGS), "adobe-analytics","core",0.9),
    (re.compile(r"adobedtm\.com/launch-", _FLAGS), "adobe-analytics","core",0.9),
    (re.compile(r"satellitelib", _FLAGS), "adobe-analytics","core",0.7),
    (re.compile(r"experience\.adobedtm\.com", _FLAGS), "adobe-analytics","core",0.8),
    (re.compile(r"omniture", _FLAGS), "adobe-analytics","core",0.4),
    (re.compile(r"alloy\.js", _FLAGS), "adobe-analytics","core",0.7),
    (re.compile(r"googletagmanager\.com", _FLAGS), "google-tag-manager","core",0.8),
    (re.compile(r"google-analytics\.com", _FLAGS), "google-analytics","core",0.7),
    (re.compile(r"js\.hs-scripts\.com", _FLAGS), "hubspot","adjacent",0.8),
    (re.compile(r"\.mktoweb\.com", _FLAGS), "marketo","adjacent",0.8),
    (re.compile(r"cdn\.segment\.com", _FLAGS), "segment","broader",0.8),
]

SCRIPT_RE = re.compile(r"<script[^>]+src=['\"]([^'\"]+)['\"]", re.IGNORECASE)
GTM_ID_RE = re.compile(r"googletagmanager\.com/gtm\.js\?id=(GTM-[A-Z0-9]+)", re.IGNORECASE)

# Vendor domain map used when crawling GTM container JS
GTM_VENDOR_DOMAIN_MAP = {
    "googletagmanager.com": ("google-tag-manager","core"),
    "google-analytics.com": ("google-analytics","core"),
    "analytics.google.com": ("google-analytics","core"),
    "googletagservices.com": ("google-marketing-platform","adjacent"),
    "doubleclick.net": ("google-marketing-platform","adjacent"),
    "facebook.com/tr": ("facebook-pixel","adjacent"),
    "connect.facebook.net": ("facebook-pixel","adjacent"),
    "snap.licdn.com": ("linkedin-insight","adjacent"),
    "bat.bing.com": ("microsoft-ads","adjacent"),
    "adobedtm.com": ("adobe-analytics","core"),
    "omtrdc.net": ("adobe-analytics","core"),
    "demdex.net": ("adobe-analytics","core"),
    # add more as needed
}

def _abs(base: str, rel: str) -> str:
    return urllib.parse.urljoin(base, rel)

async def _fetch_text(client: httpx.AsyncClient, url: str, limit: int) -> str:
    r = await client.get(url)
    r.raise_for_status()
    return r.text[:limit]

def _apply_regex(haystack: str):
    for pat, prod, bucket, weight in REGEX_RULES:
        if pat.search(haystack):
            yield prod, bucket, weight, pat.pattern

def _add_signal(vendor_map: Dict[str,Any], product: str, bucket: str, weight: float, sig_type: str, value: str, url: str|None=None):
    rec = vendor_map.setdefault(product, {"bucket":bucket,"confidence":0.0,"signals":[]})
    if weight > rec["confidence"]:
        rec["confidence"] = weight
    rec["signals"].append({"type":sig_type,"value":value,"url":url})

def _collapse(vendor_map: Dict[str,Any]) -> Dict[str,Any]:
    buckets = {"core":[], "adjacent":[], "broader":[], "competitors":[]}
    for prod,data in vendor_map.items():
        buckets[data["bucket"]].append({
            "product": prod,
            "confidence": data["confidence"],
            "signals": data["signals"],
        })
    for b in buckets:
        buckets[b].sort(key=lambda d: d["confidence"], reverse=True)
    # add names
    for b in buckets:
        buckets[b] = {"vendors": buckets[b], "names":[v["product"] for v in buckets[b]]}
    return buckets

def _crawl_gtm(container_id: str, debug: Dict[str,Any]) -> List[tuple]:
    """
    Fetch GTM container JS and scan for vendor domains.
    Returns list of (product,bucket,weight,domain).
    """
    url = f"https://www.googletagmanager.com/gtm.js?id={container_id}"
    debug.setdefault("gtm", {})["fetch_url"] = url
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        js_snip = resp.text[:256_000]
        debug["gtm"]["len"] = len(resp.text)
    except Exception as e:
        debug["gtm"]["error"] = str(e)
        return []
    hits = []
    for domain, (prod,bucket) in GTM_VENDOR_DOMAIN_MAP.items():
        if domain.lower() in js_snip.lower():
            weight = 0.6 if bucket=="adjacent" else 0.8
            hits.append((prod,bucket,weight,domain))
    return hits

async def detect(url: str, max_scripts=20, return_debug=False):
    debug: Dict[str,Any] = {"primary_url":url,"scripts_found":[], "scripts_fetched":[], "errors":[]}
    vendor_map: Dict[str,Any] = {}

    # ---- primary fetch
    async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers={"User-Agent":"UnitronMartechBot/0.3"}, trust_env=False) as client:
        try:
            html = await _fetch_text(client, url, 1_000_000)
            debug["primary_len"] = len(html)
        except Exception as e:
            log.exception("primary fetch failed: %s", e)
            raise DetectionError(f"primary fetch failed: {e}") from e

        # accumulate content
        parts: List[str] = [html]

        # extract script src
        scripts = SCRIPT_RE.findall(html)[:max_scripts]
        abs_scripts = [_abs(url, s) for s in scripts]
        debug["scripts_found"] = abs_scripts

        # fetch sample
        for s in abs_scripts:
            try:
                txt = await _fetch_text(client, s, 64_000)
                parts.append(txt)
                debug["scripts_fetched"].append(s)
            except Exception as e:
                debug["errors"].append(f"{s}: {e}")

    # ---- Wappalyzer
    apps = []
    if Wappalyzer and WebPage:
        try:
            resp = requests.get(url, timeout=10)
            page = WebPage.new_from_response(resp)
            wapp = Wappalyzer.latest()
            apps = wapp.analyze(page)
        except Exception as e:
            debug["errors"].append(f"wappalyzer:{e}")
    debug["wappalyzer_apps"] = apps
    for app in apps:
        if app in WAPP_MAP:
            prod,bucket = WAPP_MAP[app]
            _add_signal(vendor_map, prod, bucket, 0.85 if bucket=="core" else 0.7, "wappalyzer", app)

    # ---- regex fallback across aggregated bodies
    agg = "\n".join(parts)
    for prod,bucket,weight,pat in _apply_regex(agg):
        _add_signal(vendor_map, prod, bucket, weight, "regex", pat)

    # ---- GTM Container Crawl v1
    m = GTM_ID_RE.search(agg)
    if m:
        gtm_id = m.group(1)
        debug["gtm_id"] = gtm_id
        for prod,bucket,weight,domain in _crawl_gtm(gtm_id, debug):
            _add_signal(vendor_map, prod, bucket, weight, "gtm", domain,
                        url=f"https://www.googletagmanager.com/gtm.js?id={gtm_id}")

    # ---- build buckets
    buckets = _collapse(vendor_map)
    if return_debug:
        return buckets, debug
    return buckets

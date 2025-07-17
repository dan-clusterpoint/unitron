"""
OSS Martech detection helper.

Strategy:
1. Fetch target URL (follow redirects).
2. Run Wappalyzer fingerprints (if available).
3. Run custom regex/header heuristics for high-signal Martech tags.
4. Score each detected technology based on available evidence.
5. Mark competitive platforms (vs Adobe).

Return a list of per-product dictionaries with confidence, evidence and
competitor flag.
"""

from __future__ import annotations
import re
from typing import Dict, List, Set, Any
import httpx
from Wappalyzer import Wappalyzer, WebPage

# ------------------------------------------------------------------ #
#  Martech regex patterns (body search)                              #
# ------------------------------------------------------------------ #
PATTERNS = {
    "Adobe Launch": r"assets\.adobedtm\.com|satelliteLib-",
    "Adobe Analytics": r"AppMeasurement\.js|s_code\.js",
    "Adobe Target": r"mbox\\.js|at\\.js",
    "Google Tag Manager": r"googletagmanager\.com/gtm\.js",
    "Google Analytics": r"gtag\\(|analytics\.js",
    "Sitecore": r"sitecore|sc_itemid|sc_site=",
    "Optimizely": r"optimizely\.com",
    "Salesforce Marketing Cloud": r"pardot|pi\.pardot\.com|exacttarget",
    "Marketo": r"mkt_tok=|marketo",
}

# ------------------------------------------------------------------ #
#  Tier mapping (extend as needed)                                   #
# ------------------------------------------------------------------ #
CORE_KEYWORDS = {"adobe", "analytics", "tag manager", "cms", "marketing", "marketo", "pardot", "launch"}
BROAD_KEYWORDS = {"cdn", "cloud", "security", "hosting"}
# Everything else -> adjacent.

# Competitive platforms to surface explicitly
COMPETITORS: Set[str] = {
    "Sitecore",
    "Optimizely",
    "Salesforce",
    "Salesforce Marketing Cloud",
    "Marketo",
    "Contentful",
    "Acquia",
    "Drupal",
    "WordPress",
    "Google Analytics",
    "Google Tag Manager",
}

def _fetch(url: str, timeout: float = 15.0) -> httpx.Response:
    """Fetch page HTML (GET) with redirects; raise on network errors."""
    headers = {"User-Agent": "UnitronMartechBot/0.1 (+https://example.com/contact)"}
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        resp = client.get(url)
    return resp

def _run_wappalyzer(url: str, html: str) -> Dict[str, List[str]]:
    """Run Wappalyzer detection. We build a WebPage object manually so we can reuse the fetched HTML."""
    wapp = Wappalyzer.latest()
    # WebPage wants to fetch itself by URL; we override by giving html and headers
    # Use from_document so we don't re-fetch (python-Wappalyzer >=0.5)
    try:
        webpage = WebPage(url, html)
    except TypeError:
        # Fallback older API
        webpage = WebPage.new_from_url(url)
    try:
        return wapp.analyze_with_categories(webpage)
    except Exception:
        # fallback minimal detect
        try:
            return wapp.analyze(webpage)
        except Exception:
            return {}

def _regex_hits(html: str, headers: Dict[str, str]) -> Dict[str, str]:
    """Apply regex patterns to HTML and some headers."""
    found = {}
    for name, pat in PATTERNS.items():
        if re.search(pat, html, flags=re.I):
            found[name] = f"pattern:{pat}"
    # header heuristics
    xp = headers.get("x-powered-by", "")
    if "Sitecore" in xp:
        found["Sitecore"] = "header:x-powered-by"
    if "WordPress" in xp:
        found["WordPress"] = "header:x-powered-by"
    return found

def _categorize(name: str, cats: List[str]) -> str:
    """Map to core / adjacent / broader based on name + categories keywords."""
    lname = name.lower()
    cats_lower = [c.lower() for c in cats or []]
    if any(k in lname for k in CORE_KEYWORDS) or any(k in c for c in cats_lower for k in CORE_KEYWORDS):
        return "core"
    if any(k in lname for k in BROAD_KEYWORDS) or any(k in c for c in cats_lower for k in BROAD_KEYWORDS):
        return "broader"
    return "adjacent"

def detect(url: str) -> List[Dict[str, Any]]:
    """Detect marketing technology and return per-product details."""
    resp = _fetch(url)
    html = resp.text
    headers = dict(resp.headers)

    # Wappalyzer and regex/header heuristics
    wapp_hits = _run_wappalyzer(url, html)  # {tech:[cats]}
    re_hits = _regex_hits(html, headers)  # {tech:evidence}

    all_techs = set(wapp_hits) | set(re_hits)
    results: List[Dict[str, Any]] = []

    for tech in sorted(all_techs):
        cats = wapp_hits.get(tech, [])
        evidence: List[str] = [f"wapp:{c}" for c in cats]
        regex_ev = re_hits.get(tech)
        if regex_ev:
            evidence.append(regex_ev)

        confidence = 0.0
        if tech in wapp_hits:
            confidence += 0.5
        if regex_ev:
            if regex_ev.startswith("pattern:"):
                confidence += 0.3
            elif regex_ev.startswith("header:"):
                confidence += 0.2
        confidence = round(min(confidence, 1.0), 2)

        results.append({
            "product": tech,
            "confidence": confidence,
            "evidence": evidence,
            "competitor": tech in COMPETITORS,
        })

    return results

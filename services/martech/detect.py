"""
OSS Martech detection helper.

Strategy:
1. Fetch target URL (follow redirects).
2. Run Wappalyzer fingerprints (if available).
3. Run custom regex/header heuristics for high-signal Martech tags.
4. Map detected tech -> Core / Adjacent / Broader tiers.
5. Mark competitive platforms (vs Adobe).

Return categorized lists + raw evidence for debugging.
"""

from __future__ import annotations
import re
from typing import Dict, List, Set
import httpx
import tldextract
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

def detect(url: str) -> Dict[str, List[str]]:
    """Main detection function: returns dict with keys core/adjacent/broader/competitors/evidence."""
    resp = _fetch(url)
    html = resp.text
    headers = dict(resp.headers)

    # Wappalyzer
    wapp_hits = _run_wappalyzer(url, html)  # {tech:[cats]}
    # Regex heuristics
    re_hits = _regex_hits(html, headers)    # {tech:evidence}

    # Merge
    tech_to_cats: Dict[str, List[str]] = {}
    for tech, cats in wapp_hits.items():
        tech_to_cats[tech] = list(cats) if isinstance(cats, (list, set, tuple)) else [str(cats)]

    for tech, ev in re_hits.items():
        tech_to_cats.setdefault(tech, []).append(ev)

    # Categorize
    core, adjacent, broader, competitors = [], [], [], []
    evidence = {}

    for tech, cats in tech_to_cats.items():
        tier = _categorize(tech, cats)
        if tier == "core":
            core.append(tech)
        elif tier == "broader":
            broader.append(tech)
        else:
            adjacent.append(tech)
        if any(c.lower().startswith("pattern:") for c in cats):
            evidence[tech] = cats
        if tech in COMPETITORS:
            competitors.append(tech)

    # De-dup & sort
    core = sorted(set(core))
    adjacent = sorted(set(adjacent))
    broader = sorted(set(broader))
    competitors = sorted(set(competitors))

    return {
        "core": core,
        "adjacent": adjacent,
        "broader": broader,
        "competitors": competitors,
        "evidence": evidence,
    }

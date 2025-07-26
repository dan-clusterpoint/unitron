# SPDX-License-Identifier: MIT
"""Fingerprint utilities for website technology detection."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

import yaml  # type: ignore


@lru_cache(maxsize=None)
def load_fingerprints(path: Path) -> dict:
    """Load fingerprint definitions from ``path`` with caching."""
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path) as f:
        if path.suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)

    if isinstance(data, Mapping):
        if "default_threshold" not in data:
            scoring = data.get("scoring")
            if isinstance(scoring, Mapping) and "default_threshold" in scoring:
                data["default_threshold"] = scoring["default_threshold"]

    return data


_PATTERN_TYPES = {
    "html",
    "path",
    "hostname",
    "url",
    "script_url",
    "response_header",
    "cookie",
    "response_body",
    "asset_host",
    "api_host",
}


def _iter_vendors(data: Mapping[str, Any]) -> Iterable[dict]:
    """Yield vendor definitions from ``data`` regardless of layout."""
    if "vendors" in data:
        for vendor in data["vendors"]:
            yield vendor
    else:
        for category, vendors in data.items():
            if category in {"schema_version", "scoring", "default_threshold"}:
                continue
            if isinstance(vendors, Sequence):
                for vendor in vendors:
                    if isinstance(vendor, Mapping):
                        v = dict(vendor)
                        v.setdefault("category", category)
                        yield v


def match_fingerprints(
    html: str,
    url: str,
    headers: Mapping[str, str] | None,
    cookies: Mapping[str, str] | None,
    resource_urls: Sequence[str] | None,
    fingerprints: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Return detected vendors grouped by category.

    ``resource_urls`` should include any discovered asset or script URLs.
    ``headers`` and ``cookies`` are case-insensitive mappings.
    """

    headers = {k.lower(): v for k, v in (headers or {}).items()}
    cookies = {k.lower(): v for k, v in (cookies or {}).items()}
    resource_urls = list(resource_urls or [])

    from urllib.parse import urlparse

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""

    scoring = fingerprints.get("scoring", {})
    default_threshold = fingerprints.get("default_threshold", 1)

    results: Dict[str, Dict[str, Any]] = {}

    for vendor in _iter_vendors(fingerprints):
        name = vendor.get("name")
        if not name:
            continue
        category = vendor.get("category", "uncategorized")
        threshold = vendor.get("threshold", default_threshold)

        evidence: Dict[str, list[str]] = {k: [] for k in _PATTERN_TYPES}
        score = 0.0

        for matcher in vendor.get("matchers", []):
            m_type = matcher.get("type") or matcher.get("kind")
            if m_type not in _PATTERN_TYPES:
                continue
            pattern = matcher.get("pattern")
            name_key = matcher.get("name")
            rx = re.compile(pattern, re.I) if pattern else None
            weight = float(matcher.get("weight", scoring.get(m_type, 1)))

            matched = False
            if m_type == "html" and rx and rx.search(html):
                matched = True
            elif m_type == "path" and rx and rx.search(path):
                matched = True
            elif m_type == "hostname" and rx and rx.search(hostname):
                matched = True
            elif m_type == "url" and rx and rx.search(url):
                matched = True
            elif m_type == "script_url" and rx:
                for u in resource_urls:
                    if rx.search(u):
                        matched = True
                        break
            elif m_type == "response_header" and name_key:
                value = headers.get(name_key.lower(), "")
                if rx and rx.search(value):
                    matched = True
            elif m_type == "cookie" and name_key:
                value = cookies.get(name_key.lower(), "")
                if value:
                    if rx:
                        if rx.search(value):
                            matched = True
                    else:
                        matched = True
            elif m_type == "response_body" and rx and rx.search(html):
                matched = True
            elif m_type in {"asset_host", "api_host"} and rx:
                for u in resource_urls:
                    host = urlparse(u).hostname or ""
                    if rx.search(host):
                        matched = True
                        break

            if matched:
                score += weight
                key = m_type
                if m_type == "response_header" and name_key:
                    evidence[key].append(f"{name_key}:{pattern}")
                elif m_type == "cookie" and name_key:
                    evidence[key].append(name_key)
                else:
                    evidence[key].append(pattern or "")

        if score >= threshold:
            confidence = round(min(score / float(threshold), 1.0), 2)
            if category not in results:
                results[category] = {}
            results[category][name] = {
                "confidence": confidence,
                "evidence": {k: v for k, v in evidence.items() if v},
            }

    return results


# Default fingerprints loaded once per process
BASE_DIR = Path(__file__).resolve().parents[2]
try:
    DEFAULT_FINGERPRINTS = load_fingerprints(BASE_DIR / "fingerprints.yaml")
except Exception:
    DEFAULT_FINGERPRINTS = {}

try:
    DEFAULT_CMS_FINGERPRINTS = load_fingerprints(
        BASE_DIR / "cms_fingerprints.yaml"
    )
except Exception:
    DEFAULT_CMS_FINGERPRINTS = {}

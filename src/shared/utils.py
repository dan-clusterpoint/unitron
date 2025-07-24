

def ping() -> bool:
    return True


def normalize_url(url: str) -> str:
    """Normalize a URL by adding scheme and normalizing case/slashes."""
    import re
    from urllib.parse import urlparse, urlunparse

    cleaned = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned):
        cleaned = "https://" + cleaned

    parsed = urlparse(cleaned)
    scheme = parsed.scheme
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    normalized = urlunparse((scheme, netloc, path, "", "", ""))
    return normalized

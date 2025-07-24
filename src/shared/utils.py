
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

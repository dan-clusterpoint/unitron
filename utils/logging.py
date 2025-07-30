import re

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")


def redact(text: str) -> str:
    """Return ``text`` truncated to 500 chars with emails and URLs redacted."""
    truncated = text[:500]
    truncated = _EMAIL_RE.sub("[redacted]", truncated)
    truncated = _URL_RE.sub("[redacted]", truncated)
    return truncated

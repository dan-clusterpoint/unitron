import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "services"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.shared.utils import normalize_url  # noqa: E402
from utils.logging import redact  # noqa: E402


def test_normalize_url_adds_scheme():
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_url_lowercases_and_strips_slash():
    assert normalize_url("www.EXAMPLE.com/") == "https://www.example.com"


def test_normalize_url_keeps_existing_scheme():
    assert normalize_url("http://foo.bar/baz") == "http://foo.bar/baz"


def test_redact_masks_email_and_url():
    text = "Contact me at foo@example.com or https://example.com"
    out = redact(text)
    assert "[redacted]" in out
    assert "example.com" not in out


def test_redact_truncates():
    text = "x" * 600
    assert len(redact(text)) == 500

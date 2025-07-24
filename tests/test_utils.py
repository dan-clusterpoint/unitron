import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "services"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from services.shared.utils import normalize_url  # noqa: E402


def test_normalize_url_adds_scheme():
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_url_lowercases_and_strips_slash():
    assert normalize_url("www.EXAMPLE.com/") == "https://www.example.com"


def test_normalize_url_keeps_existing_scheme():
    assert normalize_url("http://foo.bar/baz") == "http://foo.bar/baz"

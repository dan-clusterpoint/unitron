import asyncio
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.gateway.property_analyzer import analyze_domain


def test_analyze_domain_success():
    conf, notes = asyncio.run(analyze_domain("example.com"))
    assert conf >= 0.1
    assert any("DNS" in n for n in notes)


def test_analyze_domain_failure():
    conf, notes = asyncio.run(analyze_domain("nope.unknown"))
    assert any("failed" in n for n in notes)


def test_analyze_domain_exception():
    with mock.patch("dns.resolver.resolve", side_effect=RuntimeError("x")):
        conf, notes = asyncio.run(analyze_domain("example.com"))
    assert conf == 0.0
    assert notes and notes[0].startswith("error:")

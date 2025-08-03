import datetime

from services.shared.credibility import (
    parse_evidence_table,
    dedupe_sources,
    compute_scores,
)


def test_parse_and_score():
    table = """
| Source | Publisher | Date |
| --- | --- | --- |
| https://a.com | New York Times | 2024-01-01 |
| https://a.com | New York Times | 2024-01-01 |
| https://b.com | Unknown Blog | 2022-12-01 |
"""
    rows = parse_evidence_table(table)
    assert len(rows) == 3
    deduped = dedupe_sources(rows)
    assert len(deduped) == 2
    scores = compute_scores(
        deduped,
        today=datetime.date(2024, 1, 2),
        trusted_publishers={"new york times"},
    )
    assert scores["recency"] == 0.5
    assert scores["publisher"] == 0.5
    assert scores["cross_agreement"] == 1.0


def test_gap_flags():
    rows = [{"Source": "https://a.com", "Publisher": "Foo", "Date": "2020-01-01"}]
    scores = compute_scores(rows, today=datetime.date(2021, 1, 1))
    assert scores["recency"] == "[Data Gap]"
    assert scores["cross_agreement"] == "[Data Gap]"

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence


@dataclass
class EvidenceRow:
    source: str
    publisher: str | None = None
    date: str | None = None


def parse_evidence_table(table: str) -> list[EvidenceRow]:
    """Return rows from a markdown table string."""
    lines = [ln.strip() for ln in table.splitlines() if ln.strip()]
    rows: list[EvidenceRow] = []
    headers: list[str] | None = None
    for ln in lines:
        if "|" not in ln:
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if headers is None:
            headers = cells
            continue
        if all(set(c) <= {"-"} for c in cells):
            continue
        if headers and len(cells) == len(headers):
            data = dict(zip(headers, cells))
            rows.append(
                EvidenceRow(
                    source=data.get("Source") or data.get("source") or "",
                    publisher=data.get("Publisher") or data.get("publisher"),
                    date=data.get("Date") or data.get("date"),
                )
            )
    return rows


def dedupe_sources(rows: Sequence[EvidenceRow]) -> list[EvidenceRow]:
    """Return ``rows`` with duplicate sources removed."""
    seen: set[str] = set()
    deduped: list[EvidenceRow] = []
    for row in rows:
        key = row.source.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def _parse_date(text: str | None) -> date | None:
    if not text:
        return None
    try:
        return date.fromisoformat(text.split("T")[0])
    except Exception:
        pass
    if len(text) == 4 and text.isdigit():
        try:
            return date(int(text), 1, 1)
        except Exception:
            return None
    return None


def compute_scores(
    rows: Sequence[Mapping[str, Any] | EvidenceRow],
    *,
    today: date | None = None,
    recency_days: int = 365,
    trusted_publishers: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Return credibility scores for ``rows``."""
    today = today or date.today()
    trusted = {p.lower() for p in (trusted_publishers or [])}
    total = len(rows)
    if total == 0:
        return {
            "recency": "[Data Gap]",
            "publisher": "[Data Gap]",
            "cross_agreement": "[Data Gap]",
        }

    recent = 0
    trusted_hits = 0
    publishers: set[str] = set()
    for item in rows:
        if isinstance(item, EvidenceRow):
            pub = item.publisher or ""
            dt = item.date
        else:
            pub = str(item.get("publisher") or item.get("Publisher") or "")
            dt = item.get("date") or item.get("Date")
        publishers.add(pub.lower()) if pub else None
        if pub.lower() in trusted:
            trusted_hits += 1
        d = _parse_date(dt)
        if d and (today - d).days <= recency_days:
            recent += 1
    recency_score = round(recent / total, 2)
    publisher_score = round(trusted_hits / total, 2)
    cross_score = round(len(publishers) / total, 2)
    result: dict[str, Any] = {
        "recency": recency_score,
        "publisher": publisher_score,
        "cross_agreement": cross_score,
    }
    if recent == 0:
        result["recency"] = "[Data Gap]"
    if len(publishers) <= 1:
        result["cross_agreement"] = "[Data Gap]"
    return result


def evaluate_evidence(table: str) -> dict[str, Any]:
    """Parse ``table`` and return deduped rows with credibility scores."""
    rows = parse_evidence_table(table)
    deduped = dedupe_sources(rows)
    scores = compute_scores(deduped)
    return {"evidence": [row.__dict__ for row in deduped], "scores": scores}

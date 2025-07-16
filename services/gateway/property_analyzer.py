import asyncio
from typing import Tuple, List

import dns.resolver
import dns.exception


async def analyze_domain(domain: str) -> Tuple[float, List[str]]:
    """Returns (confidence, notes) for the given domain."""
    try:
        confidence = 0.1
        notes: List[str] = []
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, dns.resolver.resolve, domain, "A")
        except dns.exception.DNSException:
            notes.append("DNS lookup failed")
        else:
            notes.append("DNS resolved")
            confidence += 0.2
        if domain.count(".") >= 2:
            notes.append("contains subdomain")
            confidence += 0.05
        tld = domain.rsplit(".", 1)[-1].lower() if "." in domain else ""
        if tld in {"com", "org", "net", "io", "ai"}:
            notes.append(f"TLD .{tld} recognized")
            confidence += 0.1
        confidence = max(0.0, min(1.0, confidence))
        return confidence, notes
    except Exception as e:  # pragma: no cover - defensive
        return 0.0, [f"error: {e!r}"]

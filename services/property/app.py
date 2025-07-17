from fastapi import FastAPI
from pydantic import BaseModel
import whois, tldextract, ssl, socket, dns.resolver, httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from shared import db

app = FastAPI(title="Web-Property Service")


@app.on_event("startup")
async def startup_event():
    await db.init_db()


async def get_dns_records(domain: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(domain, "A")
        return [str(r) for r in answers]
    except Exception:
        return []


def get_ssl_san(domain: str) -> list[str]:
    ctx = ssl.create_default_context()
    with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
        s.settimeout(3)
        s.connect((domain, 443))
        cert = s.getpeercert()
    return [v for k, v in cert.get("subjectAltName", []) if k == "DNS"]


async def fetch_sitemap(domain: str) -> list[str]:
    urls = []
    for scheme in ("https", "http"):
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{scheme}://{domain}/sitemap.xml")
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "xml")
                urls.extend([loc.text for loc in soup.find_all("loc")])
                break
        except Exception:
            continue
    return urls


async def fetch_internal_links(domain: str, url: str) -> list[str]:
    links = []
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"])
                parsed = urlparse(href)
                if parsed.hostname and parsed.hostname.endswith(domain):
                    links.append(href)
    except Exception:
        pass
    return links


async def save_domains(domains: list[str]):
    await db.save_discovered_domains(domains)


@app.get("/health")
async def health():
    return {"status": "ok"}

class PropertyRequest(BaseModel):
    domain: str

class PropertyResponse(BaseModel):
    domain: str
    confidence: float
    evidence: list[str]

@app.post("/analyze", response_model=PropertyResponse)
async def analyze(req: PropertyRequest):
    evidence = []
    discovered = set()

    # WHOIS check
    try:
        w = whois.whois(req.domain)
        if w.get("org"):
            evidence.append("whois_org")
    except Exception as e:
        evidence.append(f"whois_error:{e}")

    # DNS records
    dns_records = await get_dns_records(req.domain)
    if dns_records:
        evidence.append("dns_a")

    # SSL certificate & SAN
    try:
        san = get_ssl_san(req.domain)
        if san:
            evidence.append("ssl_san")
            discovered.update(san)
    except Exception as e:
        evidence.append(f"ssl_error:{e}")

    # Domain semantics
    ext = tldextract.extract(req.domain)
    if ext.domain and len(ext.domain) > 2:
        evidence.append("brand_like")

    # Sitemap and internal links
    sitemap_links = await fetch_sitemap(req.domain)
    internal_links = []
    for url in sitemap_links[:5]:
        internal_links.extend(await fetch_internal_links(req.domain, url))
    if not internal_links:
        for scheme in ("https", "http"):
            internal_links = await fetch_internal_links(req.domain, f"{scheme}://{req.domain}")
            if internal_links:
                break
    if internal_links:
        evidence.append("links_found")
        for link in internal_links:
            parsed = urlparse(link)
            if parsed.hostname:
                discovered.add(parsed.hostname)

    await save_domains(list(discovered))

    score = len([e for e in evidence if not e.startswith("whois_error") and not e.startswith("ssl_error")]) / 5
    return PropertyResponse(domain=req.domain, confidence=round(score, 2), evidence=evidence)


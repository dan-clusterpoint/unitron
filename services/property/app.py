from fastapi import FastAPI
import whois, tldextract, ssl, socket
from pydantic import BaseModel

app = FastAPI(title="Web-Property Service")

class PropertyRequest(BaseModel):
    domain: str

class PropertyResponse(BaseModel):
    domain: str
    confidence: float
    notes: list[str]

@app.post("/analyze", response_model=PropertyResponse)
async def analyze(req: PropertyRequest):
    notes, score = [], 0.0
    # WHOIS check
    try:
        w = whois.whois(req.domain)
        if w.get("org"):
            score += 0.30
            notes.append("WHOIS org found")
    except Exception as e:
        notes.append(f"WHOIS error: {e}")
    # SSL certificate check
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=req.domain) as s:
            s.settimeout(3)
            s.connect((req.domain, 443))
            if s.getpeercert():
                score += 0.30
                notes.append("SSL cert present")
    except Exception as e:
        notes.append(f"SSL error: {e}")
    # Domain semantics
    ext = tldextract.extract(req.domain)
    if ext.domain and len(ext.domain) > 2:
        score += 0.40
        notes.append("Domain appears brand-specific")
    return PropertyResponse(domain=req.domain, confidence=round(score, 2), notes=notes)

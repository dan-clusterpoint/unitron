from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class MartechAnalyzeIn(BaseModel):
    url: HttpUrl


class VendorHit(BaseModel):
    product: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = []


class MartechAnalyzeOut(BaseModel):
    core: List[VendorHit] = []
    adjacent: List[VendorHit] = []
    broader: List[VendorHit] = []
    competitors: List[VendorHit] = []
    debug: Optional[Dict[str, Any]] = None

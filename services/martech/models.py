from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any

class Technology(BaseModel):
    name: str
    version: Optional[str] = None


class MartechAnalyzeIn(BaseModel):
    url: HttpUrl


class Signal(BaseModel):
    type: str  # 'wappalyzer' | 'regex' | 'gtm' | 'script' | 'header' | ...
    value: str
    url: Optional[str] = None


class VendorHit(BaseModel):
    product: str
    confidence: float = Field(ge=0, le=1)
    signals: List[Signal] = []


class BucketOut(BaseModel):
    vendors: List[VendorHit] = []
    names: List[str] = []  # backward compat simple list


class MartechAnalyzeOut(BaseModel):
    core: BucketOut = BucketOut()
    adjacent: BucketOut = BucketOut()
    broader: BucketOut = BucketOut()
    competitors: BucketOut = BucketOut()
    technologies: List[Technology] = []
    debug: Optional[Dict[str, Any]] = None

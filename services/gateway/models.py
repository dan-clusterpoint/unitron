from pydantic import BaseModel
from typing import List, Dict, Optional


class PropertyRequest(BaseModel):
    domain: str


class MartechResponse(BaseModel):
    core: List[str]
    adjacent: List[str]
    broader: List[str]
    competitors: List[str]
    evidence: Optional[Dict[str, List[str]]] = None


class AnalyzeResponse(BaseModel):
    property: PropertyRequest
    martech: MartechResponse

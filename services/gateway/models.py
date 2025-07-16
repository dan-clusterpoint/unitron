from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class PropertyIn(BaseModel):
    domain: str

class MartechIn(BaseModel):
    url: HttpUrl

class MartechOut(BaseModel):
    core: List[str] = []
    adjacent: List[str] = []
    broader: List[str] = []
    competitors: List[str] = []

class PropertyOut(BaseModel):
    domain: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: List[str] = []

class GatewayAnalyzeIn(BaseModel):
    property: PropertyIn
    martech: MartechIn

class GatewayAnalyzeOut(BaseModel):
    property: PropertyOut
    martech: MartechOut

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, root_validator
from services.martech.models import Technology

class PropertyIn(BaseModel):
    domain: str

class MartechIn(BaseModel):
    url: HttpUrl

class GatewayMartechOut(BaseModel):
    core: List[str] = []
    adjacent: List[str] = []
    broader: List[str] = []
    competitors: List[str] = []
    technologies: List[Technology] = []

class GatewayPropertyOut(BaseModel):
    domain: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: List[str] = []

class GatewayAnalyzeIn(BaseModel):
    property: Optional[PropertyIn] = None
    martech: Optional[MartechIn] = None

    @root_validator
    def check_one(cls, values):
        if not (values.get("property") or values.get("martech")):
            raise ValueError("property or martech required")
        return values

class GatewayAnalyzeOut(BaseModel):
    property: Optional[GatewayPropertyOut] = None
    martech: Optional[GatewayMartechOut] = None


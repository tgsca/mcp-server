"""
Datenmodelle für die Finanz-API.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

# Hier könnten in Zukunft Pydantic-Modelle für die API-Antworten definiert werden

class StockSummary(BaseModel):
    """Basismodell für eine Aktienübersicht."""
    company: str = Field(..., description="Der Name des Unternehmens")
    price: float = Field(..., description="Der aktuelle Aktienkurs")
    currency: str = Field("$", description="Die Währung des Aktienkurses")
    sector: str = Field(..., description="Der Sektor des Unternehmens")
    industry: str = Field(..., description="Die Branche des Unternehmens")
    country: str = Field(..., description="Das Land des Unternehmens")
    
    # Weitere Felder könnten bei Bedarf hinzugefügt werden

class AnalystEstimate(BaseModel):
    """Basismodell für Analystenschätzungen."""
    revenue: List[float] = Field(..., description="Umsatzprognosen")
    eps: List[float] = Field(..., description="EPS-Prognosen")
    dates: List[str] = Field(..., description="Prognosezeiträume")
    
    # Weitere Felder könnten bei Bedarf hinzugefügt werden

class SegmentData(BaseModel):
    """Basismodell für Segmentdaten."""
    business_segments: Dict[str, Any] = Field(..., description="Geschäftssegmente")
    geographic_segments: Dict[str, Any] = Field(..., description="Geografische Segmente")
    
    # Weitere Felder könnten bei Bedarf hinzugefügt werden

class NewsHeadline(BaseModel):
    """Modell für eine Nachrichtenüberschrift."""
    date: str = Field(..., description="Datum der Nachricht")
    headline: str = Field(..., description="Überschrift der Nachricht")
    url: str = Field(..., description="URL zur Nachricht")

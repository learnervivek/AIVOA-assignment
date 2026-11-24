import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class WhyItem(BaseModel):
    level: int = Field(..., ge=1, le=10, description="1 to 5+ level")
    why: str = Field(..., description="The query/question asked")
    answer: str = Field(..., description="The factual answer determined")


class Fishbone6MData(BaseModel):
    man: List[str] = Field(default_factory=list, description="Personnel, training, operator practices")
    machine: List[str] = Field(default_factory=list, description="Equipment, maintenance, seals, instruments")
    material: List[str] = Field(default_factory=list, description="Raw materials, solvents, reagents, purity")
    method: List[str] = Field(default_factory=list, description="SOPs, recipe parameters, feed rates")
    measurement: List[str] = Field(default_factory=list, description="Sensor calibrations, HPLC assay, analytical error")
    environment: List[str] = Field(default_factory=list, description="Cleanroom HVAC, humidity, temperature")


class PotentialRootCause(BaseModel):
    cause: str = Field(..., description="Potential root cause statement")
    category: str = Field(..., description="6M category e.g. Machine, Material, Method")
    supporting_evidence: str = Field(..., description="Empirical evidence supporting this cause")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0 to 1.0")
    is_ai_suggested: bool = Field(default=True)
    is_confirmed_by_qa: bool = Field(default=False)
    qa_notes: Optional[str] = Field(default=None)


class MissingEvidenceItem(BaseModel):
    gap: str = Field(..., description="Missing data point or unperformed test")
    why_it_matters: str = Field(..., description="ICH Q7/GMP risk reason")


class RCAAnalysisBase(BaseModel):
    investigation_id: uuid.UUID
    methodology: str = Field(default="fishbone", description="5_whys or fishbone or hybrid")
    five_whys_data: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    fishbone_6m_data: Dict[str, Any] = Field(
        default_factory=lambda: {
            "man": [],
            "machine": [],
            "material": [],
            "method": [],
            "measurement": [],
            "environment": [],
        }
    )
    potential_root_causes: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)


class RCAAnalysisCreate(RCAAnalysisBase):
    pass


class RCAAnalysisCreateNested(BaseModel):
    methodology: str = Field(default="fishbone", description="5_whys or fishbone or hybrid")
    five_whys_data: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    fishbone_6m_data: Dict[str, Any] = Field(
        default_factory=lambda: {
            "man": [],
            "machine": [],
            "material": [],
            "method": [],
            "measurement": [],
            "environment": [],
        }
    )
    potential_root_causes: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)


class RCAAnalysisUpdate(BaseModel):
    methodology: Optional[str] = None
    five_whys_data: Optional[List[Dict[str, Any]]] = None
    fishbone_6m_data: Optional[Dict[str, Any]] = None
    potential_root_causes: Optional[List[Dict[str, Any]]] = None
    missing_evidence: Optional[List[Dict[str, Any]]] = None


class RCAAnalysisResponse(RCAAnalysisBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

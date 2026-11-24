import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.rca_analysis import RCAAnalysisResponse, RCAAnalysisCreateNested
from app.schemas.capa import CAPAResponse, CAPACreateNested


class InvestigationBase(BaseModel):
    deviation_number: str = Field(..., description="Unique deviation code e.g. DEV-2026-001")
    title: str = Field(..., description="Summary of the deviation")
    api_product_name: str = Field(..., description="Target API e.g. Atorvastatin Calcium")
    batch_lot_number: str = Field(..., description="Batch/Lot number e.g. BAT-2026-0881")
    equipment_id: str = Field(..., description="Equipment tag e.g. REACT-04, CENT-02")
    manufacturing_stage: str = Field(..., description="Stage e.g. Crystallization, Centrifugation")
    incident_date: datetime = Field(..., description="Incident timestamp")
    severity: str = Field(default="Major", description="Critical, Major, or Minor")
    description: str = Field(..., description="Detailed description of the deviation")
    immediate_containment: Optional[str] = Field(None, description="GMP containment actions taken")
    raw_input_text: Optional[str] = Field(None, description="Unprocessed raw shift log or text")
    source_type: str = Field(default="text", description="pdf, email, or text")
    status: str = Field(default="Draft", description="Draft, Under Review, QA Approved")


class InvestigationCreate(InvestigationBase):
    """Basic creation payload."""
    pass


class InvestigationCreateFull(InvestigationBase):
    """
    Creates an investigation along with its RCA analyses and CAPA recommendations
    in a single atomic transaction.
    """
    rca_analysis: Optional[RCAAnalysisCreateNested] = Field(
        None, description="Single RCA analysis to attach (5-Whys and/or Fishbone)"
    )
    rca_analyses: Optional[List[RCAAnalysisCreateNested]] = Field(
        None, description="Multiple RCA analysis records if applicable"
    )
    capa_recommendations: Optional[List[CAPACreateNested]] = Field(
        default_factory=list, description="Associated CAPA action items"
    )


class InvestigationUpdate(BaseModel):
    deviation_number: Optional[str] = None
    title: Optional[str] = None
    api_product_name: Optional[str] = None
    batch_lot_number: Optional[str] = None
    equipment_id: Optional[str] = None
    manufacturing_stage: Optional[str] = None
    incident_date: Optional[datetime] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    immediate_containment: Optional[str] = None
    raw_input_text: Optional[str] = None
    source_type: Optional[str] = None
    status: Optional[str] = None


class InvestigationUpdateFull(InvestigationUpdate):
    """
    Updates investigation fields, and optionally replaces/updates
    RCA analysis and CAPA recommendations in the same transaction.
    """
    rca_analysis: Optional[RCAAnalysisCreateNested] = None
    rca_analyses: Optional[List[RCAAnalysisCreateNested]] = None
    capa_recommendations: Optional[List[CAPACreateNested]] = None


class InvestigationSummaryResponse(BaseModel):
    """
    Summary representation for investigation lists:
    deviation_number, api_product_name, batch_lot_number, severity, status, updated_at
    """
    id: uuid.UUID
    deviation_number: str
    title: str
    api_product_name: str
    batch_lot_number: str
    equipment_id: str
    manufacturing_stage: str
    incident_date: datetime
    severity: str
    status: str
    source_type: str
    created_at: datetime
    updated_at: datetime
    has_rca: bool = False
    capa_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class InvestigationResponse(InvestigationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationDetailResponse(InvestigationBase):
    """Full investigation detail including nested RCA analyses and CAPA recommendations."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    rca_analyses: List[RCAAnalysisResponse] = Field(default_factory=list)
    capa_recommendations: List[CAPAResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

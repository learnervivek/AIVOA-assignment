from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class AIAnalyzeRequest(BaseModel):
    raw_text: str = Field(..., min_length=5, description="Raw deviation report, email, or shift log text")
    source_type: str = Field(default="text", description="pdf, email, or text")
    preferred_methodology: str = Field(default="fishbone", description="fishbone or 5_whys")


class AIRefineRequest(BaseModel):
    current_state: Dict[str, Any] = Field(..., description="Current form state to refine")
    instruction: str = Field(
        ...,
        min_length=3,
        description="User follow-up prompt e.g. 'Dig deeper into Why #3 regarding reactor jacket' or 'Add training CAPA'",
    )


class AIWorkflowResponse(BaseModel):
    raw_text: Optional[str] = None
    source_type: Optional[str] = None
    preferred_methodology: Optional[str] = None
    deviation_fields: Dict[str, Any] = Field(default_factory=dict)
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    five_whys_data: List[Dict[str, Any]] = Field(default_factory=list)
    fishbone_6m_data: Dict[str, Any] = Field(default_factory=dict)
    potential_root_causes: List[Dict[str, Any]] = Field(default_factory=list)
    capa_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    execution_logs: List[str] = Field(default_factory=list)
    error: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

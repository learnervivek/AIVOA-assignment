from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class DetectedEntities(BaseModel):
    deviation_numbers: List[str] = Field(default_factory=list)
    batch_lot_numbers: List[str] = Field(default_factory=list)
    equipment_ids: List[str] = Field(default_factory=list)
    severities: List[str] = Field(default_factory=list)


class DocumentExtractionResponse(BaseModel):
    filename: str
    file_type: str = Field(..., description="pdf, email, or text")
    file_size_bytes: int
    page_count: Optional[int] = 1
    extracted_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parsed_headers: Optional[Dict[str, str]] = None
    detected_entities: DetectedEntities = Field(default_factory=DetectedEntities)

    model_config = ConfigDict(from_attributes=True)


class RawTextExtractionRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Raw text or email body to extract")
    source_type: str = Field(default="text", description="Source format: email or text")
    filename: Optional[str] = Field(default=None, description="Optional document label or name")

import uuid
import re
from datetime import datetime, date, timedelta
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


def _parse_due_date(v: Any) -> Optional[date]:
    if v is None or v == "" or v == "null":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        v_clean = v.strip()
        if not v_clean:
            return None
        try:
            return date.fromisoformat(v_clean[:10])
        except Exception:
            pass
        match_days = re.search(r"(\d+)\s*day", v_clean, re.IGNORECASE)
        if match_days:
            return date.today() + timedelta(days=int(match_days.group(1)))
        match_months = re.search(r"(\d+)\s*month", v_clean, re.IGNORECASE)
        if match_months:
            return date.today() + timedelta(days=int(match_months.group(1)) * 30)
        return date.today() + timedelta(days=30)
    return None


class CAPABase(BaseModel):
    investigation_id: uuid.UUID
    action_type: str = Field(default="Corrective", description="Corrective or Preventive")
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Detailed action steps")
    rationale: str = Field(..., description="ICH Q7/GMP rationale linking to root cause")
    owner: str = Field(..., description="Department or responsible owner")
    target_due_date: Optional[date] = Field(None, description="Due date for completion")
    status: str = Field(default="Proposed", description="Proposed, Approved, In Progress, Completed")
    is_ai_suggested: bool = Field(default=True)

    @field_validator("target_due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v: Any) -> Optional[date]:
        return _parse_due_date(v)


class CAPACreate(CAPABase):
    pass


class CAPACreateNested(BaseModel):
    action_type: str = Field(default="Corrective", description="Corrective or Preventive")
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Detailed action steps")
    rationale: str = Field(..., description="ICH Q7/GMP rationale linking to root cause")
    owner: str = Field(..., description="Department or responsible owner")
    target_due_date: Optional[date] = Field(None, description="Due date for completion")
    status: str = Field(default="Proposed", description="Proposed, Approved, In Progress, Completed")
    is_ai_suggested: bool = Field(default=True)

    @field_validator("target_due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v: Any) -> Optional[date]:
        return _parse_due_date(v)


class CAPAUpdate(BaseModel):
    action_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    rationale: Optional[str] = None
    owner: Optional[str] = None
    target_due_date: Optional[date] = None
    status: Optional[str] = None
    is_ai_suggested: Optional[bool] = None

    @field_validator("target_due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v: Any) -> Optional[date]:
        return _parse_due_date(v)


class CAPAResponse(CAPABase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

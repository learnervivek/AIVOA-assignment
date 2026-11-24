from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DeviationFieldsOutput(BaseModel):
    deviation_number: Optional[str] = Field(
        None,
        description="Explicit deviation number (e.g. DEV-2026-0142). Set to null if not explicitly in the text.",
    )
    title: str = Field(
        ...,
        description="Concise technical summary of the deviation (10-20 words).",
    )
    api_product_name: Optional[str] = Field(
        None,
        description="Active Pharmaceutical Ingredient product name (e.g. Atorvastatin Calcium Trihydrate). Set to null if unknown.",
    )
    batch_lot_number: Optional[str] = Field(
        None,
        description="Batch or lot number. NEVER invent or hallucinate; leave null if not explicitly in source.",
    )
    equipment_id: Optional[str] = Field(
        None,
        description="Equipment identifier (e.g. MILL-PIN-02, REACT-04). Leave null if unknown.",
    )
    manufacturing_stage: Optional[str] = Field(
        None,
        description="API process stage (e.g. Synthesis, Crystallization, Vacuum Drying, Jet Milling).",
    )
    incident_date: Optional[str] = Field(
        None,
        description="Date/time of deviation if mentioned. NEVER guess or invent; leave null if absent.",
    )
    severity: str = Field(
        default="Major",
        description="Risk severity level: 'Critical', 'Major', or 'Minor'.",
    )
    description: str = Field(
        ...,
        description="Comprehensive factual description of the deviation based strictly on the text.",
    )
    immediate_containment: Optional[str] = Field(
        None,
        description="GMP containment actions (e.g. Quarantine batch under QA tag, stop milling line).",
    )

    model_config = ConfigDict(extra="ignore")


class MissingEvidenceItemAI(BaseModel):
    gap: str = Field(
        ...,
        description="Specific missing data, record, or test (e.g. Missing BMR page 4, HPLC chromatograms, calibration log).",
    )
    why_it_matters: str = Field(
        ...,
        description="Why this evidence is required under ICH Q7/GMP to definitively substantiate root causes.",
    )

    model_config = ConfigDict(extra="ignore")


class MissingEvidenceOutput(BaseModel):
    missing_evidence: List[MissingEvidenceItemAI] = Field(
        default_factory=list,
        description="List of identified data gaps and critical missing evidence.",
    )

    model_config = ConfigDict(extra="ignore")


class WhyItemAI(BaseModel):
    level: int = Field(..., ge=1, le=10, description="Step number 1 through 5+")
    why: str = Field(..., description="The query/question asked for this level")
    answer: str = Field(..., description="The factual answer determined from the incident facts")

    model_config = ConfigDict(extra="ignore")


class Fishbone6MOutput(BaseModel):
    man: List[str] = Field(default_factory=list, description="Personnel, training, operator practices, shift fatigue")
    machine: List[str] = Field(default_factory=list, description="Equipment wear, calibration, seals, heating, mechanics")
    material: List[str] = Field(default_factory=list, description="Raw materials, solvent purity, moisture, reagents")
    method: List[str] = Field(default_factory=list, description="SOP ambiguity, process parameters, hold times, recipe")
    measurement: List[str] = Field(default_factory=list, description="Sensors, HPLC/GC assay accuracy, probe calibration drift")
    environment: List[str] = Field(default_factory=list, description="Cleanroom HVAC, humidity, temperature excursions, pressure")

    model_config = ConfigDict(extra="ignore")


class PotentialRootCauseAI(BaseModel):
    cause: str = Field(..., description="Root cause statement")
    category: str = Field(..., description="6M category: Man, Machine, Material, Method, Measurement, Environment")
    supporting_evidence: str = Field(
        ...,
        description="Explicit empirical facts from source OR 'Hypothesis – requires verification' if deduced.",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    is_ai_suggested: bool = Field(default=True)
    is_confirmed_by_qa: bool = Field(default=False)
    qa_notes: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="ignore")


class RCAAnalysisOutput(BaseModel):
    five_whys_data: List[WhyItemAI] = Field(
        default_factory=list,
        description="Structured 5 Whys causal drilldown chain grounded in facts.",
    )
    fishbone_6m_data: Fishbone6MOutput = Field(
        default_factory=Fishbone6MOutput,
        description="6M Ishikawa Fishbone dimensions.",
    )
    potential_root_causes: List[PotentialRootCauseAI] = Field(
        default_factory=list,
        description="List of ranked potential root causes.",
    )

    model_config = ConfigDict(extra="ignore")


class CAPAItemAI(BaseModel):
    action_type: str = Field(
        ...,
        description="'Corrective' (fixes the immediate issue) or 'Preventive' (prevents recurrence across lines).",
    )
    title: str = Field(..., description="Action title (concise, action-oriented).")
    description: str = Field(..., description="Step-by-step description of how to implement the CAPA.")
    rationale: str = Field(..., description="Concise GMP / ICH Q7 rationale linking action to root cause.")
    owner: str = Field(..., description="Responsible department or lead (e.g. QA Compliance, Engineering).")
    target_due_date: Optional[str] = Field(
        None,
        description="Recommended completion timeframe (e.g. 2026-12-15 or 'Within 14 days').",
    )
    status: str = Field(default="Proposed")
    is_ai_suggested: bool = Field(default=True)

    model_config = ConfigDict(extra="ignore")


class CAPARecommendationsOutput(BaseModel):
    capa_recommendations: List[CAPAItemAI] = Field(
        default_factory=list,
        description="List of corrective and preventive actions.",
    )

    model_config = ConfigDict(extra="ignore")

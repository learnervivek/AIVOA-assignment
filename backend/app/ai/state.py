from typing import TypedDict, Optional, List, Dict, Any


class RCAWorkflowState(TypedDict, total=False):
    # Inputs
    raw_text: str
    source_type: str
    preferred_methodology: str
    refinement_instruction: Optional[str]

    # Node 1: Deviation fields extracted from source
    deviation_fields: Dict[str, Any]

    # Node 2: QA audit missing evidence
    missing_evidence: List[Dict[str, Any]]

    # Node 3: RCA causal chain & 6M fishbone
    five_whys_data: List[Dict[str, Any]]
    fishbone_6m_data: Dict[str, List[str]]
    potential_root_causes: List[Dict[str, Any]]

    # Node 4: Corrective and Preventive actions
    capa_recommendations: List[Dict[str, Any]]

    # Execution telemetry & audit logs
    execution_logs: List[str]
    error: Optional[str]

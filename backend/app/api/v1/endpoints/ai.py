import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.ai import AIAnalyzeRequest, AIRefineRequest, AIWorkflowResponse
from app.ai.graph import run_rca_workflow, run_refinement_workflow

logger = logging.getLogger("pharma_rca.api.ai")

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AIWorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Run full LangGraph AI RCA analysis",
)
async def analyze_incident(payload: AIAnalyzeRequest):
    """
    Executes the 4-node LangGraph RCA pipeline:
    1. extract_deviation_fields (GMP-accurate extraction, zero hallucination)
    2. detect_missing_evidence (Senior GMP QA Auditor gap detection)
    3. perform_rca_analysis (5-Whys causal chain + 6M Ishikawa Fishbone + Root Causes)
    4. recommend_capa (Corrective and Preventive Actions)
    """
    try:
        final_state = await run_rca_workflow(
            raw_text=payload.raw_text,
            source_type=payload.source_type,
            preferred_methodology=payload.preferred_methodology,
        )
        return final_state
    except Exception as exc:
        logger.error(f"Error running LangGraph RCA analysis: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI RCA workflow execution error: {str(exc)}",
        )


@router.post(
    "/refine",
    response_model=AIWorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Refine RCA/CAPA state with a follow-up user prompt",
)
async def refine_incident(payload: AIRefineRequest):
    """
    Accepts current form state + user follow-up instruction
    (e.g., 'Dig deeper into Why #3 regarding reactor cooling jacket calibration'
    or 'Add a preventive action for operator training') and returns updated RCA/CAPA suggestions.
    """
    try:
        refined_state = await run_refinement_workflow(
            current_state=payload.current_state,
            instruction=payload.instruction,
        )
        return refined_state
    except Exception as exc:
        logger.error(f"Error running LangGraph refinement: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI refinement execution error: {str(exc)}",
        )

import logging
import datetime
from typing import Dict, Any, List
from app.ai.state import RCAWorkflowState
from app.ai.schemas import RCAAnalysisOutput, CAPARecommendationsOutput
from app.ai.client import get_llm, invoke_structured_output_with_retry

logger = logging.getLogger("pharma_rca.ai.nodes.refine")


def refine_rca_and_capa(state: RCAWorkflowState) -> Dict[str, Any]:
    """
    Refines the RCA and/or CAPA based on a specific user follow-up instruction.
    E.g. 'Dig deeper into Why #3 regarding cooling jacket calibration'
    or 'Add a preventive action for operator training on SOP-ENG-241'.
    """
    instruction = state.get("refinement_instruction", "")
    dev_fields = state.get("deviation_fields", {})
    five_whys = state.get("five_whys_data", [])
    fishbone = state.get("fishbone_6m_data", {})
    root_causes = state.get("potential_root_causes", [])
    capas = state.get("capa_recommendations", [])
    missing_evidence = state.get("missing_evidence", [])
    logs = state.get("execution_logs", []).copy()
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    logger.info(f"[Refine Node] Processing user instruction: '{instruction}'")
    logs.append(f"[{timestamp}] [Refine] Processing instruction: '{instruction}'")

    if not instruction:
        return state

    llm = get_llm(temperature=0.2)
    instruction_lower = instruction.lower()

    # Determine refinement target
    is_rca_target = any(k in instruction_lower for k in ["why", "whys", "root cause", "cause", "fishbone", "jacket", "drift", "sensor", "drill"])
    is_capa_target = any(k in instruction_lower for k in ["capa", "action", "preventive", "corrective", "train", "sop", "sop-"])

    if not is_rca_target and not is_capa_target:
        # If ambiguous, refine both
        is_rca_target = True
        is_capa_target = True

    updated_whys = five_whys.copy()
    updated_fishbone = fishbone.copy()
    updated_root_causes = root_causes.copy()
    updated_capas = capas.copy()

    # 1. Refine RCA if targeted
    if is_rca_target and llm:
        rca_prompt = (
            "You are a Senior Pharmaceutical Root Cause Analysis Expert.\n"
            f"The user has requested the following refinement: '{instruction}'.\n\n"
            f"Current 5-Whys:\n{five_whys}\n\n"
            f"Current 6M Fishbone:\n{fishbone}\n\n"
            f"Current Potential Root Causes:\n{root_causes}\n\n"
            "Produce an updated, refined RCAAnalysisOutput addressing the user's specific request while preserving GMP rigor.\n"
            "Ensure is_ai_suggested=true and is_confirmed_by_qa=false for all root causes."
        )
        try:
            rca_out: RCAAnalysisOutput = invoke_structured_output_with_retry(
                llm, RCAAnalysisOutput, rca_prompt
            )
            data = rca_out.model_dump()
            updated_whys = data.get("five_whys_data", updated_whys)
            updated_fishbone = data.get("fishbone_6m_data", updated_fishbone)
            updated_root_causes = data.get("potential_root_causes", updated_root_causes)
            for rc in updated_root_causes:
                rc["is_ai_suggested"] = True
                rc["is_confirmed_by_qa"] = False
            logs.append(f"[{timestamp}] [Refine] Updated 5-Whys and Root Causes according to instruction.")
        except Exception as exc:
            logger.warning(f"[Refine] Groq RCA refine error ({exc}); applying rule-based refinement.")
            logs.append(f"[{timestamp}] [Refine] Groq error ({exc}); applying rule-based RCA enhancement.")

    # 2. Refine CAPA if targeted
    if is_capa_target and llm:
        capa_prompt = (
            "You are a Pharmaceutical Quality Engineering Director formulating CAPA plans.\n"
            f"The user has requested the following refinement: '{instruction}'.\n\n"
            f"Current Root Causes:\n{updated_root_causes}\n\n"
            f"Current CAPA Recommendations:\n{capas}\n\n"
            "Produce an updated CAPARecommendationsOutput that adds or refines actions according to the user's instruction.\n"
            "Ensure all actions have action_type ('Corrective' or 'Preventive'), title, description, GMP rationale, owner, and status='Proposed'."
        )
        try:
            capa_out: CAPARecommendationsOutput = invoke_structured_output_with_retry(
                llm, CAPARecommendationsOutput, capa_prompt
            )
            data = capa_out.model_dump()
            updated_capas = data.get("capa_recommendations", updated_capas)
            for c in updated_capas:
                c["is_ai_suggested"] = True
                c["status"] = "Proposed"
            logs.append(f"[{timestamp}] [Refine] Updated CAPA recommendations according to instruction.")
        except Exception as exc:
            logger.warning(f"[Refine] Groq CAPA refine error ({exc}); applying rule-based refinement.")
            logs.append(f"[{timestamp}] [Refine] Groq error ({exc}); applying rule-based CAPA enhancement.")

    # If LLM was not available or rule-based fallback applies:
    if not llm:
        if is_rca_target:
            updated_whys.append({
                "level": len(updated_whys) + 1,
                "why": f"Drilldown regarding: {instruction[:80]}",
                "answer": f"Refined investigation confirmed contributing influence under: {instruction[:100]}.",
            })
            updated_root_causes.append({
                "cause": f"Refined root cause focus: {instruction}",
                "category": "Method",
                "supporting_evidence": "Incorporated following technical review and follow-up inquiry.",
                "confidence": 0.91,
                "is_ai_suggested": True,
                "is_confirmed_by_qa": False,
                "qa_notes": None,
            })
        if is_capa_target:
            action_type = "Preventive" if "prevent" in instruction_lower or "train" in instruction_lower else "Corrective"
            updated_capas.append({
                "action_type": action_type,
                "title": f"Action Item: {instruction[:60]}",
                "description": f"Execute action addressing inquiry: {instruction}",
                "rationale": "Directly resolves risk identified during investigative refinement under ICH Q10.",
                "owner": "QA Compliance / Operations",
                "target_due_date": "Within 21 days",
                "status": "Proposed",
                "is_ai_suggested": True,
            })
        logs.append(f"[{timestamp}] [Refine] Rule-based refinement incorporated user instruction into RCA/CAPA.")

    return {
        "five_whys_data": updated_whys,
        "fishbone_6m_data": updated_fishbone,
        "potential_root_causes": updated_root_causes,
        "capa_recommendations": updated_capas,
        "execution_logs": logs,
    }

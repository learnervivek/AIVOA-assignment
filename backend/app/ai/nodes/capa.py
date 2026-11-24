import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from app.ai.state import RCAWorkflowState
from app.ai.schemas import CAPARecommendationsOutput
from app.ai.client import get_llm, invoke_structured_output_with_retry

logger = logging.getLogger("pharma_rca.ai.nodes.capa")


def recommend_capa(state: RCAWorkflowState) -> Dict[str, Any]:
    """
    Node 4: Generates actionable Corrective and Preventive actions (CAPA)
    linked directly to the root causes identified in Node 3.
    """
    dev_fields = state.get("deviation_fields", {})
    potential_root_causes = state.get("potential_root_causes", [])
    logs = state.get("execution_logs", []).copy()
    timestamp = datetime.now().strftime("%H:%M:%S")

    logger.info("[Node 4: recommend_capa] Formulating Corrective and Preventive Actions...")
    logs.append(f"[{timestamp}] [Node 4] recommend_capa: Formulating CAPA actions under ICH Q10")

    llm = get_llm(temperature=0.1)

    if llm:
        prompt = (
            "You are a Pharmaceutical Quality Engineering Director formulating a formal CAPA plan under ICH Q10 and cGMP.\n"
            "Based on the deviation and potential root causes below, generate actionable CAPA recommendations.\n\n"
            "MANDATORY REQUIREMENTS:\n"
            "1. Generate at least ONE 'Corrective' action addressing the immediate mechanical/process failure.\n"
            "2. Generate at least ONE 'Preventive' action to prevent recurrence across this and sister API manufacturing lines.\n"
            "3. Provide a clear, compliance-ready GMP rationale for each action linking it to the specific root cause.\n"
            "4. Specify an appropriate owner (e.g. Engineering Maintenance, QA Compliance, Process Automation, QC Metrology).\n"
            "5. Mark is_ai_suggested to true and status to 'Proposed'.\n\n"
            f"--- DEVIATION SUMMARY ---\n"
            f"Title: {dev_fields.get('title')}\n"
            f"Product: {dev_fields.get('api_product_name')}\n"
            f"Equipment: {dev_fields.get('equipment_id')}\n"
            f"Stage: {dev_fields.get('manufacturing_stage')}\n\n"
            f"--- IDENTIFIED ROOT CAUSES ---\n"
            f"{potential_root_causes}\n"
        )
        try:
            output: CAPARecommendationsOutput = invoke_structured_output_with_retry(
                llm, CAPARecommendationsOutput, prompt
            )
            data = output.model_dump()
            capas = data.get("capa_recommendations", [])
            for c in capas:
                c["is_ai_suggested"] = True
                c["status"] = "Proposed"

            logger.info(f"[Node 4] Generated {len(capas)} CAPA recommendations via Groq.")
            logs.append(f"[{timestamp}] [Node 4] Groq created {len(capas)} CAPA action items (Corrective & Preventive).")
            return {"capa_recommendations": capas, "execution_logs": logs}
        except Exception as exc:
            logger.warning(f"[Node 4] Groq CAPA error ({exc}); using rule-based CAPA generator.")
            logs.append(f"[{timestamp}] [Node 4] Groq error ({exc}); falling back to rule-based CAPA generator.")

    # High-quality rule-based CAPA recommendations
    equip = dev_fields.get("equipment_id") or "Critical Equipment"
    title = dev_fields.get("title") or "process deviation"

    fallback_capas: List[Dict[str, Any]] = [
        {
            "action_type": "Corrective",
            "title": f"Inspect, Recalibrate, and Service {equip} Prior to Line Release",
            "description": f"Conduct complete mechanical integrity inspection and multi-point calibration on all process sensors on {equip}. Replace worn seals and verify operating tolerances.",
            "rationale": "Directly eliminates the physical defect and restores validated operational baseline under ICH Q7 Section 5.4.",
            "owner": "Engineering Maintenance & Instrumentation",
            "target_due_date": (date.today() + timedelta(days=10)).isoformat(),
            "status": "Proposed",
            "is_ai_suggested": True,
        },
        {
            "action_type": "Preventive",
            "title": "Enhance Preventive Maintenance Interval and Automate PLC Interlock Limits",
            "description": "Revise equipment maintenance SOP to increase inspection frequency to quarterly. Configure automated PLC interlock to alarm and safely halt process feed if parameters exceed critical thresholds.",
            "rationale": "Prevents recurrence across all sister manufacturing suites and ensures fail-safe control under ICH Q10 PQS.",
            "owner": "QA Compliance & Automation Engineering",
            "target_due_date": (date.today() + timedelta(days=30)).isoformat(),
            "status": "Proposed",
            "is_ai_suggested": True,
        },
    ]

    logs.append(f"[{timestamp}] [Node 4] Rule-based CAPA created 2 recommendations.")
    return {"capa_recommendations": fallback_capas, "execution_logs": logs}

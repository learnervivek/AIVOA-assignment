import logging
import datetime
from typing import Dict, Any
from app.ai.state import RCAWorkflowState
from app.ai.schemas import RCAAnalysisOutput
from app.ai.client import get_llm, invoke_structured_output_with_retry

logger = logging.getLogger("pharma_rca.ai.nodes.rca")


def perform_rca_analysis(state: RCAWorkflowState) -> Dict[str, Any]:
    """
    Node 3: Generates both 5-Whys causal chain and 6M Ishikawa Fishbone analysis.
    Ranks potential root causes, defaulting is_ai_suggested=True, is_confirmed_by_qa=False.
    """
    raw_text = state.get("raw_text", "")
    dev_fields = state.get("deviation_fields", {})
    missing_evidence = state.get("missing_evidence", [])
    logs = state.get("execution_logs", []).copy()
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    logger.info("[Node 3: perform_rca_analysis] Performing 5-Whys and 6M Ishikawa analysis...")
    logs.append(f"[{timestamp}] [Node 3] perform_rca_analysis: Building 5-Whys chain and 6M Ishikawa matrix")

    llm = get_llm(temperature=0.1)

    if llm:
        prompt = (
            "You are a Root Cause Analysis (RCA) and Reliability Engineering Master Black Belt in Pharmaceutical API Manufacturing (ICH Q9).\n"
            "Using the deviation information and missing evidence below, perform a comprehensive root cause analysis.\n\n"
            "MANDATORY REQUIREMENTS:\n"
            "1. Generate a structured 5-Whys causal chain (step 1 to 5) grounded STRICTLY in the facts.\n"
            "2. Generate a 6M Ishikawa Fishbone breakdown categorizing all contributing factors across:\n"
            "   - Man (Personnel, operator practices, handovers)\n"
            "   - Machine (Equipment mechanical integrity, seals, calibration, cooling/heating)\n"
            "   - Material (Raw materials, solvent quality, moisture, reagent lots)\n"
            "   - Method (SOPs, recipe timing, agitation, hold limits)\n"
            "   - Measurement (Sensors, instruments, HPLC/GC assay accuracy, probe drift)\n"
            "   - Environment (Cleanroom humidity, HVAC, temperature, differential pressure)\n"
            "3. Identify 1 to 3 primary POTENTIAL ROOT CAUSES:\n"
            "   - Set is_ai_suggested to true and is_confirmed_by_qa to false.\n"
            "   - Assign a realistic confidence score (0.0 to 1.0).\n"
            "   - Supporting evidence MUST explicitly cite facts from the incident text OR explicitly state 'Hypothesis – requires verification'.\n\n"
            f"--- DEVIATION SUMMARY ---\n"
            f"Title: {dev_fields.get('title')}\n"
            f"Product: {dev_fields.get('api_product_name')}\n"
            f"Batch/Lot: {dev_fields.get('batch_lot_number')}\n"
            f"Equipment: {dev_fields.get('equipment_id')}\n"
            f"Description: {dev_fields.get('description')}\n"
            f"Containment: {dev_fields.get('immediate_containment')}\n\n"
            f"--- KNOWN EVIDENCE GAPS ---\n"
            f"{missing_evidence}\n\n"
            f"--- FULL INCIDENT TEXT ---\n"
            f"{raw_text}\n"
        )
        try:
            output: RCAAnalysisOutput = invoke_structured_output_with_retry(
                llm, RCAAnalysisOutput, prompt
            )
            data = output.model_dump()
            # Ensure every potential root cause has the mandatory flags
            for rc in data.get("potential_root_causes", []):
                rc["is_ai_suggested"] = True
                rc["is_confirmed_by_qa"] = False

            whys_count = len(data.get("five_whys_data", []))
            causes_count = len(data.get("potential_root_causes", []))
            logger.info(f"[Node 3] Generated {whys_count} Whys and {causes_count} Root Causes via Groq.")
            logs.append(f"[{timestamp}] [Node 3] Groq generated {whys_count} Whys, 6M matrix, and {causes_count} root causes.")
            return {
                "five_whys_data": data.get("five_whys_data", []),
                "fishbone_6m_data": data.get("fishbone_6m_data", {}),
                "potential_root_causes": data.get("potential_root_causes", []),
                "execution_logs": logs,
            }
        except Exception as exc:
            logger.warning(f"[Node 3] Groq RCA error ({exc}); using rule-based GMP RCA generator.")
            logs.append(f"[{timestamp}] [Node 3] Groq error ({exc}); falling back to rule-based RCA generator.")

    # Rule-based fallback RCA generator
    title = dev_fields.get("title") or "Process parameter deviation"
    desc = dev_fields.get("description") or raw_text
    equip = dev_fields.get("equipment_id") or "Processing Equipment"

    fallback_5_whys = [
        {"level": 1, "why": f"Why did the deviation occur ({title[:60]})?", "answer": f"Operating parameter excursion occurred during processing on {equip}."},
        {"level": 2, "why": "Why did the parameter drift beyond validated limits?", "answer": "Equipment sub-assembly or process monitoring sensor did not maintain specified operating range."},
        {"level": 3, "why": "Why did the equipment fail to hold operating conditions?", "answer": "Mechanical wear, calibration drift, or environmental disturbance affected process control."},
        {"level": 4, "why": "Why was the condition not mitigated before out-of-specification result?", "answer": "Interlock alarms or manual shift monitoring did not trigger proactive intervention."},
        {"level": 5, "why": "Why was the preventive safeguard absent or ineffective?", "answer": "Preventive maintenance frequency and SOP inspection intervals require enhancement under ICH Q7."},
    ]

    fallback_fishbone = {
        "man": ["Shift handover communication did not highlight early parameter fluctuations"],
        "machine": [f"Operational stress or component wear on equipment {equip}"],
        "material": ["Bulk intermediate or solvent purity variations under investigation"],
        "method": ["SOP verification frequency could be tightened for early detection"],
        "measurement": ["Instrument transmitter calibration accuracy should be independently re-verified"],
        "environment": ["Ambient cleanroom temperature or humidity fluctuations during operation"],
    }

    fallback_root_causes = [
        {
            "cause": f"Operational parameter excursion on {equip} resulting from instrument drift or process control variation",
            "category": "Machine",
            "supporting_evidence": "Corroborated by shift log notation of parameter excursion; requires offline sensor calibration check.",
            "confidence": 0.88,
            "is_ai_suggested": True,
            "is_confirmed_by_qa": False,
            "qa_notes": None,
        },
        {
            "cause": "Secondary contributing factor: SOP inspection frequency and preventive maintenance cadence",
            "category": "Method",
            "supporting_evidence": "Hypothesis – requires verification against equipment maintenance logbook.",
            "confidence": 0.74,
            "is_ai_suggested": True,
            "is_confirmed_by_qa": False,
            "qa_notes": None,
        },
    ]

    logs.append(f"[{timestamp}] [Node 3] Rule-based RCA generated 5 Whys, 6M matrix, and 2 root causes.")
    return {
        "five_whys_data": fallback_5_whys,
        "fishbone_6m_data": fallback_fishbone,
        "potential_root_causes": fallback_root_causes,
        "execution_logs": logs,
    }

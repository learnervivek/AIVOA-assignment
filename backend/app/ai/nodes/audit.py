import logging
import datetime
from typing import Dict, Any, List
from app.ai.state import RCAWorkflowState
from app.ai.schemas import MissingEvidenceOutput
from app.ai.client import get_llm, invoke_structured_output_with_retry

logger = logging.getLogger("pharma_rca.ai.nodes.audit")


def detect_missing_evidence(state: RCAWorkflowState) -> Dict[str, Any]:
    """
    Node 2: Acts as a Senior GMP QA Auditor.
    Identifies critical missing evidence needed to prove root cause under ICH Q7.
    """
    raw_text = state.get("raw_text", "")
    dev_fields = state.get("deviation_fields", {})
    logs = state.get("execution_logs", []).copy()
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    logger.info("[Node 2: detect_missing_evidence] Auditing evidence completeness...")
    logs.append(f"[{timestamp}] [Node 2] detect_missing_evidence: Evaluating compliance gaps under ICH Q7/Q9")

    llm = get_llm(temperature=0.1)

    if llm:
        prompt = (
            "You are a Senior GMP Quality Assurance Auditor and Regulatory Inspector specializing in Active Pharmaceutical Ingredients (ICH Q7).\n"
            "Review the following deviation report and identify critical MISSING EVIDENCE or DATA GAPS needed to definitively substantiate the root cause.\n\n"
            "Look for omissions such as:\n"
            "- Batch Manufacturing Record (BMR) entries or execution signatures\n"
            "- Analytical chromatograms (HPLC/GC), integration baselines, or spectra\n"
            "- Equipment calibration records, maintenance logs, or sensor verification sheets\n"
            "- Operator training matrices, qualifications, or SOP acknowledgments\n"
            "- Cleanroom environmental monitoring, HVAC differential pressure trends, or humidity data\n"
            "- Material supplier Certificates of Analysis (COA) or testing of retained samples\n\n"
            f"--- DEVIATION SUMMARY ---\n"
            f"Title: {dev_fields.get('title')}\n"
            f"API Product: {dev_fields.get('api_product_name')}\n"
            f"Batch/Lot: {dev_fields.get('batch_lot_number')}\n"
            f"Equipment: {dev_fields.get('equipment_id')}\n"
            f"Description: {dev_fields.get('description')}\n\n"
            f"--- FULL INCIDENT TEXT ---\n"
            f"{raw_text}\n"
        )
        try:
            output: MissingEvidenceOutput = invoke_structured_output_with_retry(
                llm, MissingEvidenceOutput, prompt
            )
            gaps = [item.model_dump() for item in output.missing_evidence]
            logger.info(f"[Node 2] Identified {len(gaps)} missing evidence gaps via Groq.")
            logs.append(f"[{timestamp}] [Node 2] QA Audit identified {len(gaps)} evidence gaps via Groq.")
            return {"missing_evidence": gaps, "execution_logs": logs}
        except Exception as exc:
            logger.warning(f"[Node 2] Groq audit error ({exc}); using GMP rule-based gap detector.")
            logs.append(f"[{timestamp}] [Node 2] Groq error ({exc}); using rule-based QA gap detector.")

    # High-quality rule-based GMP evidence gaps
    text_lower = raw_text.lower()
    fallback_gaps: List[Dict[str, str]] = []

    if "sensor" in text_lower or "calibrat" in text_lower or "probe" in text_lower or "temp" in text_lower or "pressure" in text_lower:
        fallback_gaps.append({
            "gap": "Equipment instrument calibration certificate and recent maintenance service log",
            "why_it_matters": "Proves whether instrument drift or sensor degradation contributed to out-of-trend parameter readings under ICH Q7 Section 5.4.",
        })

    if "operator" in text_lower or "shift" in text_lower or "manual" in text_lower or "training" in text_lower:
        fallback_gaps.append({
            "gap": "Operator qualification and SOP training sign-off records for current manufacturing shift",
            "why_it_matters": "Verifies personnel competency and compliance with standard operating procedures under ICH Q7 Section 3.1.",
        })

    if "qc" in text_lower or "hplc" in text_lower or "psd" in text_lower or "assay" in text_lower or "spec" in text_lower or "oos" in text_lower:
        fallback_gaps.append({
            "gap": "Raw analytical instrument data packets, system suitability logs, and testing audit trails",
            "why_it_matters": "Rules out analytical testing errors or chromatographic integration anomalies prior to attributing failure to process execution.",
        })

    # Standard GMP default gap if none triggered
    if not fallback_gaps:
        fallback_gaps.append({
            "gap": "Batch Manufacturing Record (BMR) execution log sheets and raw material dispensing records",
            "why_it_matters": "Confirms actual process step execution times and batch charge weights against validated recipe parameters.",
        })

    logs.append(f"[{timestamp}] [Node 2] Completed evidence audit with {len(fallback_gaps)} critical compliance gaps.")
    return {"missing_evidence": fallback_gaps, "execution_logs": logs}

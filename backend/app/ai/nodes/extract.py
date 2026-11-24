import logging
import datetime
from typing import Dict, Any
from app.ai.state import RCAWorkflowState
from app.ai.schemas import DeviationFieldsOutput
from app.ai.client import get_llm, invoke_structured_output_with_retry
from app.services.extractor import detect_pharma_entities

logger = logging.getLogger("pharma_rca.ai.nodes.extract")


def extract_deviation_fields(state: RCAWorkflowState) -> Dict[str, Any]:
    """
    Node 1: Extracts GMP-relevant deviation fields from raw incident text.
    Never hallucinates batch numbers or dates; leaves missing fields null.
    """
    raw_text = state.get("raw_text", "")
    source_type = state.get("source_type", "text")
    logs = state.get("execution_logs", []).copy()
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    logger.info("[Node 1: extract_deviation_fields] Starting extraction from raw text...")
    logs.append(f"[{timestamp}] [Node 1] extract_deviation_fields: Processing {len(raw_text)} chars ({source_type})")

    llm = get_llm(temperature=0.0)

    if llm:
        prompt = (
            "You are a Senior Pharmaceutical Quality Assurance Specialist operating under ICH Q7 and cGMP standards.\n"
            "Analyze the following raw incident report and extract structured deviation fields.\n\n"
            "CRITICAL GMP INTEGRITY RULES:\n"
            "1. Extract ONLY facts explicitly stated in the source text.\n"
            "2. If a field (e.g. batch_lot_number, equipment_id, incident_date, deviation_number) is NOT explicitly mentioned, you MUST set it to null.\n"
            "3. NEVER invent, fabricate, or hallucinate batch numbers, lot codes, equipment tags, or timestamps.\n"
            "4. Choose severity from: 'Critical', 'Major', 'Minor'. Default to 'Major' if unclear.\n\n"
            f"--- RAW INCIDENT SOURCE ({source_type.upper()}) ---\n"
            f"{raw_text}\n"
        )
        try:
            output: DeviationFieldsOutput = invoke_structured_output_with_retry(
                llm, DeviationFieldsOutput, prompt
            )
            data = output.model_dump()
            logger.info(f"[Node 1] Extracted deviation: {data.get('deviation_number')} | {data.get('title')}")
            logs.append(f"[{timestamp}] [Node 1] Extracted via Groq: {data.get('deviation_number') or 'Unnumbered'} - {data.get('severity')}")
            return {"deviation_fields": data, "execution_logs": logs}
        except Exception as exc:
            logger.warning(f"[Node 1] Groq extraction error ({exc}); using rule-based GMP extractor.")
            logs.append(f"[{timestamp}] [Node 1] Groq error ({exc}); falling back to GMP rule-based extractor.")

    # Rule-based fallback extraction
    entities = detect_pharma_entities(raw_text)
    dev_num = entities["deviation_numbers"][0] if entities["deviation_numbers"] else None
    batch_num = entities["batch_lot_numbers"][0] if entities["batch_lot_numbers"] else None
    equip_id = entities["equipment_ids"][0] if entities["equipment_ids"] else None
    severity = entities["severities"][0] if entities["severities"] else "Major"

    first_line = raw_text.strip().splitlines()[0] if raw_text.strip() else "API Manufacturing Deviation"
    title = first_line[:120] if len(first_line) > 10 else f"Deviation Report {dev_num or ''}".strip()

    # Detect API product name if mentioned in text
    api_product = "Active Pharmaceutical Ingredient (API)"
    known_apis = [
        "Atorvastatin Calcium Trihydrate",
        "Atorvastatin Calcium",
        "Atorvastatin",
        "Metformin Hydrochloride",
        "Metformin HCl",
        "Metformin",
        "Paracetamol",
        "Ibuprofen",
        "Amoxicillin Trihydrate",
        "Omeprazole",
    ]
    for api_cand in known_apis:
        if api_cand.lower() in raw_text.lower():
            api_product = api_cand
            break

    fallback_data = {
        "deviation_number": dev_num,
        "title": title,
        "api_product_name": api_product,
        "batch_lot_number": batch_num,
        "equipment_id": equip_id,
        "manufacturing_stage": "Manufacturing / Purification",
        "incident_date": None,
        "severity": severity,
        "description": raw_text.strip()[:1500],
        "immediate_containment": "Quarantine affected lot under QA Yellow Tag. Review equipment line state.",
    }

    logs.append(f"[{timestamp}] [Node 1] Rule-based extraction complete. Found dev: {dev_num}, batch: {batch_num}, equip: {equip_id}")
    return {"deviation_fields": fallback_data, "execution_logs": logs}

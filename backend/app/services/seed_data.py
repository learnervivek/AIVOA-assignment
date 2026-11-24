import asyncio
import logging
from datetime import datetime, timezone, date
from uuid import uuid4
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.investigation import Investigation
from app.models.rca_analysis import RCAAnalysis
from app.models.capa import CAPARecommendation

logger = logging.getLogger(__name__)


async def seed_pharma_data():
    """Seeds realistic API pharmaceutical deviation, RCA, and CAPA data."""
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(
            select(Investigation).where(Investigation.deviation_number == "DEV-2026-0142")
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info("Sample investigation DEV-2026-0142 already exists. Skipping seed.")
            return

        inv_id = uuid4()
        investigation = Investigation(
            id=inv_id,
            deviation_number="DEV-2026-0142",
            title="Out-of-Specification (OOS) Particle Size Distribution in Atorvastatin Calcium Micronization",
            api_product_name="Atorvastatin Calcium Trihydrate",
            batch_lot_number="ATC-2026-0881",
            equipment_id="MILL-PIN-02",
            manufacturing_stage="Jet Milling & Micronization",
            incident_date=datetime(2026, 11, 20, 14, 30, tzinfo=timezone.utc),
            severity="Critical",
            description=(
                "During QC release testing of Atorvastatin Calcium Trihydrate batch ATC-2026-0881, "
                "laser diffraction (Malvern Mastersizer 3000) reported D90 at 54.2 µm against specification "
                "of NMT 45.0 µm. Microscopic evaluation indicated agglomerates rather than oversized "
                "primary crystalline particles."
            ),
            immediate_containment=(
                "Quarantined batch ATC-2026-0881 under QA Yellow Tag #Q-881. Suspended micronization "
                "operations on line 2. Placed process nitrogen gas supply and feed hopper on technical hold."
            ),
            raw_input_text=(
                "Batch 0881 milled on line 2 failed PSD D90 limit at 54.2um. Operator noted jet mill feeding "
                "was sluggish and nitrogen inlet pressure fluctuated around 5.2 bar instead of steady 6.8 bar. "
                "Hopper had slight cake formation around neck."
            ),
            source_type="text",
            status="Under Review",
        )
        session.add(investigation)

        rca = RCAAnalysis(
            id=uuid4(),
            investigation_id=inv_id,
            methodology="fishbone",
            five_whys_data=[
                {
                    "level": 1,
                    "why": "Why did batch ATC-2026-0881 fail the D90 particle size specification?",
                    "answer": "The finished micronized powder exhibited electrostatic agglomeration of primary API particles.",
                },
                {
                    "level": 2,
                    "why": "Why did fine crystalline particles agglomerate during milling?",
                    "answer": "Relative humidity inside the micronization chamber surged to 68% during the second half of the milling run.",
                },
                {
                    "level": 3,
                    "why": "Why did chamber humidity rise to 68% in an inert loop?",
                    "answer": "The closed-loop nitrogen gas supply experienced moisture breakthrough due to a saturated desiccant bed in dryer unit AD-04.",
                },
                {
                    "level": 4,
                    "why": "Why did desiccant bed AD-04 suffer moisture breakthrough without early warning?",
                    "answer": "Dew point sensor DP-104 had drifted by +18°C, giving a false reading of -65°C when actual gas dew point was -25°C.",
                },
                {
                    "level": 5,
                    "why": "Why was the calibration drift on sensor DP-104 not detected prior to the run?",
                    "answer": "Preventive maintenance SOP-ENG-241 scheduled calibration annually instead of quarterly for high-criticality continuous nitrogen lines.",
                },
            ],
            fishbone_6m_data={
                "man": [
                    "Operator did not cross-check inline hygrometer reading against manual shift log baseline",
                    "Shift handover note omitted warning about sluggish feed hopper flow",
                ],
                "machine": [
                    "Inlet nitrogen pressure dipped to 5.2 bar (operating range 6.5 - 7.0 bar)",
                    "Desiccant dryer unit AD-04 desiccant bed was fully moisture saturated",
                ],
                "material": [
                    "Pre-milling crystalline Atorvastatin bulk intermediate had compliant water content (4.2% H2O, spec 3.5 - 5.5%)",
                    "Solvent residue within ICH Q3C Class 2 limits",
                ],
                "method": [
                    "SOP-ENG-241 lacked quarterly calibration schedule for critical process gas dew point transmitters",
                    "No automated interlock to halt mill feed when process gas moisture exceeds threshold",
                ],
                "measurement": [
                    "Dew point transmitter DP-104 calibration drift of +18°C gave false dry signal",
                    "Malvern Mastersizer 3000 method verification confirmed measurement assay itself was fully valid",
                ],
                "environment": [
                    "External atmospheric humidity high (88% RH) due to heavy rainfall; cleanroom HVAC damper experienced seal bypass",
                ],
            },
            potential_root_causes=[
                {
                    "cause": "Calibration drift in dew point sensor DP-104 leading to undetected nitrogen desiccant saturation and moisture-induced API agglomeration",
                    "category": "Measurement",
                    "supporting_evidence": "Desiccant inspection revealed wet alumina beads; post-deviation bench recalibration confirmed DP-104 read -65°C at actual -25°C dew point.",
                    "confidence": 0.94,
                    "is_ai_suggested": True,
                    "is_confirmed_by_qa": True,
                    "qa_notes": "QA Principal Auditor confirmed. Matches sensor drift pattern in calibration log CAL-2026-902.",
                },
                {
                    "cause": "Cleanroom HVAC damper seal bypass allowing ambient humid air ingress during heavy rainfall",
                    "category": "Environment",
                    "supporting_evidence": "Building Management System (BMS) logged differential pressure dip to 8 Pa (limit > 15 Pa) between 13:45 and 14:10.",
                    "confidence": 0.72,
                    "is_ai_suggested": True,
                    "is_confirmed_by_qa": False,
                    "qa_notes": "Secondary contributing factor; cleanroom air entered when feed hopper door opened.",
                },
            ],
            missing_evidence=[
                {
                    "gap": "Continuous feed hopper inline RH datalogger trace between 13:00 and 15:00",
                    "why_it_matters": "ICH Q7 validation requires exact duration of moisture exposure to evaluate stability impact and determine if re-micronization is permissible.",
                },
                {
                    "gap": "Karl Fischer water titration of un-milled vs. milled retained sample from lot ATC-2026-0881",
                    "why_it_matters": "Proves whether moisture uptake occurred during milling or was pre-existing in bulk intermediate lot.",
                },
            ],
        )
        session.add(rca)

        capa_1 = CAPARecommendation(
            id=uuid4(),
            investigation_id=inv_id,
            action_type="Corrective",
            title="Replace Dew Point Transmitter DP-104 and Recharge Desiccant Bed AD-04",
            description=(
                "Install a brand new Vaisala DMT143 dew point transmitter with accredited 17025 calibration "
                "certificate. Completely purge and replace molecular sieve desiccant bed in dryer unit AD-04."
            ),
            rationale="Eliminates the immediate mechanical and measurement failure that caused wet nitrogen gas to contact API.",
            owner="Metrology & Instrumentation Team",
            target_due_date=date(2026, 12, 5),
            status="Approved",
            is_ai_suggested=True,
        )

        capa_2 = CAPARecommendation(
            id=uuid4(),
            investigation_id=inv_id,
            action_type="Preventive",
            title="Update SOP-ENG-241 for Quarterly Calibration & Implement PLC Nitrogen Moisture Interlock",
            description=(
                "1. Revise SOP-ENG-241 to establish quarterly recalibration frequency for all process gas dew point sensors.\n"
                "2. Program automated PLC interlock to trigger audible alarm and immediately halt mill feeder if nitrogen dew point exceeds -50°C."
            ),
            rationale="ICH Q7 Section 5.4 mandates automated controls and preventive maintenance for critical process parameters.",
            owner="QA Compliance & Automation Engineering",
            target_due_date=date(2026, 12, 20),
            status="Approved",
            is_ai_suggested=True,
        )

        session.add(capa_1)
        session.add(capa_2)
        await session.commit()
        logger.info("Successfully seeded API pharmaceutical deviation DEV-2026-0142 with RCA and CAPA.")


if __name__ == "__main__":
    asyncio.run(seed_pharma_data())

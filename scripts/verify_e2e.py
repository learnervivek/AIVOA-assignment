import asyncio
import os
import sys
import time
import httpx

# Ensure backend app is discoverable
sys.path.insert(0, os.path.abspath("backend"))

from app.main import app

async def run_e2e_verification():
    print("=" * 70)
    print("STARTING FULL END-TO-END VERIFICATION PASS")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Step 1: Health check
        print("\n[Step 1] Checking /health endpoint & PostgreSQL connectivity...")
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        health_data = res.json()
        print(f"-> System Status: {health_data['status']}, Database: {health_data['database']['database']} ({health_data['database']['status']})")
        assert health_data["database"]["status"] == "connected", "Database not connected!"

        # Step 2: PDF Extraction
        pdf_path = "sample_data/deviation_oos_assay.pdf"
        print(f"\n[Step 2] Testing PDF extraction with '{pdf_path}'...")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        extract_res = await client.post(
            "/api/investigations/extract-file",
            files={"file": ("deviation_oos_assay.pdf", pdf_bytes, "application/pdf")}
        )
        assert extract_res.status_code == 200, f"PDF extraction failed: {extract_res.text}"
        extract_data = extract_res.json()
        print(f"-> Extracted {extract_data['page_count']} page(s), {len(extract_data['extracted_text'])} characters.")
        print(f"-> Detected Entities: {extract_data['detected_entities']}")
        assert "DEV-2026-0914" in extract_data["detected_entities"]["deviation_numbers"]
        assert "REACT-CR-01" in extract_data["detected_entities"]["equipment_ids"]

        # Step 3: LangGraph AI Ingestion & Analysis
        print("\n[Step 3] Running LangGraph RCA Workflow via POST /api/ai/analyze...")
        ai_res = await client.post(
            "/api/ai/analyze",
            json={
                "raw_text": extract_data["extracted_text"],
                "source_type": "pdf",
                "preferred_methodology": "fishbone"
            }
        )
        assert ai_res.status_code == 200, f"AI analyze failed: {ai_res.text}"
        ai_data = ai_res.json()

        print(f"-> Extracted Deviation: {ai_data['deviation_fields'].get('deviation_number')} | Severity: {ai_data['deviation_fields'].get('severity')}")
        print(f"-> Missing Evidence Gaps Detected: {len(ai_data['missing_evidence'])}")
        for gap in ai_data['missing_evidence']:
            print(f"   * {gap['gap']}")
        print(f"-> 5-Whys Steps: {len(ai_data['five_whys_data'])}")
        print(f"-> Potential Root Causes: {len(ai_data['potential_root_causes'])}")
        print(f"-> CAPA Recommendations: {len(ai_data['capa_recommendations'])}")

        assert len(ai_data['missing_evidence']) >= 2, "Expected at least 2 missing evidence items"
        assert len(ai_data['potential_root_causes']) >= 1, "Expected at least 1 potential root cause"
        assert len(ai_data['capa_recommendations']) >= 1, "Expected at least 1 CAPA recommendation"

        # Step 4: Human-in-the-Loop Edits & QA Confirmation
        print("\n[Step 4] Simulating Human-in-the-Loop review & QA confirmation...")
        dev_fields = ai_data["deviation_fields"]
        dev_number = f"DEV-2026-0914-{int(time.time())}"
        dev_fields["deviation_number"] = dev_number
        dev_fields["title"] = "CONFIRMED: Crystallization Thermal Excursion & Assay OOS"
        dev_fields["status"] = "Under Review"

        # Confirm the first root cause with formal QA notes
        root_causes = ai_data["potential_root_causes"]
        if root_causes:
            root_causes[0]["is_confirmed_by_qa"] = True
            root_causes[0]["qa_notes"] = "QA verified cooling valve diaphragm failure via instrumentation log inspection."

        # Add a custom preventive CAPA
        capas = ai_data["capa_recommendations"]
        capas.append({
            "action_type": "Preventive",
            "title": "Automated Dual-Sensor Redundancy Installation",
            "description": "Install secondary thermocouple TT-104B on reactor jacket with automatic deviation alarm interlock.",
            "rationale": "Precludes silent sensor or valve drift during critical crystallization cycles.",
            "owner": "Instrumentation & Automation Lead",
            "target_due_date": "2026-12-15",
            "status": "Approved",
            "is_ai_suggested": False
        })

        # Step 5: Save Investigation atomically to PostgreSQL
        print("\n[Step 5] Persisting reviewed investigation to PostgreSQL via POST /api/investigations...")
        save_payload = {
            "deviation_number": dev_fields.get("deviation_number") or "DEV-2026-0914",
            "title": dev_fields.get("title"),
            "api_product_name": dev_fields.get("api_product_name") or "Atorvastatin Calcium Trihydrate",
            "batch_lot_number": dev_fields.get("batch_lot_number") or "BAT-ATC-2026-0914",
            "equipment_id": dev_fields.get("equipment_id") or "REACT-CR-01",
            "manufacturing_stage": dev_fields.get("manufacturing_stage") or "Reaction & Controlled Crystallization",
            "incident_date": dev_fields.get("incident_date") or "2026-11-20T03:45:00Z",
            "severity": dev_fields.get("severity") or "Critical",
            "description": dev_fields.get("description") or "Assay OOS following crystallization temperature excursion.",
            "immediate_containment": dev_fields.get("immediate_containment") or "Quarantined 420 kg under QA Yellow Tag #Q-914",
            "raw_input_text": extract_data["extracted_text"][:500],
            "source_type": "pdf",
            "status": dev_fields.get("status") or "Under Review",
            "rca_analysis": {
                "methodology": "fishbone",
                "five_whys_data": ai_data.get("five_whys_data", []),
                "fishbone_6m_data": ai_data.get("fishbone_6m_data", {}),
                "potential_root_causes": root_causes,
                "missing_evidence": ai_data.get("missing_evidence", []),
            },
            "capa_recommendations": capas,
        }

        save_res = await client.post("/api/investigations", json=save_payload)
        assert save_res.status_code == 201, f"Save investigation failed: {save_res.text}"
        saved_inv = save_res.json()
        saved_id = saved_inv["id"]
        print(f"-> Saved Investigation ID: {saved_id} (Status: {saved_inv['status']})")
        print(f"-> Preserved RCA Analyses: {len(saved_inv.get('rca_analyses', []))}")
        print(f"-> Preserved CAPA Recommendations: {len(saved_inv.get('capa_recommendations', []))}")

        # Step 6: Reload from DB and verify persistence integrity
        print(f"\n[Step 6] Reopening investigation from PostgreSQL via GET /api/investigations/{saved_id}...")
        get_res = await client.get(f"/api/investigations/{saved_id}")
        assert get_res.status_code == 200, f"Get investigation failed: {get_res.text}"
        reloaded = get_res.json()
        assert reloaded["id"] == saved_id
        assert reloaded["deviation_number"] == dev_fields["deviation_number"]
        assert reloaded["title"] == "CONFIRMED: Crystallization Thermal Excursion & Assay OOS"
        assert len(reloaded["rca_analyses"]) > 0
        first_rca = reloaded["rca_analyses"][0]
        assert first_rca["potential_root_causes"][0]["is_confirmed_by_qa"] is True
        assert first_rca["potential_root_causes"][0]["qa_notes"] == "QA verified cooling valve diaphragm failure via instrumentation log inspection."
        assert len(reloaded["capa_recommendations"]) == len(capas)
        print("-> Database round-trip verification: 100% matched!")

        # Step 7: Update investigation (QA Sign-off)
        print(f"\n[Step 7] Updating status to 'QA Approved' via PUT /api/investigations/{saved_id}...")
        save_payload["status"] = "QA Approved"
        put_res = await client.put(f"/api/investigations/{saved_id}", json=save_payload)
        assert put_res.status_code == 200, f"Update failed: {put_res.text}"
        updated_inv = put_res.json()
        assert updated_inv["status"] == "QA Approved"
        print(f"-> Successfully updated status to: {updated_inv['status']}")

        # Step 8: Verify investigations summary list
        print("\n[Step 8] Checking investigations summary list via GET /api/investigations...")
        list_res = await client.get("/api/investigations")
        assert list_res.status_code == 200, f"List failed: {list_res.text}"
        inv_list = list_res.json()
        print(f"-> Total investigations in PostgreSQL: {len(inv_list)}")
        found = any(i["id"] == saved_id and i["status"] == "QA Approved" for i in inv_list)
        assert found, "Saved investigation not found in summary list!"
        print(f"-> Verified: Saved investigation {saved_inv['deviation_number']} is live in DB list.")

        print("\n" + "=" * 70)
        print("ALL 8 END-TO-END VERIFICATION STEPS PASSED SUCCESSFULLY!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_e2e_verification())

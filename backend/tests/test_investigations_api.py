import io
import uuid
import pytest
from datetime import datetime, timezone
import httpx
from tests.test_extractor import create_sample_pdf_bytes


@pytest.mark.asyncio
async def test_extract_file_endpoint_success(client: httpx.AsyncClient):
    sample_text = "Deviation DEV-2026-0999 in Centrifuge CENT-02. Batch BAT-2026-5544 failed filtration."
    pdf_bytes = create_sample_pdf_bytes(sample_text)

    files = {"file": ("deviation_doc.pdf", pdf_bytes, "application/pdf")}
    response = await client.post("/api/investigations/extract-file", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "deviation_doc.pdf"
    assert data["file_type"] == "pdf"
    assert "DEV-2026-0999" in data["extracted_text"]
    assert "DEV-2026-0999" in data["detected_entities"]["deviation_numbers"]
    assert "BAT-2026-5544" in data["detected_entities"]["batch_lot_numbers"]


@pytest.mark.asyncio
async def test_extract_file_endpoint_invalid_extension(client: httpx.AsyncClient):
    files = {"file": ("notes.txt", b"plain text content", "text/plain")}
    response = await client.post("/api/investigations/extract-file", files=files)
    assert response.status_code == 400
    assert "Only PDF documents (.pdf) are supported" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extract_file_endpoint_empty_file(client: httpx.AsyncClient):
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = await client.post("/api/investigations/extract-file", files=files)
    assert response.status_code == 400
    assert "empty (0 bytes)" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extract_text_endpoint(client: httpx.AsyncClient):
    payload = {
        "content": (
            "From: shift-supervisor@pharma.com\n"
            "Subject: Incident Notification DEV-2026-0312\n"
            "Date: 2026-11-23T11:00:00Z\n\n"
            "Reactor REACT-04 agitation failure during coupling step. Lot LOT-2026-8871."
        ),
        "source_type": "email",
        "filename": "shift_mail.eml",
    }
    response = await client.post("/api/investigations/extract-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["parsed_headers"] is not None
    assert data["parsed_headers"]["from"] == "shift-supervisor@pharma.com"
    assert "REACT-04" in data["detected_entities"]["equipment_ids"]
    assert "DEV-2026-0312" in data["detected_entities"]["deviation_numbers"]


@pytest.mark.asyncio
async def test_create_investigation_with_rca_and_capa_single_transaction(client: httpx.AsyncClient):
    unique_suffix = int(datetime.now().timestamp() * 1000)
    dev_num = f"DEV-2026-TX-{unique_suffix}"
    payload = {
        "deviation_number": dev_num,
        "title": "Unidentified Impurity Peak in HPLC Assay of Atorvastatin API",
        "api_product_name": "Atorvastatin Calcium Trihydrate",
        "batch_lot_number": f"ATC-2026-{unique_suffix % 10000}",
        "equipment_id": "HPLC-QC-07",
        "manufacturing_stage": "Quality Control Release",
        "incident_date": datetime.now(timezone.utc).isoformat(),
        "severity": "Critical",
        "description": "Unknown chromatographic peak observed at RRT 1.42 with 0.18% area (ICH Q3A identification threshold 0.10%).",
        "immediate_containment": "Hold release of batch. Re-inject system suitability and prepare new mobile phase.",
        "raw_input_text": "QC reported unknown peak at 1.42 RRT in Atorvastatin batch test.",
        "source_type": "text",
        "status": "Under Review",
        "rca_analysis": {
            "methodology": "5_whys",
            "five_whys_data": [
                {"level": 1, "why": "Why did the HPLC report an unknown peak at RRT 1.42?", "answer": "Degradation product formed during sample preparation standing time."},
                {"level": 2, "why": "Why did the sample degrade in the autosampler vial?", "answer": "Autosampler cooler temperature failed, maintaining 28°C instead of 4°C."},
            ],
            "fishbone_6m_data": {
                "man": ["Analyst left vial on bench for 6 hours prior to run"],
                "machine": ["Autosampler Peltier cooling unit fan clogged"],
                "material": ["Diluent acetonitrile acidified improperly"],
                "method": ["SOP did not state maximum autosampler bench life"],
                "measurement": ["HPLC column temperature was stable at 35°C"],
                "environment": ["QC lab temperature was 24°C"],
            },
            "potential_root_causes": [
                {
                    "cause": "Sample solution degradation due to autosampler Peltier cooler fan failure and lack of solution stability time limit",
                    "category": "Machine",
                    "supporting_evidence": "Re-injected freshly prepared solution showed zero peak at RRT 1.42; Peltier temperature logged at 28.5°C.",
                    "confidence": 0.96,
                    "is_ai_suggested": True,
                    "is_confirmed_by_qa": True,
                    "qa_notes": "Confirmed by QC lab manager.",
                }
            ],
            "missing_evidence": [
                {
                    "gap": "LC-MS fragmentation pattern of the RRT 1.42 peak",
                    "why_it_matters": "Confirms chemical identity matches known lactone degradation impurity.",
                }
            ],
        },
        "capa_recommendations": [
            {
                "action_type": "Corrective",
                "title": "Service HPLC-QC-07 Autosampler Peltier Unit and Clean Heat Sink",
                "description": "Replace faulty Peltier cooling fan and clean air filter. Verify 4°C setpoint.",
                "rationale": "Prevents thermal degradation of sensitive API assay solutions.",
                "owner": "QC Metrology & Service Vendor",
                "target_due_date": "2026-12-10",
                "status": "Approved",
                "is_ai_suggested": True,
            },
            {
                "action_type": "Preventive",
                "title": "Amend SOP-QC-301 to Specify 4-Hour Solution Stability Time Limit",
                "description": "Establish clear 4-hour injection window in SOP-QC-301 for Atorvastatin sample solutions.",
                "rationale": "ICH Q2(R1) analytical validation compliance.",
                "owner": "QC Compliance Lead",
                "target_due_date": "2026-12-18",
                "status": "Proposed",
                "is_ai_suggested": True,
            },
        ],
    }

    # 1. Test POST /api/investigations
    create_res = await client.post("/api/investigations", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["deviation_number"] == dev_num
    assert len(created["rca_analyses"]) == 1
    assert len(created["capa_recommendations"]) == 2
    inv_id = created["id"]

    # 2. Duplicate deviation_number should fail with 400
    dup_res = await client.post("/api/investigations", json=payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # 3. Test GET /api/investigations (Summary list)
    list_res = await client.get("/api/investigations")
    assert list_res.status_code == 200
    summaries = list_res.json()
    assert len(summaries) >= 1
    matched = next((s for s in summaries if s["id"] == inv_id), None)
    assert matched is not None
    assert matched["deviation_number"] == dev_num
    assert matched["api_product_name"] == "Atorvastatin Calcium Trihydrate"
    assert matched["has_rca"] is True
    assert matched["capa_count"] == 2

    # 4. Test GET /api/investigations/{id} (Full details)
    get_res = await client.get(f"/api/investigations/{inv_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["id"] == inv_id
    assert len(detail["rca_analyses"]) == 1
    assert len(detail["capa_recommendations"]) == 2
    assert detail["rca_analyses"][0]["methodology"] == "5_whys"
    assert detail["rca_analyses"][0]["potential_root_causes"][0]["confidence"] == 0.96

    # 5. Test PUT /api/investigations/{id} (Update)
    update_payload = {
        "status": "QA Approved",
        "severity": "Major",
        "title": "Resolved: Unidentified Impurity Peak in HPLC Assay of Atorvastatin API",
    }
    put_res = await client.put(f"/api/investigations/{inv_id}", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["status"] == "QA Approved"
    assert updated["severity"] == "Major"
    assert "Resolved:" in updated["title"]

    # 6. Test DELETE /api/investigations/{id}
    del_res = await client.delete(f"/api/investigations/{inv_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 7. Confirm deleted
    not_found_res = await client.get(f"/api/investigations/{inv_id}")
    assert not_found_res.status_code == 404

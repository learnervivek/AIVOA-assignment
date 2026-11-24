import pytest
import httpx


@pytest.mark.asyncio
async def test_ai_analyze_endpoint(client: httpx.AsyncClient):
    raw_incident = (
        "Investigation DEV-2026-0812 initiated on Line 4. Atorvastatin Calcium Trihydrate batch "
        "ATC-2026-0922 failed moisture specification (KF titration 6.8% vs spec 3.5 - 5.5%). "
        "Fluidized bed dryer FBD-02 inlet air dew point transmitter DP-202 had drifted. "
        "Batch was immediately quarantined under QA tag #Y-922. Line 4 drying suspended."
    )

    payload = {
        "raw_text": raw_incident,
        "source_type": "text",
        "preferred_methodology": "fishbone",
    }

    response = await client.post("/api/ai/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # 1. Node 1: extract_deviation_fields
    assert "deviation_fields" in data
    dev = data["deviation_fields"]
    assert dev["deviation_number"] == "DEV-2026-0812"
    assert "Atorvastatin" in dev["api_product_name"] or "ATC-2026-0922" in str(dev)
    assert dev["batch_lot_number"] == "ATC-2026-0922"
    assert dev["equipment_id"] in ["FBD-02", "DP-202"]
    assert dev["severity"] in ["Critical", "Major", "Minor"]
    assert dev["description"] is not None

    # 2. Node 2: detect_missing_evidence
    assert "missing_evidence" in data
    assert len(data["missing_evidence"]) >= 1
    first_gap = data["missing_evidence"][0]
    assert "gap" in first_gap
    assert "why_it_matters" in first_gap

    # 3. Node 3: perform_rca_analysis
    assert "five_whys_data" in data
    assert len(data["five_whys_data"]) >= 3
    assert data["five_whys_data"][0]["level"] == 1

    assert "fishbone_6m_data" in data
    fb = data["fishbone_6m_data"]
    for cat in ["man", "machine", "material", "method", "measurement", "environment"]:
        assert cat in fb

    assert "potential_root_causes" in data
    assert len(data["potential_root_causes"]) >= 1
    for rc in data["potential_root_causes"]:
        assert rc["is_ai_suggested"] is True
        assert rc["is_confirmed_by_qa"] is False
        assert "cause" in rc
        assert "category" in rc
        assert "supporting_evidence" in rc
        assert 0.0 <= rc["confidence"] <= 1.0

    # 4. Node 4: recommend_capa
    assert "capa_recommendations" in data
    assert len(data["capa_recommendations"]) >= 1
    action_types = [c["action_type"] for c in data["capa_recommendations"]]
    assert any(t in ["Corrective", "Preventive"] for t in action_types)

    # 5. Clean execution logs
    assert "execution_logs" in data
    assert len(data["execution_logs"]) >= 4


@pytest.mark.asyncio
async def test_ai_refine_endpoint_whys(client: httpx.AsyncClient):
    # Initial state
    initial_state = {
        "raw_text": "Reactor REACT-01 temperature rose to 95C. Lot LOT-1122 quarantined.",
        "deviation_fields": {
            "deviation_number": "DEV-2026-0112",
            "title": "Temperature spike in REACT-01",
            "equipment_id": "REACT-01",
        },
        "five_whys_data": [
            {"level": 1, "why": "Why did temperature rise?", "answer": "Cooling valve failed to open."}
        ],
        "fishbone_6m_data": {"machine": ["Cooling valve valve-01 jammed"]},
        "potential_root_causes": [
            {
                "cause": "Cooling valve mechanical failure",
                "category": "Machine",
                "supporting_evidence": "Valve actuator was stuck.",
                "confidence": 0.85,
                "is_ai_suggested": True,
                "is_confirmed_by_qa": False,
            }
        ],
        "capa_recommendations": [],
    }

    refine_payload = {
        "current_state": initial_state,
        "instruction": "Dig deeper into Why #2 regarding pneumatic actuator air pressure supply to cooling valve",
    }

    response = await client.post("/api/ai/refine", json=refine_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["five_whys_data"]) >= 2
    assert "execution_logs" in data


@pytest.mark.asyncio
async def test_ai_refine_endpoint_capa(client: httpx.AsyncClient):
    initial_state = {
        "deviation_fields": {"equipment_id": "REACT-01"},
        "potential_root_causes": [{"cause": "Operator error", "category": "Man"}],
        "capa_recommendations": [],
    }

    refine_payload = {
        "current_state": initial_state,
        "instruction": "Add a preventive action for annual operator retraining on SOP-REACT-004",
    }

    response = await client.post("/api/ai/refine", json=refine_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["capa_recommendations"]) >= 1
    new_capa = data["capa_recommendations"][-1]
    assert new_capa["action_type"] in ["Preventive", "Corrective"]

import pytest
import httpx


@pytest.mark.asyncio
async def test_rca_endpoints(client: httpx.AsyncClient):
    # Fetch existing seeded investigation
    inv_res = await client.get("/api/v1/investigations")
    assert inv_res.status_code == 200
    investigations = inv_res.json()
    assert len(investigations) >= 1
    seeded = next((i for i in investigations if i["deviation_number"] == "DEV-2026-0142"), None)
    assert seeded is not None
    target_inv_id = seeded["id"]

    # Fetch RCA for this investigation
    rca_res = await client.get(f"/api/v1/rca/by-investigation/{target_inv_id}")
    assert rca_res.status_code == 200
    rcas = rca_res.json()
    assert len(rcas) >= 1
    rca_item = rcas[0]
    assert rca_item["methodology"] in ["fishbone", "5_whys", "hybrid"]
    assert "fishbone_6m_data" in rca_item
    assert "man" in rca_item["fishbone_6m_data"]
    assert "machine" in rca_item["fishbone_6m_data"]
    assert "material" in rca_item["fishbone_6m_data"]
    assert "method" in rca_item["fishbone_6m_data"]
    assert "measurement" in rca_item["fishbone_6m_data"]
    assert "environment" in rca_item["fishbone_6m_data"]
    assert len(rca_item["potential_root_causes"]) >= 1
    assert len(rca_item["missing_evidence"]) >= 1

    # Update RCA
    update_res = await client.patch(
        f"/api/v1/rca/{rca_item['id']}",
        json={"methodology": "fishbone"}
    )
    assert update_res.status_code == 200


@pytest.mark.asyncio
async def test_capa_endpoints(client: httpx.AsyncClient):
    inv_res = await client.get("/api/v1/investigations")
    assert inv_res.status_code == 200
    investigations = inv_res.json()
    seeded = next((i for i in investigations if i["deviation_number"] == "DEV-2026-0142"), None)
    assert seeded is not None
    target_inv_id = seeded["id"]

    # Fetch CAPAs
    capa_res = await client.get(f"/api/v1/capa/by-investigation/{target_inv_id}")
    assert capa_res.status_code == 200
    capas = capa_res.json()
    assert len(capas) >= 2
    action_types = [c["action_type"] for c in capas]
    assert "Corrective" in action_types
    assert "Preventive" in action_types

    # Create new CAPA
    new_capa = {
        "investigation_id": target_inv_id,
        "action_type": "Preventive",
        "title": "Install redundant inline dew point monitoring sensor",
        "description": "Install second independent dew point sensor on N2 header with voting logic.",
        "rationale": "ICH Q7 fail-safe redundancy against single-point sensor drift.",
        "owner": "Instrumentation Metrology",
        "target_due_date": "2026-12-30",
        "status": "Proposed",
        "is_ai_suggested": True,
    }
    create_capa_res = await client.post("/api/v1/capa", json=new_capa)
    assert create_capa_res.status_code == 201
    created = create_capa_res.json()
    assert created["title"] == new_capa["title"]

    # Update CAPA status
    update_res = await client.patch(
        f"/api/v1/capa/{created['id']}",
        json={"status": "Approved"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Approved"

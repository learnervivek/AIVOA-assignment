import pytest
from datetime import datetime, timezone
import httpx


@pytest.mark.asyncio
async def test_health_check_endpoint(client: httpx.AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI-Powered Pharma RCA Module"
    assert "database" in data
    assert data["database"]["status"] == "connected"
    assert data["database"]["database"] == "pharma_rca_db"


@pytest.mark.asyncio
async def test_api_v1_health_check_endpoint(client: httpx.AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_investigations(client: httpx.AsyncClient):
    response = await client.get("/api/v1/investigations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Find the seeded investigation DEV-2026-0142
    seeded = next((i for i in data if i["deviation_number"] == "DEV-2026-0142"), None)
    assert seeded is not None
    assert seeded["api_product_name"] == "Atorvastatin Calcium Trihydrate"
    assert seeded["severity"] == "Critical"
    assert seeded["status"] == "Under Review"


@pytest.mark.asyncio
async def test_create_and_fetch_investigation(client: httpx.AsyncClient):
    new_deviation = {
        "deviation_number": f"DEV-2026-TEST-{int(datetime.now().timestamp())}",
        "title": "Temperature Excursion during Vacuum Tray Drying of Metformin HCl",
        "api_product_name": "Metformin Hydrochloride",
        "batch_lot_number": "MET-2026-0104",
        "equipment_id": "VTD-01",
        "manufacturing_stage": "Vacuum Tray Drying",
        "incident_date": datetime.now(timezone.utc).isoformat(),
        "severity": "Major",
        "description": "Temperature probe TT-201 spiked to 92°C for 45 minutes against upper operating limit of 80°C.",
        "immediate_containment": "Heating steam supply manually shut down. Batch flagged in MES.",
        "raw_input_text": "Dryer temperature rose to 92C at 03:00. Operator switched to manual bypass.",
        "source_type": "text",
        "status": "Draft",
    }
    create_res = await client.post("/api/v1/investigations", json=new_deviation)
    assert create_res.status_code == 201
    created_data = create_res.json()
    inv_id = created_data["id"]
    assert created_data["deviation_number"] == new_deviation["deviation_number"]

    # Fetch by ID
    fetch_res = await client.get(f"/api/v1/investigations/{inv_id}")
    assert fetch_res.status_code == 200
    assert fetch_res.json()["title"] == new_deviation["title"]

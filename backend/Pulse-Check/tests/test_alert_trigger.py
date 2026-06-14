import asyncio
import json

import pytest

pytestmark = pytest.mark.anyio


async def test_monitor_goes_down_after_timeout(client, capsys):
    
    await client.post(
        "/monitors",
        json={"id": "device-down", "timeout": 1, "alert_email": "a@b.com"},
    )

    
    await asyncio.sleep(1.3)

    response = await client.get("/monitors/device-down")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "down"
    assert data["time_remaining"] == 0

    
    captured = capsys.readouterr()
    alert_lines = [line for line in captured.out.splitlines() if "ALERT" in line]
    assert len(alert_lines) >= 1
    alert_payload = json.loads(alert_lines[-1])
    assert alert_payload["ALERT"] == "Device device-down is down!"
    assert "time" in alert_payload


async def test_heartbeat_after_down_revives_monitor(client):
    await client.post(
        "/monitors",
        json={"id": "device-revive", "timeout": 1, "alert_email": "a@b.com"},
    )
    await asyncio.sleep(1.3)

    
    response = await client.get("/monitors/device-revive")
    assert response.json()["status"] == "down"

    
    response = await client.post("/monitors/device-revive/heartbeat")
    assert response.status_code == 200
    assert response.json()["monitor"]["status"] == "active"

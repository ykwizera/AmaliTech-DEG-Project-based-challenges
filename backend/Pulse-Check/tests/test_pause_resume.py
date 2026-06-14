import asyncio

import pytest

pytestmark = pytest.mark.anyio


async def test_pause_stops_timer(client):
    await client.post(
        "/monitors",
        json={"id": "device-pause", "timeout": 1, "alert_email": "a@b.com"},
    )
    response = await client.post("/monitors/device-pause/pause")
    assert response.status_code == 200
    assert response.json()["monitor"]["status"] == "paused"

    await asyncio.sleep(1.3)

    response = await client.get("/monitors/device-pause")
    assert response.json()["status"] == "paused"


async def test_heartbeat_unpauses_monitor(client):
    await client.post(
        "/monitors",
        json={"id": "device-unpause", "timeout": 60, "alert_email": "a@b.com"},
    )
    await client.post("/monitors/device-unpause/pause")

    response = await client.post("/monitors/device-unpause/heartbeat")
    assert response.status_code == 200
    data = response.json()["monitor"]
    assert data["status"] == "active"
    assert data["time_remaining"] > 55


async def test_pause_on_missing_id_returns_404(client):
    response = await client.post("/monitors/nope/pause")
    assert response.status_code == 404


async def test_pause_already_down_monitor_returns_409(client):
    await client.post(
        "/monitors",
        json={"id": "device-downpause", "timeout": 1, "alert_email": "a@b.com"},
    )
    await asyncio.sleep(1.3)

    response = await client.post("/monitors/device-downpause/pause")
    assert response.status_code == 409

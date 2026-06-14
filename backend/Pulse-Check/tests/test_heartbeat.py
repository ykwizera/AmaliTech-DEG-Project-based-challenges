import pytest

pytestmark = pytest.mark.anyio


async def test_heartbeat_resets_timer(client):
    await client.post(
        "/monitors",
        json={"id": "device-hb", "timeout": 60, "alert_email": "a@b.com"},
    )
    response = await client.post("/monitors/device-hb/heartbeat")
    assert response.status_code == 200
    data = response.json()
    assert data["monitor"]["heartbeat_count"] == 1
    assert data["monitor"]["status"] == "active"
    assert data["monitor"]["time_remaining"] > 55


async def test_heartbeat_on_missing_id_returns_404(client):
    response = await client.post("/monitors/does-not-exist/heartbeat")
    assert response.status_code == 404

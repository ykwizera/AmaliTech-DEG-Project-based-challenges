import pytest

pytestmark = pytest.mark.anyio


async def test_register_monitor_returns_201(client):
    response = await client.post(
        "/monitors",
        json={"id": "device-123", "timeout": 60, "alert_email": "admin@critmon.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "Monitor 'device-123' created" in data["message"]
    assert data["monitor"]["id"] == "device-123"
    assert data["monitor"]["status"] == "active"
    assert data["monitor"]["timeout"] == 60


async def test_register_monitor_appears_in_list(client):
    await client.post(
        "/monitors",
        json={"id": "device-abc", "timeout": 30, "alert_email": "a@b.com"},
    )
    response = await client.get("/monitors")
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert "device-abc" in ids


async def test_register_invalid_payload_returns_422(client):
    response = await client.post(
        "/monitors",
        json={"id": "device-x", "timeout": -5, "alert_email": "not-an-email"},
    )
    assert response.status_code == 422

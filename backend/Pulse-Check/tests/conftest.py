import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.monitor_store import store


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def clear_store():
    monitors = await store.all()
    for monitor_id, monitor in monitors.items():
        if monitor.timer_task is not None and not monitor.timer_task.done():
            monitor.timer_task.cancel()
        await store.delete(monitor_id)
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

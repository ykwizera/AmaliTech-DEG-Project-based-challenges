import asyncio
import time

from app.config import STATUS_ACTIVE, STATUS_DOWN
from app.monitor_store import Monitor, store
from app.alerts import fire_alert


async def _countdown(monitor_id: str, timeout: int) -> None:
    
    try:
        await asyncio.sleep(timeout)
    except asyncio.CancelledError:
        return

    monitor = await store.get(monitor_id)
    if monitor is None:
        return

    if monitor.status == STATUS_ACTIVE and monitor.deadline <= time.time():
        monitor.status = STATUS_DOWN
        monitor.timer_task = None
        await store.set(monitor)
        await fire_alert(monitor.id, monitor.alert_email)


def _cancel_existing_task(monitor: Monitor) -> None:
    if monitor.timer_task is not None and not monitor.timer_task.done():
        monitor.timer_task.cancel()
    monitor.timer_task = None


def start_timer(monitor: Monitor) -> None:
    
    _cancel_existing_task(monitor)
    monitor.status = STATUS_ACTIVE
    monitor.deadline = time.time() + monitor.timeout
    monitor.timer_task = asyncio.create_task(
        _countdown(monitor.id, monitor.timeout)
    )


def pause_timer(monitor: Monitor) -> None:
    _cancel_existing_task(monitor)
    monitor.status = "paused"
    
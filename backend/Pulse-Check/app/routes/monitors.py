import time

from fastapi import APIRouter, HTTPException, status

from app.config import STATUS_DOWN, STATUS_PAUSED
from app.models import MonitorCreateRequest, MonitorResponse, MessageResponse
from app.monitor_store import Monitor, store
from app.timer_manager import start_timer, pause_timer

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(payload: MonitorCreateRequest):
    
    monitor = Monitor(
        id=payload.id,
        timeout=payload.timeout,
        alert_email=payload.alert_email,
    )
    start_timer(monitor)
    await store.set(monitor)

    return MessageResponse(
        message=f"Monitor '{monitor.id}' created. Countdown started for {monitor.timeout}s.",
        monitor=MonitorResponse(**monitor.to_dict()),
    )


@router.get("", response_model=list[MonitorResponse])
async def list_monitors():
   
    monitors = await store.all()
    return [MonitorResponse(**m.to_dict()) for m in monitors.values()]


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(monitor_id: str):
    
    monitor = await store.get(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail=f"Monitor '{monitor_id}' not found.")
    return MonitorResponse(**monitor.to_dict())


@router.post("/{monitor_id}/heartbeat", response_model=MessageResponse)
async def heartbeat(monitor_id: str):
    monitor = await store.get(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail=f"Monitor '{monitor_id}' not found.")

    was_paused = monitor.status == STATUS_PAUSED
    was_down = monitor.status == STATUS_DOWN

    monitor.last_heartbeat = time.time()
    monitor.heartbeat_count += 1
    start_timer(monitor)  
    await store.set(monitor)

    if was_paused:
        note = "Monitor was paused; un-paused and timer restarted."
    elif was_down:
        note = "Monitor was down; revived and timer restarted."
    else:
        note = "Timer reset."

    return MessageResponse(
        message=f"Heartbeat received for '{monitor.id}'. {note}",
        monitor=MonitorResponse(**monitor.to_dict()),
    )


@router.post("/{monitor_id}/pause", response_model=MessageResponse)
async def pause(monitor_id: str):
    monitor = await store.get(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail=f"Monitor '{monitor_id}' not found.")

    if monitor.status == STATUS_DOWN:
        raise HTTPException(
            status_code=409,
            detail=f"Monitor '{monitor_id}' is already down. Send a heartbeat to revive it.",
        )

    pause_timer(monitor)
    await store.set(monitor)

    return MessageResponse(
        message=f"Monitor '{monitor.id}' paused. No alerts will fire until heartbeat is received.",
        monitor=MonitorResponse(**monitor.to_dict()),
    )


@router.delete("/{monitor_id}", response_model=MessageResponse)
async def delete_monitor(monitor_id: str):
    monitor = await store.get(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail=f"Monitor '{monitor_id}' not found.")

    if monitor.timer_task is not None and not monitor.timer_task.done():
        monitor.timer_task.cancel()

    await store.delete(monitor_id)
    return MessageResponse(message=f"Monitor '{monitor_id}' deleted.")

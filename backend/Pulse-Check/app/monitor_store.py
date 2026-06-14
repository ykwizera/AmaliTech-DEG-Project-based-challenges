import time
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Optional

from app.config import STATUS_ACTIVE


@dataclass
class Monitor:
    id: str
    timeout: int
    alert_email: str
    status: str = STATUS_ACTIVE
    created_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    deadline: float = 0.0  # epoch time when the monitor will expire
    heartbeat_count: int = 0
    timer_task: Optional[asyncio.Task] = field(default=None, repr=False)

    def time_remaining(self) -> float:
        """Seconds remaining before this monitor expires.

        Returns 0 if down/expired. Returns timeout if paused (frozen).
        """
        if self.status == "down":
            return 0.0
        if self.status == "paused":
            return float(self.timeout)
        remaining = self.deadline - time.time()
        return max(0.0, remaining)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timeout": self.timeout,
            "alert_email": self.alert_email,
            "status": self.status,
            "time_remaining": round(self.time_remaining(), 2),
            "created_at": self.created_at,
            "last_heartbeat": self.last_heartbeat,
            "heartbeat_count": self.heartbeat_count,
        }


class MonitorStore:
    """Thread/async-safe in-memory store for monitors."""

    def __init__(self):
        self._monitors: Dict[str, Monitor] = {}
        self._lock = asyncio.Lock()

    async def get(self, monitor_id: str) -> Optional[Monitor]:
        async with self._lock:
            return self._monitors.get(monitor_id)

    async def set(self, monitor: Monitor) -> None:
        async with self._lock:
            self._monitors[monitor.id] = monitor

    async def all(self) -> Dict[str, Monitor]:
        async with self._lock:
            # shallow copy is fine - Monitor objects are mutated in place
            return dict(self._monitors)

    async def delete(self, monitor_id: str) -> None:
        async with self._lock:
            self._monitors.pop(monitor_id, None)


store = MonitorStore()

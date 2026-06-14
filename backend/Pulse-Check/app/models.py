from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class MonitorCreateRequest(BaseModel):
    id: str = Field(..., min_length=1, description="Unique device/monitor identifier")
    timeout: int = Field(..., gt=0, description="Countdown duration in seconds")
    alert_email: EmailStr = Field(..., description="Email to notify on alert")


class MonitorResponse(BaseModel):
    id: str
    timeout: int
    alert_email: str
    status: str
    time_remaining: Optional[float] = None
    created_at: float
    last_heartbeat: float
    heartbeat_count: int


class MessageResponse(BaseModel):
    message: str
    monitor: Optional[MonitorResponse] = None

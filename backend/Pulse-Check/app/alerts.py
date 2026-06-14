import json
import time

import httpx

from app.config import ALERT_WEBHOOK_URL


async def fire_alert(monitor_id: str, alert_email: str) -> dict:
   
    payload = {
        "ALERT": f"Device {monitor_id} is down!",
        "time": time.time(),
        "alert_email": alert_email,
    }

    
    print(json.dumps(payload))

    
    if ALERT_WEBHOOK_URL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(ALERT_WEBHOOK_URL, json=payload)
        except Exception as exc: 
            print(json.dumps({"ALERT_WEBHOOK_ERROR": str(exc)}))

    return payload

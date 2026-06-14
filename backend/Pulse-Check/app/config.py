import os


ALERT_WEBHOOK_URL = os.environ.get("ALERT_WEBHOOK_URL", "").strip()

STATUS_ACTIVE = "active"
STATUS_PAUSED = "paused"
STATUS_DOWN = "down"

MIN_TIMEOUT_SECONDS = 1

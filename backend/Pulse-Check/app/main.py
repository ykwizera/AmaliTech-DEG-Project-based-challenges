from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes import monitors

app = FastAPI(
    title="Pulse-Check API (Watchdog Sentinel)",
    description="A Dead Man's Switch API for monitoring remote devices.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitors.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

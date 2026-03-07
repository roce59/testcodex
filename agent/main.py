"""
Diagnostic agent for IT fleet management.

Run locally:
    python main.py

Or with custom host/port:
    python main.py --host 0.0.0.0 --port 8080

API endpoints:
    GET /              - Agent info + health
    GET /api/diag      - Full diagnostic report
    GET /api/apps      - Installed applications (?search=...)
    GET /api/hardware  - Hardware & OS info
    GET /api/processes - Running processes (?limit=N)
    GET /api/network   - Network interfaces & DNS
"""
import argparse
import platform
import socket
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from modules import apps, hardware, network, processes

app = FastAPI(
    title="Testcodex Diagnostic Agent",
    description="IT fleet management diagnostic agent",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/", summary="Agent health check")
def root():
    return {
        "agent": "testcodex-diag",
        "version": "2.0.0",
        "status": "ok",
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "timestamp": _timestamp(),
    }


@app.get("/api/apps", summary="Installed applications")
def get_apps(search: str = ""):
    data = apps.collect(search=search)
    return JSONResponse(content={"timestamp": _timestamp(), **data})


@app.get("/api/hardware", summary="Hardware and OS information")
def get_hardware():
    data = hardware.collect()
    return JSONResponse(content={"timestamp": _timestamp(), **data})


@app.get("/api/processes", summary="Running processes")
def get_processes(limit: int = 50):
    data = processes.collect(limit=limit)
    return JSONResponse(content={"timestamp": _timestamp(), **data})


@app.get("/api/network", summary="Network interfaces and DNS")
def get_network():
    data = network.collect()
    return JSONResponse(content={"timestamp": _timestamp(), **data})


@app.get("/api/diag", summary="Full diagnostic report")
def get_full_diag():
    return JSONResponse(content={
        "timestamp": _timestamp(),
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "hardware": hardware.collect(),
        "network": network.collect(),
        "apps": apps.collect(),
        "processes": processes.collect(limit=20),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testcodex Diagnostic Agent")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")
    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )

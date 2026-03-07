# Testcodex — Diagnostic Agent

A lightweight REST API agent for **IT fleet management**. Deploy it on Windows endpoints and query them locally or remotely to collect diagnostic information.

---

## Architecture

```
agent/
├── main.py          # FastAPI app — all API endpoints
├── service.py       # Windows Service wrapper (pywin32)
├── agent.spec       # PyInstaller build spec → agent.exe
├── requirements.txt
└── modules/
    ├── apps.py      # Installed applications (Windows registry)
    ├── hardware.py  # CPU, RAM, disk, OS info
    ├── processes.py # Running processes
    └── network.py   # Network interfaces & DNS
```

---

## Quick start (dev / local)

```bash
cd agent
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000/docs` for the interactive API documentation.

### Listen on all interfaces (remote access)

```bash
python main.py --host 0.0.0.0 --port 8000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check, hostname, platform |
| GET | `/api/diag` | Full diagnostic report (all modules) |
| GET | `/api/apps` | Installed applications |
| GET | `/api/apps?search=chrome` | Filter apps by name |
| GET | `/api/hardware` | CPU, RAM, disks, OS version |
| GET | `/api/processes?limit=50` | Running processes (sorted by RAM) |
| GET | `/api/network` | Network interfaces and DNS servers |

All responses are JSON with a `timestamp` field (UTC ISO 8601).

---

## Deploy on Windows endpoints

### Option 1 — Run directly

```bat
agent.exe --host 0.0.0.0 --port 8000
```

### Option 2 — Install as a Windows Service

The agent can run as a Windows Service so it starts automatically on boot:

```bat
# Install
python service.py install

# Start
python service.py start

# Stop / remove
python service.py stop
python service.py remove
```

Or with the compiled binary, use [NSSM](https://nssm.cc/):

```bat
nssm install TestcodexAgent agent.exe --host 0.0.0.0 --port 8000
nssm start TestcodexAgent
```

---

## Build a standalone .exe (no Python required on endpoints)

```bash
pip install pyinstaller
pyinstaller agent.spec
# Output: dist/agent.exe
```

Distribute `dist/agent.exe` via GPO, SCCM, or Intune. No Python installation needed on the target machine.

---

## Remote diagnostic example

```bash
# From a management machine, query any endpoint
curl http://192.168.1.42:8000/api/diag

# Get installed apps filtered by name
curl "http://192.168.1.42:8000/api/apps?search=office"

# Check disk space
curl http://192.168.1.42:8000/api/hardware | python -m json.tool
```

---

## Adding new diagnostic modules

1. Create `agent/modules/mymodule.py` with a `collect()` function returning a dict
2. Import it in `main.py` and add a route:
   ```python
   from modules import mymodule

   @app.get("/api/mymodule")
   def get_mymodule():
       return {"timestamp": _timestamp(), **mymodule.collect()}
   ```
3. Optionally include it in `/api/diag`

---

## Security notes

- By default, the agent listens on `127.0.0.1` (localhost only)
- For remote access, use `--host 0.0.0.0` and protect with a firewall rule or VPN
- Consider adding API key authentication for production deployments

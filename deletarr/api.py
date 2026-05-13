from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import threading
import yaml
from .main import run_deletarr
from .config import load_config, get_version
from .clients import QbitClient, radarr_test_connection, sonarr_test_connection

# A single run (dry or real) at a time. FastAPI runs sync handlers on a threadpool,
# so two concurrent /api/run calls would otherwise both walk hardlinks and both delete.
_run_lock = threading.Lock()

# In-memory log buffer
log_buffer = []

class ListHandler(logging.Handler):
    """
    Custom logging handler that appends logs to a list, keeping only the last N items.
    """
    def __init__(self, capacity=100):
        super().__init__()
        self.capacity = capacity
        
    def emit(self, record):
        try:
            msg = self.format(record)
            log_buffer.append(msg)
            if len(log_buffer) > self.capacity:
                log_buffer.pop(0)
        except Exception:
            self.handleError(record)

# Initialize capture handler
capture_handler = ListHandler(capacity=200)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
capture_handler.setFormatter(formatter)
# Attach to root logger
logging.getLogger().addHandler(capture_handler)
# Attach to uvicorn logger as well to capture access logs
logging.getLogger("uvicorn").addHandler(capture_handler)

app = FastAPI(title="Deletarr API", version=get_version())

# CORS only applies when the SPA is hosted on a different origin than the API.
# In production the SPA is served same-origin by FastAPI, so this never fires.
# For local development (Vite dev server) we allow the standard Vite ports.
# Extra origins can be added via DELETARR_ALLOWED_ORIGINS (comma-separated).
_default_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
_extra = os.environ.get("DELETARR_ALLOWED_ORIGINS", "")
_allowed_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_config_path():
    config_path = os.environ.get('DELETARR_CONFIG')
    if not config_path:
        default_config = './config/config.yml'
        docker_config = '/config/config.yml'
        config_path = docker_config if os.path.exists(docker_config) else default_config
    return config_path

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": get_version(),
        "env": os.environ.get('DELETARR_ENV')
    }

@app.get("/api/health/services")
def health_services():
    config_path = get_config_path()
    config = load_config(config_path)
    results = {}
    
    # qBittorrent
    try:
        qbit = QbitClient(config['qBittorrent'])
        results['qBittorrent'] = qbit.test_connection()
    except Exception as e:
        results['qBittorrent'] = {"status": "error", "message": str(e)}
        
    # Radarr
    radarr_conf = config.get('Radarr')
    if radarr_conf and radarr_conf.get('enabled', True):
        results['Radarr'] = radarr_test_connection(radarr_conf)
    else:
        results['Radarr'] = {"status": "disabled"}
        
    # Sonarr
    sonarr_conf = config.get('Sonarr')
    if sonarr_conf and sonarr_conf.get('enabled', True):
        results['Sonarr'] = sonarr_test_connection(sonarr_conf)
    else:
        results['Sonarr'] = {"status": "disabled"}
        
    return results

@app.get("/api/config")
def get_config():
    path = get_config_path()
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
def save_config(new_config: dict = Body(...)):
    path = get_config_path()
    try:
        # Basic validation: ensure it's a dict and not empty
        if not isinstance(new_config, dict) or not new_config:
            raise HTTPException(status_code=400, detail="Invalid configuration data")
            
        # Safe Write: Write to temp file first
        temp_path = f"{path}.tmp"
        with open(temp_path, 'w') as f:
            yaml.safe_dump(new_config, f, default_flow_style=False, sort_keys=False)
        
        # Atomically move temp file to original path
        os.replace(temp_path, path)
        
        logging.info("Configuration updated successfully via API.")
        return {"status": "success", "message": "Configuration saved"}
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}")
        if os.path.exists(f"{path}.tmp"):
            os.remove(f"{path}.tmp")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
def get_logs():
    return {"logs": log_buffer}

@app.get("/api/dry-run")
def dry_run():
    """
    Trigger a dry run immediately and return results.
    """
    if not _run_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Another run is already in progress")
    try:
        results = run_deletarr(dry_run=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _run_lock.release()

@app.post("/api/run")
def trigger_run():
    """
    Trigger a real run immediately.
    """
    if not _run_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Another run is already in progress")
    try:
        results = run_deletarr(dry_run=False)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _run_lock.release()

# Serves static files for the frontend
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
# In docker, we might put it elsewhere, e.g. /app/frontend/dist
# Let's check a few common places or env var
FRONTEND_DIST = os.environ.get("FRONTEND_DIST", os.path.join(os.getcwd(), "frontend/dist"))

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    FRONTEND_DIST_REAL = os.path.realpath(FRONTEND_DIST)
    INDEX_HTML = os.path.join(FRONTEND_DIST_REAL, "index.html")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Unknown /api/* routes must 404 rather than silently returning the SPA HTML.
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        # Resolve the requested path and verify it stays inside the dist root
        # before serving. Blocks traversal via ../ or symlink jumps.
        requested = os.path.realpath(os.path.join(FRONTEND_DIST_REAL, full_path))
        if (
            os.path.commonpath([requested, FRONTEND_DIST_REAL]) == FRONTEND_DIST_REAL
            and os.path.isfile(requested)
        ):
            return FileResponse(requested)

        # SPA fallback: always the fixed index.html, never an attacker-controlled path.
        return FileResponse(INDEX_HTML)
else:
    logging.warning(f"Frontend dist not found at {FRONTEND_DIST}. Web UI will not be available.")

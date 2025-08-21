import asyncio
import logging
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .db import init_db
from .auth import bootstrap_admin
from .routes import settings, mappings, templates, queue, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    bootstrap_admin()
    logging.info("FastAPI started - SMTP server managed by supervisor")
    
    yield
    
    # Shutdown
    logging.info("FastAPI shutting down")

def check_smtp_running():
    """Check if SMTP server process is running"""
    try:
        # Check if the SMTP process is running via supervisor
        result = subprocess.run(['supervisorctl', 'status', 'smtp'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'RUNNING' in result.stdout:
            return True
    except Exception as e:
        logging.debug(f"supervisorctl check failed: {e}")
    
    # Fallback: check if port 2525 is listening
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 2525))
        sock.close()
        return result == 0
    except Exception as e:
        logging.debug(f"socket check failed: {e}")
    
    return False

app = FastAPI(title="SignalHub API", lifespan=lifespan)

# Add health endpoint BEFORE static files mount
@app.get("/healthz")
def health():
    return {
        "status": "ok", 
        "smtp_running": check_smtp_running()
    }

app.include_router(settings.router, prefix="/api")
app.include_router(mappings.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(queue.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

# Serve React static files (this should be LAST)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

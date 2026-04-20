import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from pythonbot.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Pythonbot Daemon iniciando...")

    # Import tools to trigger registration
    import pythonbot.tools  # noqa: F401

    logger.info("Ferramentas registradas com sucesso.")
    yield
    logger.info("Pythonbot Daemon encerrando...")


app = FastAPI(
    title="Pythonbot Core Daemon",
    version="0.1.0",
    lifespan=lifespan,
)

# Lazy import dashboard routers to avoid circular imports
try:
    from pythonbot.interfaces.dashboard.api import api_router
    from pythonbot.interfaces.dashboard.ws import ws_router

    app.include_router(api_router, prefix="/api", tags=["api"])
    app.include_router(ws_router, tags=["websocket"])
except ImportError as e:
    logger.warning(f"Dashboard routers não carregados: {e}")


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Pythonbot is running"}


# Mount static files for dashboard (must be LAST — catches all unmatched routes)
STATIC_DIR = Path(__file__).parent.parent / "interfaces" / "dashboard" / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

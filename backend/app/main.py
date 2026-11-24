"""FastAPI main application entrypoint for SEKAT-AI."""

from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from backend.app.core.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    CORS_ORIGINS,
    OUTPUT_DIR,
    UPLOADS_DIR,
    WORKSPACE_DIR,
)
from backend.app.api.routes import router as api_router

FRONTEND_INDEX = WORKSPACE_DIR / "frontend" / "index.html"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

# Serve generated outputs and uploads as static assets
app.mount("/static/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.get("/", tags=["Root"])
def root(request: Request):
    """Root status summary endpoint or dashboard response for web browsers."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept and "application/json" not in accept:
        return FileResponse(str(FRONTEND_INDEX))
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "tagline": "Cegah Api Melebar, Jaga Napas Warga",
        "competition": "AIRIMPACT 2026",
        "status": "online",
        "docs_url": "/docs",
        "dashboard_url": "/app",
    }


@app.get("/app", response_class=FileResponse, tags=["Dashboard"])
def get_dashboard():
    """Serves the SMOKECUT Interactive Web Dashboard."""
    return FileResponse(str(FRONTEND_INDEX))


@app.get("/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

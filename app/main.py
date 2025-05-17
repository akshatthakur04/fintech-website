from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from config import settings
from app.api.routers import api_router
from app.templates import templates  # Import templates from the new module

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG
)

# Mount static files directory
static_dir_path = Path(settings.STATIC_DIR).resolve()
app.mount("/static", StaticFiles(directory=static_dir_path), name="static")

# Include API router under /api prefix
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")
    logger.info(f"Static files mounted from: {static_dir_path}")

    # Log template search paths instead of non-existent .directory
    template_paths = templates.env.loader.searchpath
    logger.info(f"Templates configured from: {template_paths}")

    # Warn if static or template directories do not exist
    if not static_dir_path.exists():
        logger.warning(f"Static directory {static_dir_path} does not exist!")
    for path in template_paths:
        if not Path(path).exists():
            logger.warning(f"Templates directory {path} does not exist!")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutdown complete.")

# Example root endpoint serving an HTML page
tags_metadata = [{"name": "root", "description": "Root HTML endpoint."}]

@app.get("/", tags=["root"])
async def read_root(request: Request):
    logger.info("Root endpoint / was accessed.")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Dashboard"}
    )
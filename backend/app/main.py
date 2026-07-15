import sys
import os
import logging
import time

# Ensure the backend directory is in the Python path to resolve imports when running from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import engine

# Initialize logging configuration
setup_logging()
logger = logging.getLogger("app.main")

# Instantiate core FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Qyverion AI-Powered SOC platform backend console.",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS (Cross-Origin Resource Sharing) policies
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register consolidated API controllers
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Middleware: Log incoming requests, HTTP methods, and latency
@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    # Process request
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"
    
    # Avoid clogging logs with static assets or health checks in production if needed,
    # but logging them in debug mode is helpful
    logger.info(
        f"Request: {method} {path} - Status: {response.status_code} - Completed in: {formatted_process_time}"
    )
    
    # Prevent caching in development to ensure latest files load immediately
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# API endpoint: Health check (Task requirement for verifying database connection)
@app.get(f"{settings.API_V1_STR}/health", tags=["System"])
def health_check() -> JSONResponse:
    """
    Verifies API availability and validates PostgreSQL database connectivity.
    """
    db_status = "healthy"
    details = {}
    
    try:
        # Perform light-weight ping execution
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        details["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failure: {str(e)}")
        db_status = "unhealthy"
        details["database"] = f"error: {str(e)}"
        
    return JSONResponse(
        status_code=200 if db_status == "healthy" else 500,
        content={
            "status": db_status,
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "details": details
        }
    )

# Mount the static frontend.
# Statically serves index.html, style.css, and app.js.
# Uses absolute path calculation to prevent working directory launch mismatch.
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
frontend_dir = os.path.join(base_dir, "frontend")

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info(f"Frontend static files successfully mounted from: {frontend_dir}")
else:
    logger.warning(f"Frontend static files directory not found at: {frontend_dir}")

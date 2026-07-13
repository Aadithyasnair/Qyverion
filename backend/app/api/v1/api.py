from fastapi import APIRouter
from app.api.v1.endpoints import logs, alerts, indicators

# Core v1 API Router setup
api_router = APIRouter()

# Group endpoint modules
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["Threat Intelligence"])

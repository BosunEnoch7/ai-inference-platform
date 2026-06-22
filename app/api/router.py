from fastapi import APIRouter

from app.api.routes import health, inference, metrics

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metrics.router, tags=["operations"])
api_router.include_router(inference.router, prefix="/api/v1", tags=["inference"])

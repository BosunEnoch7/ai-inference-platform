from fastapi import APIRouter

from app.core.config import get_settings
from app.models.health import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="healthy", version=settings.app_version)


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness check")
async def ready() -> ReadinessResponse:
    settings = get_settings()
    return ReadinessResponse(status="ready", provider=settings.llm_provider)


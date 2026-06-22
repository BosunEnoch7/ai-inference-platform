from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_provider
from app.core.config import get_settings
from app.models.health import HealthResponse, ReadinessResponse
from app.providers.base import LLMProvider

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="healthy", version=settings.app_version)


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness check")
async def ready(
    provider: Annotated[LLMProvider, Depends(get_provider)],
) -> ReadinessResponse:
    return ReadinessResponse(status="ready", provider=provider.name)

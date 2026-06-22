import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import PlatformError
from app.core.logging import configure_logging
from app.core.metrics_middleware import MetricsMiddleware
from app.core.middleware import RequestIDMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Cloud-ready API for provider-independent AI inference.",
        lifespan=lifespan,
    )
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(MetricsMiddleware)
    application.include_router(api_router)

    @application.exception_handler(PlatformError)
    async def platform_error_handler(request: Request, exc: PlatformError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        headers = dict(exc.headers)
        if request_id:
            headers["X-Request-ID"] = request_id
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id,
                }
            },
        )

    @application.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            "Unhandled application error",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            headers={"X-Request-ID": request_id} if request_id else None,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred.",
                    "request_id": request_id,
                }
            },
        )

    return application


app = create_app()

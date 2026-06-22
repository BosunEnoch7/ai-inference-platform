from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, ConfigurationError


async def verify_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    if not settings.api_auth_enabled:
        return

    configured_key = settings.inference_api_key
    if configured_key is None:
        raise ConfigurationError(
            "Inference authentication is enabled but not configured.",
            code="authentication_not_configured",
        )

    supplied_key = api_key or ""
    expected_key = configured_key.get_secret_value()
    if not compare_digest(supplied_key.encode("utf-8"), expected_key.encode("utf-8")):
        raise AuthenticationError()

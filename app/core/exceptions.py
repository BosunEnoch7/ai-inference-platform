class PlatformError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.headers = headers or {}


class InferenceError(PlatformError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "inference_failed",
        status_code: int = 502,
    ) -> None:
        super().__init__(message, code=code, status_code=status_code)


class ConfigurationError(PlatformError):
    def __init__(self, message: str, *, code: str = "service_not_configured") -> None:
        super().__init__(message, code=code, status_code=503)


class AuthenticationError(PlatformError):
    def __init__(self) -> None:
        super().__init__(
            "A valid API key is required.",
            code="invalid_api_key",
            status_code=401,
            headers={"WWW-Authenticate": "ApiKey"},
        )


class RateLimitExceededError(PlatformError):
    def __init__(self, retry_after: int) -> None:
        super().__init__(
            "The inference rate limit has been exceeded.",
            code="rate_limit_exceeded",
            status_code=429,
            headers={"Retry-After": str(retry_after)},
        )

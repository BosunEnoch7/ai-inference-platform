class PlatformError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


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
        )

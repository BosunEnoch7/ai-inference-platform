class InferenceError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "inference_failed",
        status_code: int = 502,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


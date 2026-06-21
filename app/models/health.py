from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    version: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    provider: str


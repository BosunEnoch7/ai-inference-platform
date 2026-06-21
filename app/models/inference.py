from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    max_tokens: int = Field(default=256, ge=1, le=4_096)
    temperature: float = Field(default=0.7, ge=0, le=2)


class ProviderResult(BaseModel):
    text: str
    model: str


class InferenceResponse(BaseModel):
    request_id: str
    output: str
    model: str
    provider: str


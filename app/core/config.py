from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI Inference Platform"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    llm_provider: str = "mock"
    inference_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    openai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


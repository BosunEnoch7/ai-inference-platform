from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
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
    llm_provider: Literal["mock", "openai"] = "mock"
    inference_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    api_auth_enabled: bool = False
    inference_api_key: SecretStr | None = None
    rate_limit_enabled: bool = False
    rate_limit_requests: int = Field(default=60, ge=1, le=100_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=86_400)
    rate_limit_fail_open: bool = False
    redis_url: SecretStr = SecretStr("redis://redis:6379/0")
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_max_retries: int = Field(default=2, ge=0, le=10)


@lru_cache
def get_settings() -> Settings:
    return Settings()

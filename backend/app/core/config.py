"""Typed application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "FleetMind AI"
    app_version: str = "0.5.0"
    environment: str = "development"
    demo_mode: bool = True
    llm_provider: str = "demo"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    cognito_client_id: str = ""
    allowed_origins: str = "http://localhost:5173"
    conversations_table: str | None = None
    bots_table: str | None = None
    tasks_table: str | None = None
    max_upload_bytes: int = 2_000_000
    demo_auth_secret: str = ""
    demo_token_ttl_seconds: int = 28_800
    demo_manager_password: str = "FleetMind2026!"
    demo_technician_password: str = "Service2026!"
    demo_viewer_password: str = "View2026!"
    demo_verification_code: str = "482913"

    @field_validator("llm_provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"demo", "bedrock"}:
            raise ValueError("LLM_PROVIDER must be 'demo' or 'bedrock'")
        return normalized

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def cognito_enabled(self) -> bool:
        return bool(self.cognito_client_id.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

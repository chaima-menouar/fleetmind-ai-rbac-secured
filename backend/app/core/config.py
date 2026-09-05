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
    aws_free_tier_only: bool = True
    llm_provider: str = "demo"
    rag_provider: str = "local"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    bedrock_knowledge_base_id: str = ""
    bedrock_guardrail_id: str = ""
    bedrock_guardrail_version: str = "DRAFT"
    rag_top_k: int = 5
    cognito_client_id: str = ""
    cognito_client_secret: str = ""
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

    @field_validator("rag_provider")
    @classmethod
    def validate_rag_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"local", "bedrock_kb"}:
            raise ValueError("RAG_PROVIDER must be 'local' or 'bedrock_kb'")
        return normalized

    @field_validator("rag_top_k")
    @classmethod
    def validate_rag_top_k(cls, value: int) -> int:
        if value < 1 or value > 20:
            raise ValueError("RAG_TOP_K must be between 1 and 20")
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def cognito_enabled(self) -> bool:
        return bool(self.cognito_client_id.strip())

    @property
    def effective_llm_provider(self) -> str:
        """Paid generative inference is disabled while free-tier-only mode is on."""
        return "demo" if self.aws_free_tier_only else self.llm_provider

    @property
    def effective_rag_provider(self) -> str:
        """Cloud vector retrieval is disabled while free-tier-only mode is on."""
        return "local" if self.aws_free_tier_only else self.rag_provider

    @property
    def bedrock_kb_enabled(self) -> bool:
        return (
            not self.aws_free_tier_only
            and self.effective_rag_provider == "bedrock_kb"
            and bool(self.bedrock_knowledge_base_id.strip())
        )

    @property
    def bedrock_guardrail_enabled(self) -> bool:
        return (
            not self.aws_free_tier_only
            and bool(self.bedrock_guardrail_id.strip())
            and bool(self.bedrock_guardrail_version.strip())
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

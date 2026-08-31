from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "NURA Medical API"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./nura_medical.db"

    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30

    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    allow_self_registration: bool = False
    seed_demo_data: bool = False
    demo_clinician_email: str = "reviewer@nuratech.ai"
    demo_clinician_password: str = "ReplaceBeforeRelease123!"
    admin_email: str = "admin@nuratech.ai"
    admin_password: str = "ReplaceBeforeRelease123!"

    ai_provider: Literal["disabled", "openai", "hermes"] = "disabled"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5-mini"
    openai_baa_confirmed: bool = False
    openai_phi_approved: bool = False
    clinical_engine_url: str | None = None
    clinical_engine_token: str | None = None
    clinical_request_timeout_seconds: float = 45.0

    privacy_policy_url: str = "https://nuratech.ai/privacy"
    terms_url: str = "https://nuratech.ai/terms"
    support_url: str = "https://nuratech.ai/support"
    evidence_as_of: str = "2026-08-31"

    max_case_characters: int = Field(default=30_000, ge=1_000, le=100_000)

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str, info):
        # Runtime production validation also occurs in validate_for_startup().
        if not value:
            raise ValueError("APP_JWT_SECRET must not be empty")
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    def validate_for_startup(self) -> None:
        if self.app_env == "production":
            if len(self.jwt_secret) < 32 or "change-me" in self.jwt_secret.lower():
                raise RuntimeError("APP_JWT_SECRET must be a unique 32+ character secret in production")
            if self.seed_demo_data:
                raise RuntimeError("APP_SEED_DEMO_DATA must be false in production")
            if "localhost" in self.allowed_origins or "*" in self.allowed_origins:
                raise RuntimeError("APP_ALLOWED_ORIGINS must contain only approved HTTPS origins")
            if not self.database_url.startswith("postgresql"):
                raise RuntimeError("Production requires PostgreSQL")

        if self.ai_provider == "openai":
            if not self.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
            if not (self.openai_baa_confirmed and self.openai_phi_approved):
                raise RuntimeError(
                    "OpenAI clinical routing remains disabled until BAA and PHI approval flags are true"
                )
        if self.ai_provider == "hermes" and not self.clinical_engine_url:
            raise RuntimeError("CLINICAL_ENGINE_URL is required when AI_PROVIDER=hermes")


@lru_cache
def get_settings() -> Settings:
    return Settings()

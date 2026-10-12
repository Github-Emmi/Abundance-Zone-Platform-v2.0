"""
Core Configuration Module
Handles all environment variables and application settings
Uses Pydantic Settings for validation
"""

from typing import Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable validation"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # ─── Application ─────────────────────────────────────────────────────────
    APP_NAME: str = "Abundance Zone Youth Platform v2.0"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ─── Database (Neon PostgreSQL) ──────────────────────────────────────────
    DATABASE_URL: str  # postgresql+asyncpg://... (pooled connection)
    DATABASE_URL_SYNC: str = ""  # postgresql://... (optional for tests)
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ─── Redis (Upstash Redis) ───────────────────────────────────────────────
    REDIS_URL: str  # rediss://default:password@host:6379
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # ─── JWT ─────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str = ""  # Will use JWT_SECRET_KEY if empty
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── AI Services ─────────────────────────────────────────────────────────
    GOOGLE_API_KEY: str = ""  # Gemini AI (optional for tests)
    OPENROUTER_API_KEY: str | None = None  # Fallback AI
    OPENAI_API_KEY: str = ""  # GPT-4o Vision (optional for tests)

    # ─── File Storage ────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = "test-cloud"
    CLOUDINARY_API_KEY: str = "test-key"
    CLOUDINARY_API_SECRET: str = "test-secret"

    # ─── Email (Resend) ──────────────────────────────────────────────────────
    RESEND_API_KEY: str = "test-resend-key"
    EMAIL_FROM: str = "noreply@abundancezone.org"
    EMAIL_FROM_NAME: str = "Abundance Zone Youth Platform"

    # ─── WhatsApp (Twilio) ───────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_WHATSAPP_FROM: str | None = None

    # ─── Firebase ────────────────────────────────────────────────────────────
    FIREBASE_PROJECT_ID: str = "test-project"
    FIREBASE_PRIVATE_KEY_ID: str = "test-key-id"
    FIREBASE_PRIVATE_KEY: str = "test-private-key"
    FIREBASE_CLIENT_EMAIL: str = "test@test.com"

    # ─── Frontend ────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 2

    # ─── Rate Limiting ───────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    # ─── Cache TTL ───────────────────────────────────────────────────────────
    AI_CACHE_TTL_SECONDS: int = 86400  # 24 hours
    ANALYTICS_CACHE_TTL_SECONDS: int = 2592000  # 30 days

    # ─── Database Seed ───────────────────────────────────────────────────────
    SEED_ADMIN_EMAIL: str = "admin@abundancezone.org"
    SEED_ADMIN_PASSWORD: str = "SecurePassword123!"
    SEED_BRANCH_NAME: str = "Oke-Afa 2 Branch"

    # ─── Error Monitoring ────────────────────────────────────────────────────
    SENTRY_DSN: str | None = None

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Ensure DATABASE_URL uses asyncpg driver for Neon"""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use postgresql+asyncpg:// for async support with Neon"
            )
        return v

    @field_validator("REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND")
    def validate_redis_url(cls, v: str) -> str:
        """Ensure Redis URLs use secure connection for Upstash"""
        if not (v.startswith("redis://") or v.startswith("rediss://")):
            raise ValueError("Redis URLs must start with redis:// or rediss://")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment"""
        return self.ENVIRONMENT == "staging"

    @property
    def is_test(self) -> bool:
        """Check if running in test environment"""
        return self.ENVIRONMENT == "test"


# Global settings instance
settings = Settings()

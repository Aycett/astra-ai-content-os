"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "staging", "production"]


class Settings(BaseSettings):
    """Validated application settings sourced from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Astra AI Content OS")
    app_version: str = Field(default="0.1.0")
    environment: EnvironmentName = Field(default="local")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    postgres_user: str = Field(default="astra")
    postgres_password: str = Field(default="")
    postgres_db: str = Field(default="astra")
    postgres_port: int = Field(default=5432)
    database_url: PostgresDsn | str = Field(default="postgresql://astra@localhost:5432/astra")

    redis_port: int = Field(default=6379)
    redis_url: str = Field(default="redis://localhost:6379/0")

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            raise ValueError("DATABASE_URL must not be empty")
        return value

    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, value: object) -> str:
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError("REDIS_URL must not be empty")
        if not value.startswith("redis://"):
            raise ValueError("REDIS_URL must use the redis:// scheme")
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

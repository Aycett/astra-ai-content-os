"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
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


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

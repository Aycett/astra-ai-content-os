"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "staging", "production"]

_PROJECT_ROOT_MARKERS = ("MASTER_CONTEXT.md", "docker-compose.yml", ".env.example")


def find_project_root() -> Path:
    """Locate the repository root using known marker files."""
    start = Path(__file__).resolve().parent
    for directory in (start, *start.parents):
        if any((directory / marker).exists() for marker in _PROJECT_ROOT_MARKERS):
            return directory
    return Path(__file__).resolve().parents[3]


def resolve_root_env_file() -> Path | None:
    """Return the repository root .env path when the file exists."""
    env_file = find_project_root() / ".env"
    return env_file if env_file.is_file() else None


_ROOT_ENV_FILE = resolve_root_env_file()


class Settings(BaseSettings):
    """Validated application settings sourced from the environment."""

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV_FILE) if _ROOT_ENV_FILE else None,
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

    tavily_api_key: str | None = Field(default=None)
    openai_api_key: str | None = Field(default=None)
    elevenlabs_api_key: str | None = Field(default=None)
    elevenlabs_voice_id: str | None = Field(default=None)

    @field_validator("tavily_api_key", mode="before")
    @classmethod
    def empty_tavily_api_key_as_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def empty_openai_api_key_as_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("elevenlabs_api_key", mode="before")
    @classmethod
    def empty_elevenlabs_api_key_as_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("elevenlabs_voice_id", mode="before")
    @classmethod
    def empty_elevenlabs_voice_id_as_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

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

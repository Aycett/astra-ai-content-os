"""Health check response schema."""

from typing import Literal

from pydantic import BaseModel, Field

HealthStatus = Literal["ok"]


class HealthResponse(BaseModel):
    """Standard health check payload."""

    status: HealthStatus = Field(description="Service health indicator.")
    service: str = Field(description="Application name.")
    version: str = Field(description="Application version.")
    environment: str = Field(description="Active deployment environment.")

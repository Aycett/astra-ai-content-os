"""Agent execution result model."""

from typing import Any

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Standardized output returned by every agent invocation."""

    success: bool = Field(description="Whether the agent completed without failure.")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured payload produced by the agent.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal issues encountered during execution.",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Fatal or blocking errors encountered during execution.",
    )
    execution_time_ms: float = Field(
        ge=0,
        description="Wall-clock execution duration in milliseconds.",
    )

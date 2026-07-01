"""Agent execution context model."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Input context passed to every agent invocation."""

    request_id: UUID = Field(description="Unique identifier for the pipeline request.")
    topic: str | None = Field(
        default=None,
        description="Optional subject or trend topic for the agent to process.",
    )
    language: str = Field(
        default="en",
        description="ISO 639-1 language code for generated content.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional workspace or pipeline metadata for the agent.",
    )

"""LLM gateway data models."""

from typing import Any

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Input payload for LLM generation."""

    prompt: str = Field(min_length=1, description="User prompt for text generation.")
    system_prompt: str | None = Field(
        default=None,
        description="Optional system instruction for the model.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional request context.",
    )


class LLMResponse(BaseModel):
    """Output payload from LLM generation."""

    text: str = Field(description="Generated text content.")
    provider: str = Field(default="mock", description="Provider that served the request.")
    model: str = Field(default="mock", description="Model identifier used for generation.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional response context.",
    )

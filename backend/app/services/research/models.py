"""Research provider data models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ResearchSource(BaseModel):
    """A single research result item from a provider."""

    title: str = Field(description="Title of the source document.")
    url: str = Field(description="Canonical URL of the source.")
    snippet: str = Field(description="Short excerpt or summary of the source.")
    provider: str = Field(description="Name of the provider that returned this source.")
    published_at: datetime | None = Field(
        default=None,
        description="Publication timestamp when known.",
    )
    score: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Trend relevance score between 0 and 1, assigned by trend scoring.",
    )


class ResearchQuery(BaseModel):
    """Input parameters for a research provider search."""

    query: str = Field(min_length=1, description="Search query or topic string.")
    language: str = Field(default="en", description="ISO 639-1 language code.")
    max_results: int = Field(default=5, ge=1, le=50, description="Maximum sources to return.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional context passed to providers.",
    )


class ResearchResult(BaseModel):
    """Aggregated output from a research provider search."""

    query: str = Field(description="The query that was searched.")
    sources: list[ResearchSource] = Field(
        default_factory=list,
        description="Research sources returned by the provider.",
    )
    provider_used: str = Field(description="Name of the provider that produced this result.")
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal issues encountered during the search.",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered during the search.",
    )

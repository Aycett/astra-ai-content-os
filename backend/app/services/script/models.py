"""Script service data models."""

from typing import Any

from pydantic import BaseModel, Field


class ScriptPackage(BaseModel):
    """Structured short-form video script derived from a content brief."""

    title: str = Field(description="Video title for publishing metadata.")
    hook: str = Field(description="Opening hook, max 120 characters.")
    narration: str = Field(description="Full voiceover narration text.")
    on_screen_text: list[str] = Field(description="Short on-screen text overlays.")
    call_to_action: str = Field(description="Closing call to action.")
    estimated_duration_seconds: int = Field(
        ge=30,
        le=60,
        description="Estimated narration duration in seconds.",
    )
    language: str = Field(description="ISO 639-1 language code.")
    source_url: str = Field(description="Reference URL from the content brief.")
    source_title: str = Field(description="Reference title from the content brief.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional script context and brief metadata.",
    )

"""TTS gateway data models."""

from typing import Any

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Input payload for text-to-speech generation."""

    text: str = Field(min_length=1, description="Text to synthesize into speech.")
    language: str = Field(default="en", description="ISO 639-1 language code.")
    voice_profile: str = Field(
        default="default_fast_clear",
        description="Voice style profile for synthesis.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional request context.",
    )


class TTSResponse(BaseModel):
    """Output payload from text-to-speech generation."""

    audio_path: str = Field(description="Reference path to generated audio.")
    provider: str = Field(default="mock", description="Provider that served the request.")
    status: str = Field(default="generated", description="TTS generation status.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional response context.",
    )

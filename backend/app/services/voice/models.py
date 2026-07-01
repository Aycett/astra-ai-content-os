"""Voice service data models."""

from typing import Any

from pydantic import BaseModel, Field


class VoicePackage(BaseModel):
    """Voiceover payload prepared for future text-to-speech generation."""

    narration_text: str = Field(description="Full narration text for TTS input.")
    language: str = Field(description="ISO 639-1 language code.")
    voice_profile: str = Field(
        default="default_fast_clear",
        description="Voice style profile for TTS rendering.",
    )
    estimated_duration_seconds: int = Field(
        ge=30,
        le=60,
        description="Estimated audio duration in seconds.",
    )
    provider: str = Field(
        default="none",
        description="TTS provider identifier; none until configured.",
    )
    status: str = Field(
        default="pending_tts",
        description="Voice generation lifecycle status.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional voice context from the script package.",
    )

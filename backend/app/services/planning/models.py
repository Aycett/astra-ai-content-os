"""Planning service data models."""

from pydantic import BaseModel, Field


class ContentBrief(BaseModel):
    """Structured content plan derived from a trend candidate."""

    title: str = Field(description="Video title for the content piece.")
    topic: str = Field(description="Primary topic or niche subject.")
    angle: str = Field(description="Creative angle for the short-form video.")
    target_platforms: list[str] = Field(
        default=["youtube_shorts", "tiktok", "instagram_reels"],
        description="Platforms this brief targets.",
    )
    duration_seconds: int = Field(
        default=45,
        ge=30,
        le=60,
        description="Target video duration in seconds.",
    )
    language: str = Field(default="en", description="ISO 639-1 language code.")
    source_url: str = Field(description="Reference URL from research.")
    source_title: str = Field(description="Reference title from research.")
    hook_hint: str = Field(description="Short opening hook guidance for the script.")
    tone: str = Field(
        default="informative_fast_paced",
        description="Voice and pacing style for the content.",
    )
    status: str = Field(default="draft", description="Brief lifecycle status.")

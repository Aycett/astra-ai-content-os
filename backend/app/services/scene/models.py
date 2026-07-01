"""Scene service data models."""

from typing import Any

from pydantic import BaseModel, Field


class VideoScene(BaseModel):
    """A single scene in a short-form video plan."""

    scene_number: int = Field(ge=1, description="Scene order starting at 1.")
    purpose: str = Field(description="Scene role in the video structure.")
    narration_segment: str = Field(description="Narration spoken during this scene.")
    on_screen_text: str = Field(description="Text displayed on screen for this scene.")
    visual_prompt: str = Field(description="Deterministic visual generation prompt.")
    duration_seconds: int = Field(ge=1, description="Scene duration in seconds.")
    transition: str = Field(default="cut", description="Transition into the next scene.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional scene context.",
    )


class ScenePlan(BaseModel):
    """Full scene breakdown for a short-form video."""

    title: str = Field(description="Video title from the script package.")
    total_duration_seconds: int = Field(
        ge=30,
        le=60,
        description="Total planned video duration in seconds.",
    )
    scenes: list[VideoScene] = Field(description="Ordered list of video scenes.")
    language: str = Field(description="ISO 639-1 language code.")
    source_url: str = Field(description="Reference URL from the script package.")
    source_title: str = Field(description="Reference title from the script package.")

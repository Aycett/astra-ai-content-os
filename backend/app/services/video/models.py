"""Video service data models."""

from typing import Any

from pydantic import BaseModel, Field


class RenderScene(BaseModel):
    """A single scene entry in a render manifest."""

    scene_number: int = Field(ge=1, description="Scene order starting at 1.")
    purpose: str = Field(description="Scene role in the video structure.")
    narration_segment: str = Field(description="Narration spoken during this scene.")
    on_screen_text: str = Field(description="Text displayed on screen for this scene.")
    visual_prompt: str = Field(description="Visual generation prompt for the scene.")
    duration_seconds: int = Field(ge=1, description="Scene duration in seconds.")
    transition: str = Field(default="cut", description="Transition into the next scene.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Scene and asset metadata for rendering.",
    )


class RenderManifest(BaseModel):
    """Combined instructions for video assembly."""

    title: str = Field(description="Video title for the render job.")
    scenes: list[RenderScene] = Field(description="Ordered scenes with asset references.")
    audio_path: str = Field(description="Path to the narration audio file.")
    total_duration_seconds: int = Field(
        ge=30,
        le=60,
        description="Total planned video duration in seconds.",
    )
    output_format: str = Field(default="mp4", description="Target video container format.")
    aspect_ratio: str = Field(default="9:16", description="Target aspect ratio.")
    resolution: str = Field(default="1080x1920", description="Target output resolution.")
    status: str = Field(default="pending_render", description="Render lifecycle status.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional render context.",
    )

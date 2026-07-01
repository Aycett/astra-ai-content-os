"""Asset service data models."""

from typing import Any

from pydantic import BaseModel, Field


class VisualAssetRequest(BaseModel):
    """Visual asset generation request for a single scene."""

    scene_number: int = Field(ge=1, description="Scene order starting at 1.")
    prompt: str = Field(description="Visual generation prompt for the scene.")
    asset_type: str = Field(default="image", description="Requested visual asset type.")
    aspect_ratio: str = Field(default="9:16", description="Target aspect ratio for the asset.")
    status: str = Field(
        default="pending_generation",
        description="Asset generation lifecycle status.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional asset request context.",
    )


class AssetPackage(BaseModel):
    """Collection of visual asset requests for a scene plan."""

    title: str = Field(description="Video title from the scene plan.")
    assets: list[VisualAssetRequest] = Field(description="Visual asset requests per scene.")
    provider: str = Field(
        default="none",
        description="Visual provider identifier; none until configured.",
    )
    status: str = Field(
        default="pending_assets",
        description="Asset package lifecycle status.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional asset package context.",
    )

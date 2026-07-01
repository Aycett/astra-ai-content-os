"""Deterministic asset package generation from scene plans."""

from typing import Any

from app.services.assets.models import AssetPackage, VisualAssetRequest
from app.services.scene.models import ScenePlan


def _to_scene_plan(scene_plan: ScenePlan | dict[str, Any]) -> ScenePlan:
    if isinstance(scene_plan, ScenePlan):
        return scene_plan
    return ScenePlan.model_validate(scene_plan)


def generate_asset_package(scene_plan: ScenePlan | dict[str, Any]) -> AssetPackage:
    """Convert a scene plan into a visual asset package."""
    normalized = _to_scene_plan(scene_plan)

    assets = [
        VisualAssetRequest(
            scene_number=scene.scene_number,
            prompt=scene.visual_prompt,
            metadata={
                "purpose": scene.purpose,
                "on_screen_text": scene.on_screen_text,
                "duration_seconds": scene.duration_seconds,
                **scene.metadata,
            },
        )
        for scene in normalized.scenes
    ]

    return AssetPackage(
        title=normalized.title,
        assets=assets,
        metadata={
            "total_duration_seconds": normalized.total_duration_seconds,
            "language": normalized.language,
            "source_url": normalized.source_url,
            "source_title": normalized.source_title,
            "scene_count": len(assets),
        },
    )

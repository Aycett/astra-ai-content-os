"""Deterministic render manifest generation."""

from typing import Any

from app.services.assets.models import AssetPackage
from app.services.scene.models import ScenePlan
from app.services.tts.models import TTSResponse
from app.services.video.models import RenderManifest, RenderScene


def _to_scene_plan(scene_plan: ScenePlan | dict[str, Any]) -> ScenePlan:
    if isinstance(scene_plan, ScenePlan):
        return scene_plan
    return ScenePlan.model_validate(scene_plan)


def _to_asset_package(assets: AssetPackage | dict[str, Any]) -> AssetPackage:
    if isinstance(assets, AssetPackage):
        return assets
    return AssetPackage.model_validate(assets)


def _to_tts_response(tts: TTSResponse | dict[str, Any]) -> TTSResponse:
    if isinstance(tts, TTSResponse):
        return tts
    return TTSResponse.model_validate(tts)


def generate_render_manifest(
    scene_plan: ScenePlan | dict[str, Any],
    assets: AssetPackage | dict[str, Any],
    tts: TTSResponse | dict[str, Any],
) -> RenderManifest:
    """Combine scene plan, assets, and TTS into a render manifest."""
    normalized_plan = _to_scene_plan(scene_plan)
    normalized_assets = _to_asset_package(assets)
    normalized_tts = _to_tts_response(tts)

    assets_by_scene = {asset.scene_number: asset for asset in normalized_assets.assets}

    render_scenes: list[RenderScene] = []
    for scene in normalized_plan.scenes:
        asset = assets_by_scene.get(scene.scene_number)
        asset_metadata: dict[str, Any] = {}
        if asset is not None:
            asset_metadata = {
                **asset.metadata,
                "asset_type": asset.asset_type,
                "asset_status": asset.status,
                "asset_aspect_ratio": asset.aspect_ratio,
            }

        render_scenes.append(
            RenderScene(
                scene_number=scene.scene_number,
                purpose=scene.purpose,
                narration_segment=scene.narration_segment,
                on_screen_text=scene.on_screen_text,
                visual_prompt=scene.visual_prompt,
                duration_seconds=scene.duration_seconds,
                transition=scene.transition,
                metadata={**scene.metadata, **asset_metadata},
            )
        )

    return RenderManifest(
        title=normalized_plan.title,
        scenes=render_scenes,
        audio_path=normalized_tts.audio_path,
        total_duration_seconds=normalized_plan.total_duration_seconds,
        metadata={
            "language": normalized_plan.language,
            "source_url": normalized_plan.source_url,
            "source_title": normalized_plan.source_title,
            "tts_provider": normalized_tts.provider,
            "tts_status": normalized_tts.status,
            "assets_provider": normalized_assets.provider,
            "assets_status": normalized_assets.status,
            "scene_count": len(render_scenes),
        },
    )

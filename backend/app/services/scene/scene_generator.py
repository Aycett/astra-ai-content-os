"""Deterministic scene plan generation from script packages."""

from typing import Any

from app.services.scene.models import ScenePlan, VideoScene
from app.services.script.models import ScriptPackage


def _to_script_package(script: ScriptPackage | dict[str, Any]) -> ScriptPackage:
    if isinstance(script, ScriptPackage):
        return script
    return ScriptPackage.model_validate(script)


def _split_duration(total_seconds: int, scene_count: int) -> list[int]:
    base = total_seconds // scene_count
    remainder = total_seconds % scene_count
    return [base + (1 if index < remainder else 0) for index in range(scene_count)]


def _split_narration(narration: str, parts: int) -> list[str]:
    if parts <= 0:
        return []

    words = narration.split()
    if not words:
        return [""] * parts

    chunk_size = max(1, len(words) // parts)
    segments: list[str] = []
    start = 0

    for index in range(parts):
        if index == parts - 1:
            segment_words = words[start:]
        else:
            segment_words = words[start : start + chunk_size]
            start += chunk_size
        segments.append(" ".join(segment_words))

    return segments


def _visual_prompt(scene_text: str, title: str) -> str:
    return (
        f"Vertical 9:16 original visual for '{title}': {scene_text}. "
        "Modern, clean composition, no copyrighted characters, no text overlay."
    )


def generate_scene_plan(script: ScriptPackage | dict[str, Any]) -> ScenePlan:
    """Convert a script package into an ordered scene plan."""
    normalized = _to_script_package(script)

    middle_texts = normalized.on_screen_text or ["Key insight"]
    narration_segments = _split_narration(normalized.narration, len(middle_texts))
    scene_count = 1 + len(middle_texts) + 1
    durations = _split_duration(normalized.estimated_duration_seconds, scene_count)

    scenes: list[VideoScene] = []

    scenes.append(
        VideoScene(
            scene_number=1,
            purpose="hook",
            narration_segment=normalized.hook,
            on_screen_text=normalized.hook,
            visual_prompt=_visual_prompt(normalized.hook, normalized.title),
            duration_seconds=durations[0],
            metadata={"segment": "opening"},
        )
    )

    for index, overlay in enumerate(middle_texts):
        narration_segment = narration_segments[index] if index < len(narration_segments) else overlay
        scenes.append(
            VideoScene(
                scene_number=index + 2,
                purpose="body",
                narration_segment=narration_segment,
                on_screen_text=overlay,
                visual_prompt=_visual_prompt(overlay, normalized.title),
                duration_seconds=durations[index + 1],
                metadata={"segment": "middle", "overlay_index": index},
            )
        )

    final_index = scene_count - 1
    scenes.append(
        VideoScene(
            scene_number=scene_count,
            purpose="call_to_action",
            narration_segment=normalized.call_to_action,
            on_screen_text=normalized.call_to_action,
            visual_prompt=_visual_prompt(normalized.call_to_action, normalized.title),
            duration_seconds=durations[final_index],
            metadata={"segment": "closing"},
        )
    )

    return ScenePlan(
        title=normalized.title,
        total_duration_seconds=normalized.estimated_duration_seconds,
        scenes=scenes,
        language=normalized.language,
        source_url=normalized.source_url,
        source_title=normalized.source_title,
    )

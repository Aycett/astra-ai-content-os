"""Deterministic voice package generation from script packages."""

from typing import Any

from app.services.script.models import ScriptPackage
from app.services.voice.models import VoicePackage


def _to_script_package(script: ScriptPackage | dict[str, Any]) -> ScriptPackage:
    if isinstance(script, ScriptPackage):
        return script
    return ScriptPackage.model_validate(script)


def generate_voice_package(script: ScriptPackage | dict[str, Any]) -> VoicePackage:
    """Convert a script package into a voice package for future TTS."""
    normalized = _to_script_package(script)

    return VoicePackage(
        narration_text=normalized.narration,
        language=normalized.language,
        estimated_duration_seconds=normalized.estimated_duration_seconds,
        metadata={
            "title": normalized.title,
            "hook": normalized.hook,
            "source_url": normalized.source_url,
            "source_title": normalized.source_title,
            **normalized.metadata,
        },
    )

"""Deterministic script generation from content briefs."""

from typing import Any

from app.services.planning.models import ContentBrief
from app.services.script.models import ScriptPackage

_MAX_HOOK_LENGTH = 120
_MIN_NARRATION_WORDS = 80
_MAX_NARRATION_WORDS = 130


def _to_content_brief(brief: ContentBrief | dict[str, Any]) -> ContentBrief:
    if isinstance(brief, ContentBrief):
        return brief
    return ContentBrief.model_validate(brief)


def _build_hook(brief: ContentBrief) -> str:
    hook = brief.hook_hint.strip() or f"Stop scrolling — {brief.title}"
    if len(hook) > _MAX_HOOK_LENGTH:
        hook = f"{hook[: _MAX_HOOK_LENGTH - 3].rstrip()}..."
    return hook


def _build_narration(brief: ContentBrief) -> str:
    sentences = [
        f"If you care about {brief.topic}, give me the next {brief.duration_seconds} seconds.",
        f"Most people talk about {brief.topic}, but miss the point that actually drives views.",
        brief.angle,
        (
            f"Research from {brief.source_title} points to a simple opportunity: "
            f"one clear idea, delivered fast, with original value."
        ),
        (
            "The winning format is vertical, under sixty seconds, and built for "
            "YouTube Shorts, TikTok, and Instagram Reels."
        ),
        (
            f"Use a strong hook, one core insight about {brief.topic}, "
            "and a direct call to action at the end."
        ),
        (
            "Do not repost clips or recycle copyrighted footage. "
            "Original narration plus generated visuals is the sustainable path."
        ),
        (
            f"Your angle: stay {brief.tone.replace('_', ' ')}, "
            "cut filler, and land the payoff before attention drops."
        ),
        (
            f"That is how you turn {brief.topic} into a repeatable short-video series "
            "without guessing what to say next."
        ),
        "Save this breakdown and use it as your script outline for the next publish.",
    ]

    words: list[str] = []
    for sentence in sentences:
        words.extend(sentence.split())
        if len(words) >= _MIN_NARRATION_WORDS:
            break

    padding = (
        "Focus on one actionable takeaway, keep pacing tight, "
        "and end with a clear next step for viewers to follow."
    ).split()

    while len(words) < _MIN_NARRATION_WORDS:
        words.extend(padding)

    if len(words) > _MAX_NARRATION_WORDS:
        words = words[:_MAX_NARRATION_WORDS]

    narration = " ".join(words)
    if not narration.endswith("."):
        narration = f"{narration}."
    return narration


def _build_on_screen_text(brief: ContentBrief) -> list[str]:
    return [
        brief.topic[:40],
        "Key insight",
        "Why it matters",
        f"{brief.duration_seconds}s breakdown",
        "Save this",
    ]


def _build_call_to_action(brief: ContentBrief) -> str:
    return f"Follow for more {brief.topic} breakdowns."


def generate_script(brief: ContentBrief | dict[str, Any]) -> ScriptPackage:
    """Convert a content brief into a structured script package."""
    normalized = _to_content_brief(brief)

    return ScriptPackage(
        title=normalized.title,
        hook=_build_hook(normalized),
        narration=_build_narration(normalized),
        on_screen_text=_build_on_screen_text(normalized),
        call_to_action=_build_call_to_action(normalized),
        estimated_duration_seconds=normalized.duration_seconds,
        language=normalized.language,
        source_url=normalized.source_url,
        source_title=normalized.source_title,
        metadata={
            "topic": normalized.topic,
            "tone": normalized.tone,
            "target_platforms": normalized.target_platforms,
            "brief_status": normalized.status,
        },
    )

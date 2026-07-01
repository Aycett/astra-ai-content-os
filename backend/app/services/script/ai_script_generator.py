"""AI-ready script generation using the LLM gateway."""

from typing import Any

from app.core.config import get_settings
from app.services.llm import LLMRequest, MockLLMProvider, OpenAIProvider
from app.services.llm.models import LLMResponse
from app.services.planning.models import ContentBrief
from app.services.script.models import ScriptPackage

_MAX_HOOK_LENGTH = 120
_MIN_NARRATION_WORDS = 80
_MAX_NARRATION_WORDS = 130


def _to_content_brief(brief: ContentBrief | dict[str, Any]) -> ContentBrief:
    if isinstance(brief, ContentBrief):
        return brief
    return ContentBrief.model_validate(brief)


def _build_prompt(brief: ContentBrief) -> str:
    return (
        "Generate a short-form vertical video script.\n"
        f"Title: {brief.title}\n"
        f"Topic: {brief.topic}\n"
        f"Angle: {brief.angle}\n"
        f"Tone: {brief.tone}\n"
        f"Duration: {brief.duration_seconds} seconds"
    )


def _build_system_prompt(brief: ContentBrief) -> str:
    return (
        "You write original short-form video scripts for YouTube Shorts, TikTok, "
        f"and Instagram Reels. Use a {brief.tone.replace('_', ' ')} delivery."
    )


def _build_hook(brief: ContentBrief) -> str:
    hook = brief.hook_hint.strip() or f"Stop scrolling — {brief.title}"
    if len(hook) > _MAX_HOOK_LENGTH:
        hook = f"{hook[: _MAX_HOOK_LENGTH - 3].rstrip()}..."
    return hook


def _build_narration(brief: ContentBrief, llm_text: str) -> str:
    seed = f"{brief.topic} {brief.angle} {llm_text}"
    words = seed.split()

    padding = (
        f"Deliver this in {brief.duration_seconds} seconds with a {brief.tone.replace('_', ' ')} "
        f"style. Focus on {brief.topic}, keep it original, and land one clear takeaway."
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
        brief.title[:40],
        f"{brief.duration_seconds}s breakdown",
        "Save this",
    ]


def _build_call_to_action(brief: ContentBrief) -> str:
    return f"Follow for more {brief.topic} breakdowns."


def _generate_llm_response(
    request: LLMRequest,
    llm_provider: MockLLMProvider | None = None,
) -> LLMResponse:
    if llm_provider is not None:
        return llm_provider.generate(request)

    if get_settings().openai_api_key:
        try:
            return OpenAIProvider().generate(request)
        except Exception:
            return MockLLMProvider().generate(request)

    return MockLLMProvider().generate(request)


def generate_ai_script(
    brief: ContentBrief | dict[str, Any],
    llm_provider: MockLLMProvider | None = None,
) -> ScriptPackage:
    """Convert a content brief into a script package via the LLM gateway."""
    normalized = _to_content_brief(brief)

    llm_response = _generate_llm_response(
        LLMRequest(
            prompt=_build_prompt(normalized),
            system_prompt=_build_system_prompt(normalized),
            metadata={
                "topic": normalized.topic,
                "duration_seconds": normalized.duration_seconds,
            },
        ),
        llm_provider=llm_provider,
    )

    return ScriptPackage(
        title=normalized.title,
        hook=_build_hook(normalized),
        narration=_build_narration(normalized, llm_response.text),
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
            "generator": "ai_openai" if llm_response.provider == "openai" else "ai_mock",
            "llm_provider": llm_response.provider,
            "llm_model": llm_response.model,
        },
    )

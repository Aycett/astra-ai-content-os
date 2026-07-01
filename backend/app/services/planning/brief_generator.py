"""Deterministic content brief generation from trend candidates."""

from typing import Any

from app.services.planning.models import ContentBrief
from app.services.research.models import TrendCandidate

_DURATION_BY_RANK = (45, 50, 40, 55, 35)
_MAX_HOOK_LENGTH = 120


def _to_trend_candidate(candidate: TrendCandidate | dict[str, Any]) -> TrendCandidate:
    if isinstance(candidate, TrendCandidate):
        return candidate
    return TrendCandidate.model_validate(candidate)


def _duration_for_rank(rank: int) -> int:
    return max(30, min(60, _DURATION_BY_RANK[rank % len(_DURATION_BY_RANK)]))


def _hook_hint(candidate: TrendCandidate, topic: str, duration: int) -> str:
    hook = (
        f"Open with a bold claim about {topic}, then prove it in {duration} seconds "
        f"using the angle: {candidate.title}"
    )
    if len(hook) > _MAX_HOOK_LENGTH:
        hook = f"{hook[: _MAX_HOOK_LENGTH - 3].rstrip()}..."
    return hook


def generate_briefs(
    candidates: list[TrendCandidate | dict[str, Any]],
    topic: str,
    limit: int = 3,
) -> list[ContentBrief]:
    """Convert top-scored trend candidates into content briefs."""
    normalized = [_to_trend_candidate(candidate) for candidate in candidates]
    ranked = sorted(normalized, key=lambda candidate: candidate.score, reverse=True)

    briefs: list[ContentBrief] = []
    for rank, candidate in enumerate(ranked[:limit]):
        duration = _duration_for_rank(rank)
        briefs.append(
            ContentBrief(
                title=candidate.title,
                topic=topic,
                angle=candidate.angle,
                duration_seconds=duration,
                source_url=candidate.source_url,
                source_title=candidate.source_title,
                hook_hint=_hook_hint(candidate, topic, duration),
            )
        )

    return briefs

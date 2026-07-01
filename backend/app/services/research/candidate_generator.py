"""Deterministic trend candidate generation from research sources."""

from app.services.research.models import ResearchSource, TrendCandidate

_MAX_TITLE_LENGTH = 80


def _video_title(source: ResearchSource, query: str) -> str:
    title = source.title.strip()
    if query.lower() not in title.lower():
        title = f"{query}: {title}"
    if len(title) > _MAX_TITLE_LENGTH:
        title = f"{title[: _MAX_TITLE_LENGTH - 3].rstrip()}..."
    return title


def _angle(source: ResearchSource, query: str) -> str:
    snippet = source.snippet.strip()
    if snippet:
        preview = snippet if len(snippet) <= 120 else f"{snippet[:117].rstrip()}..."
        return (
            f"Create a 30-60 second vertical video about {query} "
            f"highlighting: {preview}"
        )
    return (
        f"Create a 30-60 second vertical video explaining {query} "
        f"based on insights from '{source.title}'."
    )


def _reasoning(source: ResearchSource, query: str, score: float) -> str:
    return (
        f"Ranked {score:.2f} for '{query}' with strong short-video fit; "
        f"source matched query relevance via title and snippet signals."
    )


def generate_candidates(
    sources: list[ResearchSource],
    query: str,
    limit: int = 5,
) -> list[TrendCandidate]:
    """Build trend candidates from the highest-scored research sources."""
    ranked = sorted(sources, key=lambda source: source.score or 0.0, reverse=True)

    return [
        TrendCandidate(
            title=_video_title(source, query),
            angle=_angle(source, query),
            source_url=source.url,
            source_title=source.title,
            score=source.score if source.score is not None else 0.0,
            reasoning=_reasoning(source, query, source.score or 0.0),
        )
        for source in ranked[:limit]
    ]

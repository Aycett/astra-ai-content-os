"""Deterministic trend relevance scoring for research sources."""

from app.services.research.models import ResearchSource

_BASE_SCORE = 0.1
_URL_SCORE = 0.2
_TITLE_MATCH_SCORE = 0.4
_SNIPPET_MATCH_SCORE = 0.3
_MAX_SCORE = 1.0


def _query_words(query: str) -> list[str]:
    return [word.lower() for word in query.split() if word.strip()]


def _contains_query_word(text: str, words: list[str]) -> bool:
    normalized = text.lower()
    return any(word in normalized for word in words)


def _score_source(source: ResearchSource, words: list[str]) -> float:
    score = _BASE_SCORE

    if source.url.strip():
        score += _URL_SCORE

    if words and _contains_query_word(source.title, words):
        score += _TITLE_MATCH_SCORE

    if words and _contains_query_word(source.snippet, words):
        score += _SNIPPET_MATCH_SCORE

    return min(score, _MAX_SCORE)


def score_sources(sources: list[ResearchSource], query: str) -> list[ResearchSource]:
    """Score and sort research sources by deterministic trend relevance rules."""
    words = _query_words(query)

    scored = [
        source.model_copy(update={"score": _score_source(source, words)})
        for source in sources
    ]
    scored.sort(key=lambda source: source.score or 0.0, reverse=True)
    return scored

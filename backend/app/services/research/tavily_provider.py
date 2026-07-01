"""Tavily research provider."""

from datetime import datetime
from typing import Any

from tavily import TavilyClient

from app.services.research.base_provider import BaseResearchProvider
from app.services.research.models import ResearchQuery, ResearchResult, ResearchSource


class TavilyProvider(BaseResearchProvider):
    """Research provider backed by the Tavily Search API."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = TavilyClient(api_key=api_key)

    @property
    def name(self) -> str:
        return "tavily"

    def search(self, query: ResearchQuery) -> ResearchResult:
        try:
            response = self._client.search(
                query=query.query,
                max_results=query.max_results,
            )
        except Exception as exc:
            return ResearchResult(
                query=query.query,
                sources=[],
                provider_used=self.name,
                errors=[f"Tavily search failed: {exc}"],
            )

        raw_results = response.get("results", [])
        if not isinstance(raw_results, list) or not raw_results:
            return ResearchResult(
                query=query.query,
                sources=[],
                provider_used=self.name,
                errors=["Tavily returned no results."],
            )

        sources = [
            source
            for item in raw_results
            if isinstance(item, dict)
            for source in [self._to_research_source(item)]
            if source is not None
        ]

        if not sources:
            return ResearchResult(
                query=query.query,
                sources=[],
                provider_used=self.name,
                errors=["Tavily returned no usable results."],
            )

        return ResearchResult(
            query=query.query,
            sources=sources,
            provider_used=self.name,
        )

    def _to_research_source(self, item: dict[str, Any]) -> ResearchSource | None:
        title = item.get("title")
        url = item.get("url")
        if not title or not url:
            return None

        snippet = item.get("content") or item.get("snippet") or ""
        score = item.get("score")
        normalized_score = float(score) if isinstance(score, (int, float)) else None

        return ResearchSource(
            title=str(title),
            url=str(url),
            snippet=str(snippet),
            provider=self.name,
            published_at=self._parse_published_at(item.get("published_date")),
            score=normalized_score,
        )

    @staticmethod
    def _parse_published_at(value: object) -> datetime | None:
        if not isinstance(value, str) or not value.strip():
            return None

        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"

        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

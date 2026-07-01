"""Orchestrates research providers with ordered fallback."""

from app.services.research.base_provider import BaseResearchProvider
from app.services.research.models import ResearchQuery, ResearchResult


class ResearchProviderManager:
    """Try configured research providers in order until one succeeds."""

    def __init__(self, providers: list[BaseResearchProvider]) -> None:
        if not providers:
            raise ValueError("At least one research provider is required.")
        self._providers = providers

    def search(self, query: ResearchQuery) -> ResearchResult:
        """Return the first successful provider result, or an error result if all fail."""
        warnings: list[str] = []
        errors: list[str] = []

        for provider in self._providers:
            try:
                result = provider.search(query)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")
                continue

            if result.sources:
                return ResearchResult(
                    query=query.query,
                    sources=result.sources,
                    provider_used=result.provider_used,
                    warnings=[*warnings, *result.warnings],
                    errors=result.errors,
                )

            warnings.extend(result.warnings)
            if result.errors:
                errors.extend(result.errors)
            else:
                errors.append(f"{provider.name}: returned no sources")

        return ResearchResult(
            query=query.query,
            sources=[],
            provider_used="none",
            warnings=warnings,
            errors=errors or ["All research providers failed."],
        )

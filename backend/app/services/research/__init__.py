"""Research service — provider framework for trend and topic discovery."""

from app.services.research.base_provider import BaseResearchProvider
from app.services.research.mock_provider import MockResearchProvider
from app.services.research.models import (
    ResearchQuery,
    ResearchResult,
    ResearchSource,
)
from app.services.research.provider_manager import ResearchProviderManager
from app.services.research.tavily_provider import TavilyProvider

__all__ = [
    "BaseResearchProvider",
    "MockResearchProvider",
    "ResearchProviderManager",
    "ResearchQuery",
    "ResearchResult",
    "ResearchSource",
    "TavilyProvider",
]

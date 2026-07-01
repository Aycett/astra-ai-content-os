"""Abstract base class for research providers."""

from abc import ABC, abstractmethod

from app.services.research.models import ResearchQuery, ResearchResult


class BaseResearchProvider(ABC):
    """Contract for all research source providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable provider identifier used in logs and results."""

    @abstractmethod
    def search(self, query: ResearchQuery) -> ResearchResult:
        """Execute a research search and return structured results."""

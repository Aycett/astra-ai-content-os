"""Research agent — discovers trend signals and topic candidates."""

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent
from app.core.config import get_settings
from app.services.research.base_provider import BaseResearchProvider
from app.services.research.mock_provider import MockResearchProvider
from app.services.research.models import ResearchQuery
from app.services.research.provider_manager import ResearchProviderManager
from app.services.research.scoring import score_sources
from app.services.research.tavily_provider import TavilyProvider


def _default_provider_manager() -> ResearchProviderManager:
    settings = get_settings()
    providers: list[BaseResearchProvider] = []

    if settings.tavily_api_key:
        providers.append(TavilyProvider(api_key=settings.tavily_api_key))

    providers.append(MockResearchProvider())
    return ResearchProviderManager(providers=providers)


class ResearchAgent(BaseAgent):
    """Runs research searches through configured providers."""

    def __init__(
        self,
        provider_manager: ResearchProviderManager | None = None,
    ) -> None:
        self._provider_manager = provider_manager or _default_provider_manager()

    @property
    def name(self) -> str:
        return "research"

    @property
    def version(self) -> str:
        return "0.2.0"

    def _execute(self, context: AgentContext) -> AgentResult:
        if not context.topic:
            return AgentResult(
                success=False,
                errors=["Topic is required for research."],
                execution_time_ms=0.0,
            )

        research_query = ResearchQuery(
            query=context.topic,
            language=context.language,
            metadata=context.metadata,
        )
        research_result = self._provider_manager.search(research_query)

        if research_result.sources:
            scored_sources = score_sources(research_result.sources, research_query.query)
            research_result = research_result.model_copy(update={"sources": scored_sources})

        if not research_result.sources:
            return AgentResult(
                success=False,
                data={"research": research_result.model_dump(mode="json")},
                warnings=research_result.warnings,
                errors=research_result.errors,
                execution_time_ms=0.0,
            )

        return AgentResult(
            success=True,
            data={"research": research_result.model_dump(mode="json")},
            warnings=research_result.warnings,
            errors=research_result.errors,
            execution_time_ms=0.0,
        )

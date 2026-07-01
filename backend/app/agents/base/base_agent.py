"""Abstract base class for all Astra agents."""

from abc import ABC, abstractmethod
import time

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult


class BaseAgent(ABC):
    """Contract that every domain agent must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable agent identifier used in logs and orchestration."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version of the agent implementation."""

    @abstractmethod
    def _execute(self, context: AgentContext) -> AgentResult:
        """Run agent-specific logic and return a result without timing metadata."""

    def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent and attach execution timing to the result."""
        started_at = time.perf_counter()
        result = self._execute(context)
        elapsed_ms = (time.perf_counter() - started_at) * 1000

        return result.model_copy(update={"execution_time_ms": elapsed_ms})

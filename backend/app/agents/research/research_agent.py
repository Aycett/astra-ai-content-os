"""Research agent — discovers trend signals and topic candidates."""

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """Placeholder research agent pending trend discovery implementation."""

    @property
    def name(self) -> str:
        return "research"

    @property
    def version(self) -> str:
        return "0.1.0"

    def _execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            data={
                "agent": self.name,
                "request_id": str(context.request_id),
                "status": "placeholder",
            },
            warnings=["ResearchAgent has not been implemented yet."],
            execution_time_ms=0.0,
        )

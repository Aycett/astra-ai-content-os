"""Script agent — generates script packages from content briefs."""

from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent
from app.services.script.ai_script_generator import generate_ai_script


class ScriptAgent(BaseAgent):
    """Generates a ScriptPackage from a content brief in agent context."""

    @property
    def name(self) -> str:
        return "script"

    @property
    def version(self) -> str:
        return "0.1.0"

    def _execute(self, context: AgentContext) -> AgentResult:
        brief: Any = context.metadata.get("brief")
        if brief is None:
            return AgentResult(
                success=False,
                errors=["Content brief is required in context.metadata['brief']."],
                execution_time_ms=0.0,
            )

        script_package = generate_ai_script(brief)

        return AgentResult(
            success=True,
            data={"script": script_package.model_dump(mode="json")},
            execution_time_ms=0.0,
        )

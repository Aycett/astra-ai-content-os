"""Voice agent — generates voice packages from script packages."""

from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent
from app.services.voice.voice_package_generator import generate_voice_package


class VoiceAgent(BaseAgent):
    """Generates a VoicePackage from a script package in agent context."""

    @property
    def name(self) -> str:
        return "voice"

    @property
    def version(self) -> str:
        return "0.1.0"

    def _execute(self, context: AgentContext) -> AgentResult:
        script: Any = context.metadata.get("script")
        if script is None:
            return AgentResult(
                success=False,
                errors=["Script package is required in context.metadata['script']."],
                execution_time_ms=0.0,
            )

        voice_package = generate_voice_package(script)

        return AgentResult(
            success=True,
            data={"voice": voice_package.model_dump(mode="json")},
            execution_time_ms=0.0,
        )

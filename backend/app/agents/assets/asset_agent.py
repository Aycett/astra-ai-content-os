"""Asset agent — generates visual asset packages from scene plans."""

from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent
from app.services.assets import MockImageProvider, generate_asset_package


class AssetAgent(BaseAgent):
    """Generates an asset package from a scene plan in agent context."""

    def __init__(self, image_provider: MockImageProvider | None = None) -> None:
        self._image_provider = image_provider or MockImageProvider()

    @property
    def name(self) -> str:
        return "assets"

    @property
    def version(self) -> str:
        return "0.1.0"

    def _execute(self, context: AgentContext) -> AgentResult:
        scene_plan: Any = context.metadata.get("scene_plan")
        if scene_plan is None:
            return AgentResult(
                success=False,
                errors=["Scene plan is required in context.metadata['scene_plan']."],
                execution_time_ms=0.0,
            )

        asset_package = generate_asset_package(scene_plan)
        asset_package = self._image_provider.generate(asset_package)

        return AgentResult(
            success=True,
            data={"assets": asset_package.model_dump(mode="json")},
            execution_time_ms=0.0,
        )

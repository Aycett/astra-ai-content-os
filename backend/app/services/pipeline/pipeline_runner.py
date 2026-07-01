"""End-to-end mock content pipeline."""

from typing import Any
from uuid import uuid4

from app.agents import (
    AgentContext,
    AssetAgent,
    ResearchAgent,
    ScriptAgent,
    TTSAgent,
    VoiceAgent,
)
from app.services.planning import generate_briefs
from app.services.scene import generate_scene_plan
from app.services.video import MockVideoRenderer, generate_render_manifest


def _require_success(step: str, result: Any) -> None:
    if not result.success:
        errors = ", ".join(result.errors) or "Unknown error"
        raise RuntimeError(f"{step} failed: {errors}")


def run_mock_pipeline(topic: str) -> dict[str, Any]:
    """Run the full mock content pipeline from topic to rendered video."""
    request_id = uuid4()

    research_result = ResearchAgent().run(
        AgentContext(request_id=request_id, topic=topic, language="en")
    )
    _require_success("ResearchAgent", research_result)

    briefs = generate_briefs(research_result.data["candidates"], topic=topic, limit=1)
    if not briefs:
        raise RuntimeError("generate_briefs failed: no briefs produced")

    brief = briefs[0].model_dump(mode="json")

    script_result = ScriptAgent().run(
        AgentContext(request_id=request_id, metadata={"brief": brief})
    )
    _require_success("ScriptAgent", script_result)
    script = script_result.data["script"]

    voice_result = VoiceAgent().run(
        AgentContext(request_id=request_id, metadata={"script": script})
    )
    _require_success("VoiceAgent", voice_result)
    voice = voice_result.data["voice"]

    tts_result = TTSAgent().run(
        AgentContext(request_id=request_id, metadata={"voice": voice})
    )
    _require_success("TTSAgent", tts_result)
    tts = tts_result.data["tts"]

    scene_plan = generate_scene_plan(script)
    scene_plan_data = scene_plan.model_dump(mode="json")

    assets_result = AssetAgent().run(
        AgentContext(request_id=request_id, metadata={"scene_plan": scene_plan_data})
    )
    _require_success("AssetAgent", assets_result)
    assets = assets_result.data["assets"]

    render_manifest = generate_render_manifest(scene_plan_data, assets, tts)
    video = MockVideoRenderer().render(render_manifest)

    return {
        "topic": topic,
        "research": research_result.data["research"],
        "brief": brief,
        "script": script,
        "voice": voice,
        "tts": tts,
        "scene_plan": scene_plan_data,
        "assets": assets,
        "render_manifest": render_manifest.model_dump(mode="json"),
        "video": video,
        "status": "completed",
    }

"""TTS agent — generates audio references from voice packages."""

from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent
from app.core.config import get_settings
from app.services.tts import ElevenLabsProvider, MockTTSProvider, TTSRequest
from app.services.tts.models import TTSResponse
from app.services.voice.models import VoicePackage


class TTSAgent(BaseAgent):
    """Generates a TTS response from a voice package in agent context."""

    def __init__(self, tts_provider: MockTTSProvider | None = None) -> None:
        self._tts_provider = tts_provider

    @property
    def name(self) -> str:
        return "tts"

    @property
    def version(self) -> str:
        return "0.1.0"

    def _generate_tts_response(self, request: TTSRequest) -> TTSResponse:
        if self._tts_provider is not None:
            return self._tts_provider.generate(request)

        if get_settings().elevenlabs_api_key:
            try:
                return ElevenLabsProvider().generate(request)
            except Exception:
                return MockTTSProvider().generate(request)

        return MockTTSProvider().generate(request)

    def _execute(self, context: AgentContext) -> AgentResult:
        voice: Any = context.metadata.get("voice")
        if voice is None:
            return AgentResult(
                success=False,
                errors=["Voice package is required in context.metadata['voice']."],
                execution_time_ms=0.0,
            )

        voice_package = (
            voice if isinstance(voice, VoicePackage) else VoicePackage.model_validate(voice)
        )
        tts_request = TTSRequest(
            text=voice_package.narration_text,
            language=voice_package.language,
            voice_profile=voice_package.voice_profile,
            metadata=voice_package.metadata,
        )
        tts_response = self._generate_tts_response(tts_request)

        return AgentResult(
            success=True,
            data={"tts": tts_response.model_dump(mode="json")},
            execution_time_ms=0.0,
        )

"""TTS gateway — models and providers."""

from app.services.tts.mock_tts_provider import MockTTSProvider
from app.services.tts.models import TTSRequest, TTSResponse

__all__ = ["MockTTSProvider", "TTSRequest", "TTSResponse"]

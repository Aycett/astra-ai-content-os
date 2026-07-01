"""Mock TTS provider for local development and testing."""

import hashlib

from app.services.tts.models import TTSRequest, TTSResponse


class MockTTSProvider:
    """Returns a fake audio path without generating real audio."""

    def generate(self, request: TTSRequest) -> TTSResponse:
        digest = hashlib.sha256(
            f"{request.text}|{request.language}|{request.voice_profile}".encode()
        ).hexdigest()[:16]

        return TTSResponse(
            audio_path=f"mock://audio/{digest}.mp3",
            metadata={
                "request_metadata": request.metadata,
                "text_length": len(request.text),
                "voice_profile": request.voice_profile,
                "language": request.language,
            },
        )

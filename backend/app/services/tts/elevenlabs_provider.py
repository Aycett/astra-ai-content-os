"""ElevenLabs TTS provider."""

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

from app.core.config import get_settings
from app.services.tts.models import TTSRequest, TTSResponse

_DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
_MODEL_ID = "eleven_multilingual_v2"


class ElevenLabsConfigurationError(RuntimeError):
    """Raised when ElevenLabs provider is used without required configuration."""


class ElevenLabsProvider:
    """Generates real MP3 audio using the ElevenLabs TTS API."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.elevenlabs_api_key:
            raise ElevenLabsConfigurationError(
                "ELEVENLABS_API_KEY is not configured. Set it in the repository root .env file."
            )

        self._api_key = settings.elevenlabs_api_key
        self._voice_id = settings.elevenlabs_voice_id or _DEFAULT_VOICE_ID

    def generate(self, request: TTSRequest) -> TTSResponse:
        audio_dir = _audio_storage_dir()
        digest = hashlib.sha256(
            f"{request.text}|{request.language}|{request.voice_profile}|{self._voice_id}".encode()
        ).hexdigest()[:16]
        audio_path = audio_dir / f"{digest}.mp3"

        audio_bytes = self._synthesize(request.text)
        audio_path.write_bytes(audio_bytes)

        return TTSResponse(
            audio_path=str(audio_path.resolve()),
            provider="elevenlabs",
            metadata={
                "request_metadata": request.metadata,
                "text_length": len(request.text),
                "voice_profile": request.voice_profile,
                "language": request.language,
                "voice_id": self._voice_id,
                "model_id": _MODEL_ID,
            },
        )

    def _synthesize(self, text: str) -> bytes:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self._voice_id}"
        payload = json.dumps(
            {
                "text": text,
                "model_id": _MODEL_ID,
            }
        ).encode("utf-8")

        api_request = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self._api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(api_request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"ElevenLabs TTS request failed ({exc.code}): {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"ElevenLabs TTS request failed: {exc.reason}") from exc


def _audio_storage_dir() -> Path:
    directory = Path(__file__).resolve().parents[3] / "storage" / "audio"
    directory.mkdir(parents=True, exist_ok=True)
    return directory

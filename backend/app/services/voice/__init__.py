"""Voice service — voice package generation."""

from app.services.voice.models import VoicePackage
from app.services.voice.voice_package_generator import generate_voice_package

__all__ = ["VoicePackage", "generate_voice_package"]

"""Mock video renderer for local development and testing."""

import re
from typing import Any

from app.services.video.models import RenderManifest


class MockVideoRenderer:
    """Returns a fake video path without running FFmpeg."""

    def render(self, manifest: RenderManifest) -> dict[str, Any]:
        slug = _slugify_title(manifest.title)

        return {
            "video_path": f"mock://video/{slug}.mp4",
            "status": "rendered",
            "provider": "mock",
            "metadata": {
                "title": manifest.title,
                "audio_path": manifest.audio_path,
                "total_duration_seconds": manifest.total_duration_seconds,
                "output_format": manifest.output_format,
                "aspect_ratio": manifest.aspect_ratio,
                "resolution": manifest.resolution,
                "scene_count": len(manifest.scenes),
                **manifest.metadata,
            },
        }


def _slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "output"

"""FFmpeg video renderer for placeholder MP4 generation."""

import hashlib
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from app.services.video.models import RenderManifest


class FFmpegRenderError(RuntimeError):
    """Raised when FFmpeg video rendering fails."""


class FFmpegVideoRenderer:
    """Renders a real MP4 placeholder video from a render manifest."""

    def render(self, manifest: RenderManifest) -> dict[str, Any]:
        ffmpeg_executable = _resolve_ffmpeg_executable()
        if ffmpeg_executable is None:
            raise FFmpegRenderError("FFmpeg is not installed or not available on PATH.")

        width, height = _parse_resolution(manifest.resolution)
        duration = manifest.total_duration_seconds
        output_path = _output_path(manifest.title)

        video_filter = _build_video_filter(manifest, width, height, duration)
        command = _build_ffmpeg_command(
            ffmpeg_executable=ffmpeg_executable,
            video_filter=video_filter,
            duration=duration,
            audio_path=manifest.audio_path,
            output_path=output_path,
        )

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip() or "Unknown FFmpeg error"
            raise FFmpegRenderError(f"FFmpeg render failed: {stderr}") from exc

        return {
            "video_path": str(output_path.resolve()),
            "status": "rendered",
            "provider": "ffmpeg",
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


def _resolve_ffmpeg_executable() -> str | None:
    ffmpeg_executable = shutil.which("ffmpeg")
    if ffmpeg_executable is not None:
        return ffmpeg_executable

    windows_fallback = Path(r"C:\ffmpeg\bin\ffmpeg.exe")
    if windows_fallback.is_file():
        return str(windows_fallback.resolve())

    return None


def _video_storage_dir() -> Path:
    directory = Path(__file__).resolve().parents[3] / "storage" / "videos"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "output"


def _output_path(title: str) -> Path:
    slug = _slugify_title(title)
    digest = hashlib.sha256(title.encode("utf-8")).hexdigest()[:12]
    return _video_storage_dir() / f"{slug}-{digest}.mp4"


def _parse_resolution(resolution: str) -> tuple[int, int]:
    if "x" not in resolution:
        return 1080, 1920
    width_text, height_text = resolution.lower().split("x", maxsplit=1)
    return int(width_text), int(height_text)


_X_MARGIN = 120
_Y_MARGIN = 180
_TITLE_FONT_SIZE = 28
_SCENE_FONT_SIZE = 34
_MAX_LINE_CHARS = 32
_MAX_TEXT_LINES = 3


def _sanitize_drawtext(text: str) -> str:
    sanitized = text.replace("\n", " ")
    sanitized = sanitized.replace("\\", " ")
    sanitized = sanitized.replace(":", "-")
    sanitized = sanitized.replace("'", "")
    return " ".join(sanitized.split())


def _wrap_drawtext_lines(
    text: str,
    max_line_chars: int = _MAX_LINE_CHARS,
    max_lines: int = _MAX_TEXT_LINES,
) -> list[str]:
    sanitized = _sanitize_drawtext(text)
    if not sanitized:
        return [""]

    words = sanitized.split()
    lines: list[str] = []
    current = ""

    for word in words:
        if len(lines) >= max_lines:
            break

        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_line_chars:
            current = candidate
            continue

        if current:
            lines.append(current)
            if len(lines) >= max_lines:
                current = ""
                break
            current = word[:max_line_chars]
        else:
            lines.append(word[:max_line_chars])
            current = ""
            if len(lines) >= max_lines:
                break

    if current and len(lines) < max_lines:
        lines.append(current[:max_line_chars])

    return lines or [""]


def _drawtext_text_value(lines: list[str]) -> str:
    return "\\n".join(lines)


def _centered_x_expr() -> str:
    return f"max({_X_MARGIN}\\,(w-text_w)/2)"


def _build_video_filter(
    manifest: RenderManifest,
    width: int,
    height: int,
    duration: int,
) -> str:
    filters: list[str] = []

    title_text = _drawtext_text_value(_wrap_drawtext_lines(manifest.title))
    filters.append(
        f"drawtext=text='{title_text}':fontsize={_TITLE_FONT_SIZE}:fontcolor=white:"
        f"x={_centered_x_expr()}:y={_Y_MARGIN}"
    )

    start = 0
    for scene in manifest.scenes:
        end = start + scene.duration_seconds
        scene_text = _drawtext_text_value(_wrap_drawtext_lines(scene.on_screen_text))
        filters.append(
            f"drawtext=text='{scene_text}':fontsize={_SCENE_FONT_SIZE}:fontcolor=white:"
            f"x={_centered_x_expr()}:y=(h-text_h)/2:"
            f"enable='between(t\\,{start}\\,{end})'"
        )
        start = end

    return (
        f"color=c=#111111:s={width}x{height}:d={duration}:r=30,"
        + ",".join(filters)
    )


def _build_ffmpeg_command(
    ffmpeg_executable: str,
    video_filter: str,
    duration: int,
    audio_path: str,
    output_path: Path,
) -> list[str]:
    command = [
        ffmpeg_executable,
        "-y",
        "-f",
        "lavfi",
        "-i",
        video_filter,
    ]

    audio_file = Path(audio_path)
    if not audio_path.startswith("mock://") and audio_file.is_file():
        command.extend(["-i", str(audio_file.resolve())])
    else:
        command.extend(
            [
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=r=44100:cl=stereo,atrim=duration={duration}",
            ]
        )

    command.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path.resolve()),
        ]
    )
    return command

"""Audio processor for voice note inputs."""
from __future__ import annotations


def process_audio(audio_bytes: bytes, mime_type: str = "audio/webm") -> tuple[bytes, str]:
    """Pass-through audio validator."""
    return audio_bytes, mime_type

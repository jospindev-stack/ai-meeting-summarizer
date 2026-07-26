from pathlib import Path
from typing import Optional

from groq import Groq

from ..config import MAX_AUDIO_BYTES, SUPPORTED_AUDIO_FORMATS, settings
from ..models.schemas import TranscriptionResult

_client = Groq(api_key=settings.groq_api_key)


def transcribe_audio(
    file_bytes: bytes,
    filename: str,
    language: Optional[str] = None,
) -> TranscriptionResult:
    """Transcribe an audio file using Groq Whisper and return text + metadata."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported format '{ext}'. "
            f"Accepted: {', '.join(sorted(SUPPORTED_AUDIO_FORMATS))}"
        )
    if len(file_bytes) > MAX_AUDIO_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise ValueError(
            f"File is {size_mb:.1f} MB — Groq Whisper limit is 25 MB. "
            "Compress the audio to a lower bitrate (e.g. mono MP3 at 64 kbps) "
            "to reduce the file size."
        )

    kwargs: dict = {
        "file": (filename, file_bytes),
        "model": settings.whisper_model,
        "response_format": "verbose_json",
    }
    if language:
        kwargs["language"] = language

    response = _client.audio.transcriptions.create(**kwargs)

    return TranscriptionResult(
        text=response.text.strip(),
        language=getattr(response, "language", None),
        duration_seconds=getattr(response, "duration", None),
    )

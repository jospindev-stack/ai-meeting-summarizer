import time
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..models.schemas import MeetingResponse, TranscriptionResult
from ..services.summarizer import summarize_transcript
from ..services.transcriber import transcribe_audio

router = APIRouter(prefix="/api", tags=["meeting"])


@router.post(
    "/analyze",
    response_model=MeetingResponse,
    summary="Transcribe audio and generate structured meeting summary",
)
async def analyze_meeting(
    audio_file: UploadFile = File(..., description="Meeting audio file (max 25 MB)"),
    language: Optional[str] = Form(
        default=None,
        description="ISO 639-1 language code (e.g. 'fr', 'en'). Leave blank for auto-detection.",
    ),
):
    file_bytes = await audio_file.read()
    start = time.time()

    try:
        transcription: TranscriptionResult = transcribe_audio(
            file_bytes=file_bytes,
            filename=audio_file.filename or "audio.mp3",
            language=language or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Transcription failed.") from exc

    if not transcription.text:
        raise HTTPException(
            status_code=422,
            detail="Transcription returned empty text. Verify the audio contains speech.",
        )

    try:
        meeting = summarize_transcript(
            transcript=transcription.text,
            detected_language=transcription.language,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Summarization failed.") from exc

    return MeetingResponse(
        status="success",
        filename=audio_file.filename or "audio.mp3",
        audio_duration_seconds=transcription.duration_seconds,
        transcript_length=len(transcription.text),
        processing_time=round(time.time() - start, 2),
        transcript=transcription.text,
        meeting=meeting,
    )


@router.post(
    "/transcribe",
    response_model=TranscriptionResult,
    summary="Transcribe audio only (no summarization)",
)
async def transcribe_only(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(default=None),
):
    file_bytes = await audio_file.read()
    try:
        return transcribe_audio(
            file_bytes=file_bytes,
            filename=audio_file.filename or "audio.mp3",
            language=language or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Transcription failed.") from exc


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "AI Meeting Summarizer"}

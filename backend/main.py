from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import meeting

app = FastAPI(
    title="AI Meeting Summarizer",
    description=(
        "Upload a meeting audio file — Groq Whisper transcribes it, "
        "then LLaMA 3.3 extracts key points, decisions and action items."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meeting.router)


@app.get("/", tags=["root"])
async def root():
    return {
        "service": "AI Meeting Summarizer",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "transcribe": "POST /api/transcribe",
            "health": "GET /api/health",
            "docs": "/docs",
        },
    }

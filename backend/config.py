from pydantic_settings import BaseSettings

SUPPORTED_AUDIO_FORMATS = {
    ".mp3", ".mp4", ".mpeg", ".mpga",
    ".m4a", ".wav", ".webm", ".ogg", ".flac",
}
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # Groq Whisper hard limit: 25 MB
MAX_TRANSCRIPT_CHARS = 15_000       # Chars sent to the LLM for summarisation


class Settings(BaseSettings):
    groq_api_key: str
    whisper_model: str = "whisper-large-v3-turbo"
    llm_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"


settings = Settings()

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task: str
    responsible: Optional[str] = None
    deadline: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"


class Decision(BaseModel):
    decision: str
    context: Optional[str] = None


class MeetingSummary(BaseModel):
    title: str
    language: Optional[str] = None
    sentiment: Optional[Literal["positive", "neutral", "mixed", "tense"]] = None
    participants: List[str] = Field(default_factory=list)
    summary: str
    key_points: List[str] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    topics_discussed: List[str] = Field(default_factory=list)


class TranscriptionResult(BaseModel):
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None


class MeetingResponse(BaseModel):
    status: str
    filename: str
    audio_duration_seconds: Optional[float] = None
    transcript_length: int
    processing_time: float
    transcript: str
    meeting: MeetingSummary

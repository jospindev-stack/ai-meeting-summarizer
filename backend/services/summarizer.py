import json

from groq import Groq

from ..config import MAX_TRANSCRIPT_CHARS, settings
from ..models.schemas import MeetingSummary

_client = Groq(api_key=settings.groq_api_key)

_SYSTEM_PROMPT = """You are an expert meeting analyst and executive assistant.
Analyze the provided meeting transcript and extract fully structured data.

Respond with valid JSON only — no markdown, no commentary, no text outside the JSON object.

Guidelines:
- The response language MUST match the transcript language (French transcript → French output).
- Extract participant names only if they are explicitly mentioned in the transcript.
- For action_items, extract responsible person and deadline only when explicitly stated — never infer them.
- priority: assign "high" for urgent/blocking items, "medium" for normal tasks, "low" for nice-to-haves.
- sentiment: overall tone of the meeting (positive/neutral/mixed/tense).
- key_points: 3 to 10 of the most important points discussed.
- If a field cannot be determined, use null (for strings) or [] (for arrays) — never fabricate data.

Return exactly this JSON structure:
{
  "title": "<concise meeting title inferred from content>",
  "language": "<ISO 639-1 code, e.g. fr, en>",
  "sentiment": "<positive | neutral | mixed | tense>",
  "participants": ["<Name>", "..."],
  "summary": "<2–4 sentence executive summary>",
  "key_points": ["<point>", "..."],
  "decisions": [
    {
      "decision": "<what was decided>",
      "context": "<why or how — or null>"
    }
  ],
  "action_items": [
    {
      "task": "<what needs to be done>",
      "responsible": "<person name or null>",
      "deadline": "<date, timeframe, or null>",
      "priority": "<high | medium | low>"
    }
  ],
  "topics_discussed": ["<topic>", "..."]
}"""


def summarize_transcript(transcript: str, detected_language: str | None = None) -> MeetingSummary:
    """Generate a structured meeting summary from a transcript using an LLM."""
    excerpt = transcript[:MAX_TRANSCRIPT_CHARS]
    truncation_note = (
        f"\n\n[NOTE: Transcript was truncated to {MAX_TRANSCRIPT_CHARS} characters for analysis.]"
        if len(transcript) > MAX_TRANSCRIPT_CHARS
        else ""
    )

    lang_hint = (
        f"\nThe transcript is in: {detected_language}. Respond in the same language."
        if detected_language
        else ""
    )

    response = _client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT + lang_hint},
            {
                "role": "user",
                "content": (
                    f"Analyze this meeting transcript and return the structured JSON:\n\n"
                    f"---\n{excerpt}{truncation_note}\n---"
                ),
            },
        ],
        temperature=0.2,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)
    return MeetingSummary(**data)

# AI Meeting Summarizer

> An AI-powered meeting assistant that transcribes audio recordings with **Groq Whisper** and automatically generates structured meeting summaries, key decisions, action items, participants, and discussion topics using **Llama 3.3**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?logo=streamlit)
![Whisper](https://img.shields.io/badge/Whisper-large--v3--turbo-8B5CF6)
![LLaMA](https://img.shields.io/badge/LLaMA-3.3_70B-orange)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

---

## About

AI Meeting Summarizer is a full-stack application that transforms meeting recordings into structured reports using speech recognition and large language models.

The application transcribes multilingual audio with Groq Whisper, analyzes the transcript using Llama 3.3, and automatically extracts executive summaries, key discussion points, decisions, action items, participants, and meeting topics.

The project demonstrates AI integration, prompt engineering, speech-to-text processing, FastAPI backend development, and interactive Streamlit interfaces.

---

## Technology Stack

| Category           | Technology     |
| ------------------ | -------------- |
| Backend            | FastAPI        |
| Frontend           | Streamlit      |
| Speech Recognition | Groq Whisper   |
| AI                 | Groq Llama 3.3 |
| Validation         | Pydantic       |
| Containerization   | Docker         |

---

## Features

| Feature               | Description                                                            |
| --------------------- | ---------------------------------------------------------------------- |
| Audio Transcription   | Multilingual transcription powered by Groq Whisper.                    |
| AI Meeting Summary    | Generate executive summaries from meeting transcripts.                 |
| Decision Extraction   | Automatically identify key decisions discussed during the meeting.     |
| Action Items          | Extract tasks with assignees, priorities, and deadlines.               |
| Participant Detection | Identify participants mentioned in the conversation.                   |
| Topic Extraction      | Detect the main discussion topics automatically.                       |
| Export Options        | Export results as JSON, TXT reports, or CSV action lists.              |
| REST API              | Integrate meeting analysis into external applications through FastAPI. |
| Interactive Interface | User-friendly Streamlit web interface.                                 |

---

## AI Processing Workflow

```text
Audio Recording
      │
      ▼
Groq Whisper
      │
      ▼
Speech-to-Text Transcript
      │
      ▼
Groq Llama 3.3
      │
      ▼
Structured Meeting Analysis
      │
      ▼
Executive Summary
Key Points
Decisions
Action Items
Participants
Topics
      │
      ▼
Exports (JSON • TXT • CSV)
```

---

## Project Structure

```text
ai-meeting-summarizer/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   └── schemas.py
│   ├── routers/
│   │   └── meeting.py
│   └── services/
│       ├── transcriber.py
│       └── summarizer.py
│
├── frontend/
│   └── app.py
│
├── Dockerfile
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── run.bat
├── run.sh
└── README.md
```

---

## Prerequisites

- Python 3.11 or later
- Groq API Key
- Docker & Docker Compose (optional)

Create a free API key at:

https://console.groq.com

---

## Security

The application follows several best practices to ensure secure processing of meeting recordings and AI requests.

Implemented security features include:

- Environment-based API key management
- Server-side communication with Groq APIs
- Request validation using Pydantic
- File type and size validation
- Structured JSON responses
- Configurable CORS policy
- Temporary file cleanup after processing

---

## Environment Variables

| Variable             | Default                   | Description                           |
| -------------------- | ------------------------- | ------------------------------------- |
| `GROQ_API_KEY`       | —                         | Groq API key (required)               |
| `WHISPER_MODEL`      | `whisper-large-v3-turbo`  | Speech-to-text model                  |
| `LLM_MODEL`          | `llama-3.3-70b-versatile` | Language model used for summarization |
| `BACKEND_URL`        | `http://localhost:8000`   | Backend API URL                       |
| `MAX_UPLOAD_SIZE_MB` | `25`                      | Maximum accepted audio file size      |

---

## Deployment

### Backend

The FastAPI backend can be deployed to:

- Railway
- Render
- Docker
- Azure App Service
- Google Cloud Run

Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

- `GROQ_API_KEY`
- `WHISPER_MODEL`
- `LLM_MODEL`

---

### Frontend

The Streamlit frontend can be deployed to:

- Streamlit Community Cloud
- Docker
- Railway

Start command:

```bash
streamlit run frontend/app.py
```

Configure the following secret:

```text
BACKEND_URL=https://your-backend-url
```

---

## Roadmap

Planned improvements include:

- Speaker diarization (identify who said what)
- PDF meeting reports
- Microsoft Teams integration
- Zoom integration
- Google Meet integration
- Email summary delivery
- Meeting history
- User authentication
- Searchable meeting archive
- Multi-language UI
- Docker Compose production profile
- Unit tests
- Integration tests

---

## Future Improvements

Possible enhancements for future versions:

- Calendar integration
- AI-generated meeting titles
- Automatic follow-up emails
- Sentiment analysis per speaker
- Audio noise reduction
- Meeting comparison
- Dashboard with meeting analytics
- Team workspaces
- Slack and Discord notifications

---

## License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute it under the terms of the license.

---

## Author

**Jospin Meka**

Software Developer

Passionate about backend development, artificial intelligence, cloud technologies, and modern software architecture.

- GitHub: https://github.com/jospindev-stack
- Portfolio: https://jospindev.netlify.app

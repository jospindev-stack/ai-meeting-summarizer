# AI Meeting Summarizer

> An AI-powered meeting assistant that transcribes audio recordings with **Groq Whisper** and generates structured meeting summaries, decisions, action items, participants, and discussion topics using **Llama 3.3**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?logo=streamlit)
![Whisper](https://img.shields.io/badge/Whisper-large--v3--turbo-8B5CF6)
![LLaMA](https://img.shields.io/badge/LLaMA-3.3_70B-orange)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
[![CI](https://github.com/jospindev-stack/ai-meeting-summarizer/actions/workflows/ci.yml/badge.svg)](https://github.com/jospindev-stack/ai-meeting-summarizer/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/License-MIT-green)

---

## About

AI Meeting Summarizer is a full-stack application that transforms meeting recordings into structured reports using speech recognition and large language models.

The application transcribes multilingual audio with Groq Whisper, analyzes the transcript using Llama 3.3, and extracts executive summaries, key discussion points, decisions, action items, participants, and meeting topics.

The project demonstrates AI integration, prompt engineering, speech-to-text processing, FastAPI backend development, Docker-based deployment, automated API testing, and continuous integration.

---

## Technology Stack

| Category | Technology |
| --- | --- |
| Backend | FastAPI |
| Frontend | Streamlit |
| Speech Recognition | Groq Whisper |
| AI | Groq Llama 3.3 |
| Validation | Pydantic |
| Containerization | Docker |
| Testing | pytest + pytest-cov |
| CI | GitHub Actions |

---

## Features

| Feature | Description |
| --- | --- |
| Audio Transcription | Multilingual transcription powered by Groq Whisper |
| AI Meeting Summary | Generate executive summaries from meeting transcripts |
| Decision Extraction | Identify key decisions discussed during the meeting |
| Action Items | Extract tasks with assignees, priorities, and deadlines |
| Participant Detection | Identify participants mentioned in the conversation |
| Topic Extraction | Detect the main discussion topics automatically |
| Export Options | Export results as JSON, TXT reports, or CSV action lists |
| REST API | Integrate meeting analysis into external applications through FastAPI |
| Interactive Interface | Streamlit web interface |

---

## AI Processing Workflow

```text
Audio Recording
      |
      v
Groq Whisper
      |
      v
Speech-to-Text Transcript
      |
      v
Groq Llama 3.3
      |
      v
Structured Meeting Analysis
      |
      v
Summary / Decisions / Action Items / Participants / Topics
```

---

## Testing and CI

The backend API is covered with pytest and FastAPI's test client. Speech-to-text and LLM services are mocked during tests, so the suite does not require external Groq calls or production credentials.

Covered scenarios include:

- API health check
- successful audio transcription
- successful transcription-to-summary workflow
- empty transcription validation
- invalid audio validation
- safe handling of transcription provider failures
- safe handling of summarization provider failures

Run the suite locally:

```bash
pip install -r requirements-dev.txt
pytest -q --cov=backend --cov-report=term-missing
```

GitHub Actions runs the test suite on Python 3.12 for pushes to `main`, test branches, and pull requests targeting `main`.

---

## Security

Implemented security and resilience practices include:

- environment-based API key management
- server-side communication with Groq APIs
- request validation using Pydantic
- file type and size validation
- configurable CORS policy
- temporary file cleanup after processing
- generic HTTP 500 responses that do not expose internal AI provider exception details

---

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | - | Groq API key |
| `WHISPER_MODEL` | `whisper-large-v3-turbo` | Speech-to-text model |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Summarization model |
| `BACKEND_URL` | `http://localhost:8000` | Backend API URL |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum accepted audio file size |

---

## Docker

The repository includes Dockerfiles for the FastAPI backend and Streamlit frontend plus Docker Compose orchestration.

```bash
docker compose up --build
```

---

## Deployment

The backend can be deployed with Docker, Railway, Render, Azure App Service, or Google Cloud Run. The Streamlit frontend can be deployed independently and configured through `BACKEND_URL`.

---

## Roadmap

Planned improvements include:

- Speaker diarization
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
- Frontend tests
- End-to-end tests

---

## License

This project is licensed under the MIT License.

---

## Author

**Jospin Meka**

Software Developer

- GitHub: https://github.com/jospindev-stack
- Portfolio: https://jospindev.netlify.app

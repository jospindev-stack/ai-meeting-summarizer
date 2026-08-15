from fastapi.testclient import TestClient

from backend.main import app
from backend.models.schemas import MeetingSummary, TranscriptionResult
import backend.routers.meeting as meeting_router

client = TestClient(app)


def test_health_check():
    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'service': 'AI Meeting Summarizer',
    }


def test_transcribe_returns_transcription(monkeypatch):
    def fake_transcribe_audio(file_bytes, filename, language):
        assert file_bytes == b'audio-bytes'
        assert filename == 'meeting.mp3'
        assert language == 'fr'
        return TranscriptionResult(
            text='Bonjour tout le monde',
            language='fr',
            duration_seconds=12.5,
        )

    monkeypatch.setattr(meeting_router, 'transcribe_audio', fake_transcribe_audio)

    response = client.post(
        '/api/transcribe',
        files={'audio_file': ('meeting.mp3', b'audio-bytes', 'audio/mpeg')},
        data={'language': 'fr'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'text': 'Bonjour tout le monde',
        'language': 'fr',
        'duration_seconds': 12.5,
    }


def test_analyze_returns_structured_meeting(monkeypatch):
    monkeypatch.setattr(
        meeting_router,
        'transcribe_audio',
        lambda **kwargs: TranscriptionResult(
            text='We agreed to ship Friday.',
            language='en',
            duration_seconds=30.0,
        ),
    )
    monkeypatch.setattr(
        meeting_router,
        'summarize_transcript',
        lambda transcript, detected_language: MeetingSummary(
            title='Release Meeting',
            language=detected_language,
            sentiment='positive',
            participants=['Alex'],
            summary='The team agreed on the release date.',
            key_points=['Release Friday'],
            decisions=[{'decision': 'Ship Friday'}],
            action_items=[
                {
                    'task': 'Prepare release notes',
                    'responsible': 'Alex',
                    'priority': 'high',
                }
            ],
            topics_discussed=['Release'],
        ),
    )

    response = client.post(
        '/api/analyze',
        files={'audio_file': ('meeting.mp3', b'audio-bytes', 'audio/mpeg')},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'success'
    assert payload['filename'] == 'meeting.mp3'
    assert payload['transcript'] == 'We agreed to ship Friday.'
    assert payload['meeting']['title'] == 'Release Meeting'
    assert payload['meeting']['decisions'][0]['decision'] == 'Ship Friday'


def test_analyze_rejects_empty_transcription(monkeypatch):
    monkeypatch.setattr(
        meeting_router,
        'transcribe_audio',
        lambda **kwargs: TranscriptionResult(text='', language='en', duration_seconds=1.0),
    )

    response = client.post(
        '/api/analyze',
        files={'audio_file': ('silent.mp3', b'audio-bytes', 'audio/mpeg')},
    )

    assert response.status_code == 422
    assert response.json()['detail'] == (
        'Transcription returned empty text. Verify the audio contains speech.'
    )


def test_transcribe_returns_validation_error(monkeypatch):
    def fail_transcription(**kwargs):
        raise ValueError('Unsupported audio type')

    monkeypatch.setattr(meeting_router, 'transcribe_audio', fail_transcription)

    response = client.post(
        '/api/transcribe',
        files={'audio_file': ('meeting.txt', b'not-audio', 'text/plain')},
    )

    assert response.status_code == 422
    assert response.json() == {'detail': 'Unsupported audio type'}


def test_transcription_provider_error_is_not_exposed(monkeypatch):
    def fail_transcription(**kwargs):
        raise RuntimeError('provider token and internal details')

    monkeypatch.setattr(meeting_router, 'transcribe_audio', fail_transcription)

    response = client.post(
        '/api/transcribe',
        files={'audio_file': ('meeting.mp3', b'audio-bytes', 'audio/mpeg')},
    )

    assert response.status_code == 500
    assert response.json() == {'detail': 'Transcription failed.'}


def test_summarization_provider_error_is_not_exposed(monkeypatch):
    monkeypatch.setattr(
        meeting_router,
        'transcribe_audio',
        lambda **kwargs: TranscriptionResult(
            text='Meeting transcript',
            language='en',
            duration_seconds=10.0,
        ),
    )

    def fail_summary(**kwargs):
        raise RuntimeError('provider secret details')

    monkeypatch.setattr(meeting_router, 'summarize_transcript', fail_summary)

    response = client.post(
        '/api/analyze',
        files={'audio_file': ('meeting.mp3', b'audio-bytes', 'audio/mpeg')},
    )

    assert response.status_code == 500
    assert response.json() == {'detail': 'Summarization failed.'}

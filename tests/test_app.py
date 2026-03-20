"""
Tests for the Claude Translator Flask backend (app.py).

Covers:
  - Health check endpoint
  - Input validation (missing fields, bad JSON, unsupported languages, length limits)
  - Translation endpoint (success + API error handling)
  - Transcription endpoint (success, empty audio, oversized audio, missing file)
  - Error handlers (404, 405)
  - Helper utilities (error_response, validate_json decorator)
"""

import io
import json
from unittest.mock import patch, MagicMock

import pytest

# Patch API clients before importing app so they don't require real keys
with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key", "OPENAI_API_KEY": "test-key"}):
    from app import app, error_response, ALLOWED_LANGUAGES, MAX_INPUT_LENGTH


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Health Check ────────────────────────────────────────────


class TestHealthCheck:
    def test_health_returns_ok(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "claude-translator"


# ── Translate Endpoint ──────────────────────────────────────


class TestTranslateValidation:
    def test_missing_content_type(self, client):
        resp = client.post("/translate", data="not json")
        assert resp.status_code == 415

    def test_missing_text_field(self, client):
        resp = client.post("/translate", json={"targetLang": "English"})
        assert resp.status_code == 400
        assert "text" in resp.get_json()["error"]

    def test_missing_target_lang_field(self, client):
        resp = client.post("/translate", json={"text": "hello"})
        assert resp.status_code == 400
        assert "targetLang" in resp.get_json()["error"]

    def test_empty_text(self, client):
        resp = client.post("/translate", json={"text": "", "targetLang": "English"})
        assert resp.status_code == 400

    def test_text_exceeds_max_length(self, client):
        long_text = "a" * (MAX_INPUT_LENGTH + 1)
        resp = client.post("/translate", json={"text": long_text, "targetLang": "English"})
        assert resp.status_code == 400
        assert "5000" in resp.get_json()["error"]

    def test_unsupported_language(self, client):
        resp = client.post("/translate", json={"text": "hello", "targetLang": "Klingon"})
        assert resp.status_code == 400
        assert "Unsupported" in resp.get_json()["error"]

    def test_all_allowed_languages_accepted(self):
        """Ensure the constant includes both English names and legacy Chinese keys."""
        assert "English" in ALLOWED_LANGUAGES
        assert "Chinese" in ALLOWED_LANGUAGES
        assert "中文" in ALLOWED_LANGUAGES  # legacy key


class TestTranslateSuccess:
    @patch("app.anthropic_client")
    def test_successful_translation(self, mock_client, client):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Bonjour")]
        mock_client.messages.create.return_value = mock_response

        resp = client.post("/translate", json={"text": "Hello", "targetLang": "French"})
        assert resp.status_code == 200
        assert resp.get_json()["result"] == "Bonjour"

    @patch("app.anthropic_client")
    def test_translation_with_whitespace_trimmed(self, mock_client, client):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hola")]
        mock_client.messages.create.return_value = mock_response

        resp = client.post("/translate", json={"text": "  Hello  ", "targetLang": "Spanish"})
        assert resp.status_code == 200
        # Verify trimmed text was sent
        call_args = mock_client.messages.create.call_args
        user_msg = call_args.kwargs["messages"][0]["content"]
        assert "  Hello  " not in user_msg
        assert "Hello" in user_msg


class TestTranslateErrors:
    @patch("app.anthropic_client")
    def test_anthropic_api_error(self, mock_client, client):
        import anthropic
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="rate limited",
            request=MagicMock(),
            body=None,
        )
        resp = client.post("/translate", json={"text": "Hello", "targetLang": "French"})
        assert resp.status_code == 502
        assert "unavailable" in resp.get_json()["error"].lower()

    @patch("app.anthropic_client")
    def test_unexpected_exception(self, mock_client, client):
        mock_client.messages.create.side_effect = RuntimeError("boom")
        resp = client.post("/translate", json={"text": "Hello", "targetLang": "French"})
        assert resp.status_code == 500


# ── Transcribe Endpoint ─────────────────────────────────────


class TestTranscribeValidation:
    def test_no_audio_file(self, client):
        resp = client.post("/transcribe")
        assert resp.status_code == 400
        assert "No audio" in resp.get_json()["error"]

    def test_empty_audio_file(self, client):
        data = {"audio": (io.BytesIO(b""), "audio.webm")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 400
        assert "empty" in resp.get_json()["error"].lower()

    def test_very_short_audio_returns_empty(self, client):
        """Audio < 500 bytes should return empty string (no speech)."""
        data = {"audio": (io.BytesIO(b"x" * 200), "audio.webm")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 200
        assert resp.get_json()["result"] == ""

    def test_oversized_audio_rejected(self, client):
        big = b"x" * (25 * 1024 * 1024 + 1)
        data = {"audio": (io.BytesIO(big), "audio.webm")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 400
        assert "too large" in resp.get_json()["error"].lower()


class TestTranscribeSuccess:
    @patch("app.openai_client")
    def test_successful_transcription(self, mock_client, client):
        mock_transcript = MagicMock()
        mock_transcript.text = "Hello world"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        audio_data = b"x" * 1000  # above 500-byte threshold
        data = {"audio": (io.BytesIO(audio_data), "audio.webm")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 200
        assert resp.get_json()["result"] == "Hello world"

    @patch("app.openai_client")
    def test_transcription_mime_type_detection(self, mock_client, client):
        """Verify correct MIME type is passed based on file extension."""
        mock_transcript = MagicMock()
        mock_transcript.text = "test"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        audio_data = b"x" * 1000
        data = {"audio": (io.BytesIO(audio_data), "recording.mp4")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 200

        call_args = mock_client.audio.transcriptions.create.call_args
        filename, _, mime = call_args.kwargs["file"]
        assert mime == "audio/mp4"

    @patch("app.openai_client")
    def test_transcription_unknown_extension_defaults_webm(self, mock_client, client):
        mock_transcript = MagicMock()
        mock_transcript.text = "test"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        audio_data = b"x" * 1000
        data = {"audio": (io.BytesIO(audio_data), "recording.xyz")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 200

        call_args = mock_client.audio.transcriptions.create.call_args
        _, _, mime = call_args.kwargs["file"]
        assert mime == "audio/webm"


class TestTranscribeErrors:
    @patch("app.openai_client")
    def test_whisper_api_failure(self, mock_client, client):
        mock_client.audio.transcriptions.create.side_effect = Exception("API down")
        audio_data = b"x" * 1000
        data = {"audio": (io.BytesIO(audio_data), "audio.webm")}
        resp = client.post("/transcribe", content_type="multipart/form-data", data=data)
        assert resp.status_code == 502


# ── Error Handlers ──────────────────────────────────────────


class TestErrorHandlers:
    def test_404(self, client):
        resp = client.get("/nonexistent")
        assert resp.status_code == 404
        assert "not found" in resp.get_json()["error"].lower()

    def test_405_method_not_allowed(self, client):
        resp = client.get("/translate")  # GET not allowed
        assert resp.status_code == 405
        assert "not allowed" in resp.get_json()["error"].lower()


# ── Helpers ─────────────────────────────────────────────────


class TestHelpers:
    def test_error_response_default_status(self):
        with app.app_context():
            resp, status = error_response("bad request")
            assert status == 400
            assert json.loads(resp.data)["error"] == "bad request"

    def test_error_response_custom_status(self):
        with app.app_context():
            resp, status = error_response("not found", 404)
            assert status == 404

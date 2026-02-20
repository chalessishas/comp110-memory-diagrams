"""
Claude Translator — Backend API
Flask server handling translation (Anthropic Claude) and speech-to-text (OpenAI Whisper).
"""

import os
import logging
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
from openai import OpenAI

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
log = logging.getLogger(__name__)

# ── App Setup ────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # tighten in production

# ── Clients ──────────────────────────────────────────────────
anthropic_client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# ── Constants ────────────────────────────────────────────────
ALLOWED_LANGUAGES = {
    "English", "Chinese", "Japanese", "Korean",
    "French", "Spanish", "German", "Russian",
    "Portuguese", "Arabic",
    # Legacy Chinese keys (from old frontend)
    "英文", "中文", "日文", "韩文", "法文",
    "西班牙文", "德文", "俄文", "葡萄牙文", "阿拉伯文",
}

MAX_INPUT_LENGTH = 5000
CLAUDE_MODEL = "claude-sonnet-4-20250514"
WHISPER_MODEL = "whisper-1"
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB (Whisper limit)

SYSTEM_PROMPT = (
    "You are a professional translator. "
    "Detect the source language automatically, then translate the user-provided text "
    "into the requested target language. "
    "Output ONLY the translated text — no explanations, no notes, no quotation marks."
)

# ── Helpers ──────────────────────────────────────────────────

def error_response(message: str, status: int = 400):
    """Return a JSON error with the given HTTP status."""
    return jsonify({"error": message}), status


def validate_json(*required_fields):
    """Decorator that ensures the request is JSON and contains required fields."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)
            if data is None:
                return error_response("Request must be JSON.", 415)
            for field in required_fields:
                if not data.get(field):
                    return error_response(f"Missing required field: '{field}'.")
            return fn(data, *args, **kwargs)
        return wrapper
    return decorator


# ── Routes ───────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    """Health-check endpoint."""
    return jsonify({"status": "ok", "service": "claude-translator"})


@app.route("/translate", methods=["POST"])
@validate_json("text", "targetLang")
def translate(data):
    text = data["text"].strip()
    target_lang = data["targetLang"].strip()

    # Validate
    if len(text) > MAX_INPUT_LENGTH:
        return error_response(f"Text exceeds {MAX_INPUT_LENGTH} characters.")
    if target_lang not in ALLOWED_LANGUAGES:
        return error_response(f"Unsupported target language: '{target_lang}'.")

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Translate the following text into {target_lang}:\n\n{text}",
                }
            ],
        )
        result = response.content[0].text
        log.info("Translation OK — %d chars → %s", len(text), target_lang)
        return jsonify({"result": result})

    except anthropic.APIError as e:
        log.error("Anthropic API error: %s", e)
        return error_response("Translation service unavailable. Please try again.", 502)
    except Exception as e:
        log.exception("Unexpected error during translation")
        return error_response("Internal server error.", 500)


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return error_response("No audio file provided.")

    audio_file = request.files["audio"]
    filename = audio_file.filename or "audio.webm"
    audio_bytes = audio_file.read()

    if len(audio_bytes) == 0:
        return error_response("Audio file is empty.")
    if len(audio_bytes) < 500:
        # Very short segments likely contain no speech
        return jsonify({"result": ""})
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        return error_response("Audio file too large (max 25 MB).")

    # Detect mime type from filename extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    mime_map = {
        "webm": "audio/webm",
        "mp4": "audio/mp4",
        "m4a": "audio/mp4",
        "ogg": "audio/ogg",
        "wav": "audio/wav",
    }
    mime_type = mime_map.get(ext, "audio/webm")

    try:
        transcript = openai_client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=(filename, audio_bytes, mime_type),
        )
        log.info("Transcription OK — %d bytes (%s)", len(audio_bytes), ext)
        return jsonify({"result": transcript.text})

    except Exception as e:
        log.exception("Transcription error")
        return error_response("Transcription failed. Please try again.", 502)


# ── Error Handlers ───────────────────────────────────────────

@app.errorhandler(404)
def not_found(_):
    return error_response("Endpoint not found.", 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return error_response("Method not allowed.", 405)


@app.errorhandler(500)
def internal_error(_):
    return error_response("Internal server error.", 500)


# ── Entry Point ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    log.info("Starting Claude Translator API on port %d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)
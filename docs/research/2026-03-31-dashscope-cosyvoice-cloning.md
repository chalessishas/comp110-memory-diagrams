# DashScope CosyVoice Voice Cloning API Research

**Date:** 2026-03-31
**Sources:** Alibaba Cloud official docs, DashScope API reference

## Summary

DashScope provides CosyVoice voice cloning through two steps:
1. **Voice Registration** (REST API) -- upload reference audio, get `voice_id`
2. **TTS Synthesis** (WebSocket only) -- use `voice_id` to synthesize new text

Voice management (create/query/update/delete) uses standard HTTP POST.
Speech synthesis ONLY supports WebSocket -- no HTTP REST endpoint for TTS.

## API Endpoints

| Operation | Beijing | Singapore |
|-----------|---------|-----------|
| Voice CRUD | `POST https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization` | `POST https://dashscope-intl.aliyuncs.com/api/v1/services/audio/tts/customization` |
| TTS WebSocket | `wss://dashscope.aliyuncs.com/api-ws/v1/inference/` | `wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference/` |

## Voice Cloning (Step 1: Register)

### Request
```json
POST /api/v1/services/audio/tts/customization
Authorization: Bearer <DASHSCOPE_API_KEY>
Content-Type: application/json

{
  "model": "voice-enrollment",
  "input": {
    "action": "create_voice",
    "target_model": "cosyvoice-v3.5-plus",
    "prefix": "myvoice",
    "url": "https://publicly-accessible-audio-url.wav",
    "language_hints": ["zh"]
  }
}
```

### Response
```json
{
  "output": {
    "voice_id": "cosyvoice-v3.5-plus-myvoice-xxxxxxxx"
  },
  "request_id": "..."
}
```

### Parameters
- `model`: Fixed `"voice-enrollment"`
- `target_model`: Must match later TTS model. Options: `cosyvoice-v3.5-plus`, `cosyvoice-v3.5-flash`, `cosyvoice-v3-plus`, `cosyvoice-v3-flash`, `cosyvoice-v2`
- `prefix`: Alphanumeric only, max 10 chars
- `url`: Publicly accessible audio URL
- `language_hints`: `["zh"]`, `["en"]`, etc. (optional but recommended)
- `max_prompt_audio_length`: 3.0-30.0 seconds (default 10.0)
- `enable_preprocess`: Boolean, noise reduction

## TTS Synthesis (Step 2: Synthesize)

WebSocket only. Three-phase protocol:
1. `run-task` -- configure model/voice/format
2. `continue-task` -- send text chunks
3. `finish-task` -- signal end

### run-task message
```json
{
  "header": { "action": "run-task", "task_id": "<UUID>", "streaming": "duplex" },
  "payload": {
    "task_group": "audio",
    "task": "tts",
    "function": "SpeechSynthesizer",
    "model": "cosyvoice-v3.5-plus",
    "parameters": {
      "text_type": "PlainText",
      "voice": "<voice_id from step 1>",
      "format": "mp3",
      "sample_rate": 22050,
      "volume": 50,
      "rate": 1,
      "pitch": 1
    },
    "input": {}
  }
}
```

### Response flow
- Text messages: `task-started`, `sentence-begin`, `sentence-synthesis`, `sentence-end`, `task-finished`
- Binary messages: raw audio data in specified format

## Audio Requirements

| Requirement | Value |
|-------------|-------|
| Format | WAV (preferred), MP3, OGG |
| Sample rate | >= 16 kHz (24kHz+ recommended) |
| Channels | Mono |
| Duration | 10-20 seconds (recommended 15s) |
| Max file size | 10 MB |
| Speech ratio | >= 60% active speech |
| Silence gaps | No gaps > 2 seconds |
| Quality | No background noise, echo, or static |

## Limitations

- Max 1000 voices per account
- Unused voices auto-deleted after 1 year
- `target_model` at creation MUST match `model` at synthesis
- v3.5 models only available in Beijing region
- No HTTP REST endpoint for TTS synthesis (WebSocket only)

## Pricing

| Model | Price (per 10,000 chars) |
|-------|--------------------------|
| cosyvoice-v3.5-plus / v3-plus | $0.287 (~2 RMB) |
| cosyvoice-v3.5-flash / v3-flash | $0.116-$0.143 |
| cosyvoice-v2 | $0.287 |

- Voice creation/management: **Free**
- Character counting: Chinese char = 2, English/number/punctuation = 1
- New accounts get free quota (varies by region)

## Output Formats

Formats: pcm, wav, mp3 (default), opus
Sample rates: 8000, 16000, 22050 (default), 24000, 44100, 48000 Hz

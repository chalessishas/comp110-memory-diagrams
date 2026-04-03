# Research: Reducing Input Friction in Auto-Execution Mode

Date: 2026-03-24
Context: User complained "需要输入很多内容很烦" — auto mode still requires 3 text inputs (thesis, outline, hook) before AI starts writing. Need to reduce friction.

## Problem

Auto mode flow: thesis input → outline input → hook input → AI writes. Three mandatory text fields before anything happens. For a feature branded "you think, we write," this is too much writing.

## Option 1: Voice Input (Web Speech API)

**What:** Add a microphone button next to each checkpoint textarea. User speaks, text appears.

**Implementation:**
- `react-speech-recognition` npm package (React wrapper for Web Speech API)
- Source: https://github.com/JamesBrill/react-speech-recognition
- Chinese support: `SpeechRecognition.startListening({ language: 'zh-CN' })`
- English: `SpeechRecognition.startListening({ language: 'en-US' })`
- Zero backend cost — browser handles recognition via Google's servers

**Code sketch:**
```tsx
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

// In checkpoint UI:
const { transcript, listening, resetTranscript } = useSpeechRecognition();

<button onClick={() => SpeechRecognition.startListening({ language })}>
  {listening ? "Listening..." : "🎤"}
</button>
// transcript auto-fills the textarea
```

**Limitations:**
- Chrome/Edge only (no Firefox/Safari support for SpeechRecognition)
- Requires internet (audio sent to Google for processing)
- Not available on iOS Safari
- Need polyfill or fallback for unsupported browsers

**Effort:** ~30 lines of code in AutoExecutor checkpoint UI. Install `react-speech-recognition` + `regenerator-runtime`.

**Impact:** High. Speaking a thesis is much faster than typing one. Directly addresses "输入很多内容很烦."

## Option 2: Merge Checkpoints into One

**What:** Instead of 3 separate checkpoints (thesis → outline → hook), show a single "Tell me about your essay" input that collects everything at once.

**How it works:**
1. Single large textarea: "What do you want to write about? Include your main argument, key points, and how you'd like to open."
2. AI splits the response into thesis/outline/hook automatically before drafting
3. User sees a summary of what AI extracted → confirms or edits → then auto blocks run

**Implementation:**
- Add a "quick-input" mode that sends one user message to DeepSeek
- DeepSeek returns structured `{ thesis, outline, hook }` JSON
- Auto-populate the 3 checkpoint outputs
- Skip directly to draft block

**Effort:** New API action (~40 lines in route.ts) + UI tweak (~20 lines in AutoExecutor)

**Impact:** Reduces 3 inputs to 1. User can type a single paragraph or even a few sentences. Dramatically lower friction.

**Risk:** If AI misinterprets the user's intent, the extracted thesis/outline may not match what the user meant. Needs a confirmation step showing "Here's what I understood: [thesis] [outline] [hook] — is this right?"

## Option 3: Preset Topics (Zero Input)

**What:** Offer pre-built topic cards for common essay types. User clicks one, auto mode starts with zero typing.

**Examples:**
- "Social media's impact on education"
- "Should college tuition be free?"
- "Climate change solutions for developing nations"
- "AI in healthcare: benefits and risks"

**Implementation:** Static array of `{ topic, thesis, outline, hook }` objects. Click → auto-populate → start pipeline.

**Effort:** ~20 lines data + UI.

**Impact:** Zero friction for demo/exploration. But users with their own topics still need to type.

## Recommendation: Option 2 + Option 1

**Phase 1 (now):** Merge 3 checkpoints into 1 unified input. "Tell me what you want to write about" → AI extracts structure → confirm → auto-execute. This cuts friction by 67% (1 input vs 3).

**Phase 2 (post-MVP):** Add voice input button on the unified input. "Say what you want to write about" → speech-to-text fills the box → AI extracts structure → confirm → auto-execute. This makes it truly "you think, we write" — user literally just talks.

**Phase 3 (nice-to-have):** Add preset topics for zero-click demo experience.

## Why Not Just Remove Checkpoints?

The checkpoints ARE the product differentiation. Without them, auto mode is ChatGPT. The thesis/outline/hook inputs are where the user contributes their thinking. The fix is to make input easier, not to remove it.

The key insight from HyperWrite and Jenni: reduce friction by meeting users where they are. A student doesn't think in "thesis statements" and "outline points" — they think "I want to write about X because Y." Let AI do the structuring.

Sources:
- [react-speech-recognition](https://github.com/JamesBrill/react-speech-recognition)
- [Web Speech API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [HyperWrite](https://www.hyperwriteai.com/)
- [Jenni AI](https://jenni.ai/)
- [Web Speech API Chinese support](https://webspeechrecognition.com/react-speech-recognition-api-docs)

import { writeFileSync, readFileSync } from "fs";
import { join, resolve } from "path";
import { createServer } from "http";
import { randomUUID } from "crypto";
import WebSocket from "ws";
import { SegmentAudio } from "./types.js";

const DASHSCOPE_ENDPOINT =
  "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation";
const DASHSCOPE_CUSTOM_ENDPOINT =
  "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization";
const DASHSCOPE_WS_URL =
  "wss://dashscope.aliyuncs.com/api-ws/v1/inference/";
const SAMPLE_RATE = 24000;
const BYTES_PER_SAMPLE = 2;

export interface TTSOptions {
  voice?: string;
  language?: string;
  /** Path to reference audio for voice cloning */
  cloneRef?: string;
  /** Cached voice_id from previous clone registration */
  voiceId?: string;
}

// ── Standard TTS (Qwen3-TTS, HTTP) ────────────

async function synthesizeStandard(
  text: string,
  outputPath: string,
  voice: string,
  language: string
): Promise<SegmentAudio> {
  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (!apiKey) throw new Error("DASHSCOPE_API_KEY not set");

  const res = await fetch(DASHSCOPE_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "qwen3-tts-flash",
      input: { text: text.slice(0, 600), voice, language_type: language },
    }),
  });

  if (!res.ok) throw new Error(`TTS ${res.status}: ${await res.text()}`);

  const data = (await res.json()) as { output?: { audio?: { url?: string } } };
  const audioUrl = data.output?.audio?.url;
  if (!audioUrl) throw new Error("TTS: no audio URL");

  const wavRes = await fetch(audioUrl);
  if (!wavRes.ok) throw new Error(`WAV download: ${wavRes.status}`);
  const buf = Buffer.from(await wavRes.arrayBuffer());
  writeFileSync(outputPath, buf);

  const pcmBytes = Math.max(0, buf.length - 44);
  const durationMs = Math.round((pcmBytes / (SAMPLE_RATE * BYTES_PER_SAMPLE)) * 1000);
  return { filePath: outputPath, durationMs };
}

// ── Voice Clone Registration ───────────────────

async function serveFileTemporarily(
  filePath: string,
  port = 18923
): Promise<{ url: string; close: () => void }> {
  const data = readFileSync(filePath);
  const server = createServer((req, res) => {
    res.writeHead(200, { "Content-Type": "audio/wav", "Content-Length": data.length });
    res.end(data);
  });

  return new Promise((resolve) => {
    server.listen(port, () => {
      resolve({
        url: `http://localhost:${port}/reference.wav`,
        close: () => server.close(),
      });
    });
  });
}

export async function registerCloneVoice(
  refAudioPath: string,
  prefix = "coursevc"
): Promise<string> {
  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (!apiKey) throw new Error("DASHSCOPE_API_KEY not set");

  // Serve the file temporarily for DashScope to download
  // Note: this only works if DashScope can reach localhost (it can't in production)
  // For production, upload to OSS/S3 first
  // Alternative: try base64 upload via cosyvoice endpoint
  console.log("  Registering clone voice...");

  // Try direct file upload approach first
  const audioData = readFileSync(refAudioPath);
  const base64Audio = audioData.toString("base64");

  const res = await fetch(DASHSCOPE_CUSTOM_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "voice-enrollment",
      input: {
        action: "create_voice",
        target_model: "cosyvoice-v3-plus",
        prefix,
        audio: base64Audio,
        language_hints: ["zh"],
        max_prompt_audio_length: 30.0,
      },
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    // If base64 doesn't work, fall back to URL approach
    if (err.includes("url") || err.includes("audio")) {
      console.log("  Base64 upload failed, trying URL approach...");
      return registerCloneVoiceViaUrl(refAudioPath, prefix);
    }
    throw new Error(`Voice registration failed (${res.status}): ${err}`);
  }

  const data = (await res.json()) as { output?: { voice_id?: string } };
  const voiceId = data.output?.voice_id;
  if (!voiceId) throw new Error("No voice_id in response");

  console.log(`  Voice registered: ${voiceId}`);
  return voiceId;
}

async function registerCloneVoiceViaUrl(
  refAudioPath: string,
  prefix: string
): Promise<string> {
  const apiKey = process.env.DASHSCOPE_API_KEY!;
  const { url, close } = await serveFileTemporarily(refAudioPath);

  try {
    const res = await fetch(DASHSCOPE_CUSTOM_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "voice-enrollment",
        input: {
          action: "create_voice",
          target_model: "cosyvoice-v3-plus",
          prefix,
          url,
          language_hints: ["zh"],
          max_prompt_audio_length: 30.0,
        },
      }),
    });

    if (!res.ok) throw new Error(`Voice registration: ${res.status} ${await res.text()}`);

    const data = (await res.json()) as { output?: { voice_id?: string } };
    const voiceId = data.output?.voice_id;
    if (!voiceId) throw new Error("No voice_id in response");

    console.log(`  Voice registered: ${voiceId}`);
    return voiceId;
  } finally {
    close();
  }
}

// ── Clone Voice TTS (CosyVoice, WebSocket) ────

function synthesizeClone(
  voiceId: string,
  text: string,
  outputPath: string
): Promise<SegmentAudio> {
  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (!apiKey) throw new Error("DASHSCOPE_API_KEY not set");

  return new Promise((resolve, reject) => {
    const taskId = randomUUID();
    const chunks: Buffer[] = [];

    const ws = new WebSocket(DASHSCOPE_WS_URL, {
      headers: { Authorization: `bearer ${apiKey}` },
    });

    ws.on("open", () => {
      ws.send(
        JSON.stringify({
          header: { action: "run-task", task_id: taskId, streaming: "duplex" },
          payload: {
            task_group: "audio",
            task: "tts",
            function: "SpeechSynthesizer",
            model: "cosyvoice-v3-plus",
            parameters: {
              text_type: "PlainText",
              voice: voiceId,
              format: "wav",
              sample_rate: SAMPLE_RATE,
              volume: 50,
              rate: 1,
              pitch: 1,
            },
            input: {},
          },
        })
      );
    });

    ws.on("message", (data: Buffer | string, isBinary: boolean) => {
      if (isBinary) {
        chunks.push(Buffer.isBuffer(data) ? data : Buffer.from(data));
        return;
      }

      const msg = JSON.parse(data.toString());
      const event = msg.header?.event;

      if (event === "task-started") {
        ws.send(
          JSON.stringify({
            header: { action: "continue-task", task_id: taskId, streaming: "duplex" },
            payload: { input: { text } },
          })
        );
        ws.send(
          JSON.stringify({
            header: { action: "finish-task", task_id: taskId, streaming: "duplex" },
            payload: { input: {} },
          })
        );
      } else if (event === "task-failed") {
        reject(new Error(`Clone TTS failed: ${JSON.stringify(msg)}`));
        ws.close();
      }
    });

    ws.on("error", reject);
    ws.on("close", () => {
      if (chunks.length === 0) {
        reject(new Error("Clone TTS: no audio data received"));
        return;
      }

      const audio = Buffer.concat(chunks);
      writeFileSync(outputPath, audio);

      // Duration from raw audio bytes
      const durationMs = Math.round((audio.length / (SAMPLE_RATE * BYTES_PER_SAMPLE)) * 1000);
      resolve({ filePath: outputPath, durationMs });
    });
  });
}

// ── Public API ─────────────────────────────────

export async function synthesizeAll(
  narrations: string[],
  outputDir: string,
  options: TTSOptions = {}
): Promise<SegmentAudio[]> {
  const results: SegmentAudio[] = [];
  const { voice = "Ethan", language = "Chinese", cloneRef, voiceId: cachedVoiceId } = options;

  // If clone voice requested, register it first
  let voiceId = cachedVoiceId;
  if (cloneRef && !voiceId) {
    voiceId = await registerCloneVoice(cloneRef);
    // Wait for voice to be ready
    console.log("  Waiting for voice deployment...");
    await new Promise((r) => setTimeout(r, 5000));
  }

  for (let i = 0; i < narrations.length; i++) {
    const outputPath = join(outputDir, `segment-${String(i).padStart(3, "0")}.wav`);
    console.log(
      `  [TTS] Segment ${i + 1}/${narrations.length}: ${narrations[i].slice(0, 50)}...`
    );

    if (voiceId) {
      const result = await synthesizeClone(voiceId, narrations[i], outputPath);
      results.push(result);
    } else {
      const result = await synthesizeStandard(narrations[i], outputPath, voice, language);
      results.push(result);
    }

    // Rate limit
    if (i < narrations.length - 1) {
      await new Promise((r) => setTimeout(r, 350));
    }
  }

  return results;
}

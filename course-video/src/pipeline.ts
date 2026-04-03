import { mkdirSync, writeFileSync, unlinkSync, rmSync } from "fs";
import { join, resolve } from "path";
import { execSync } from "child_process";
import { renderVideo } from "@revideo/renderer";
import { generateScript } from "./script-generator.js";
import { synthesizeAll } from "./tts.js";
import { CourseScript, PipelineResult } from "./types.js";
import { preRenderFormulas } from "./latex.js";

export interface PipelineOptions {
  topic: string;
  sourceFile?: string;
  model?: string;
  outputDir?: string;
  voice?: string;
  language?: string;
  cloneRef?: string;
  voiceId?: string;
}

export async function runPipeline(
  options: PipelineOptions
): Promise<PipelineResult> {
  const {
    topic,
    sourceFile,
    model,
    outputDir = "./output",
    voice,
    language,
    cloneRef,
    voiceId,
  } = options;

  const absOutputDir = resolve(outputDir);
  const audioDir = join(absOutputDir, "audio");
  mkdirSync(audioDir, { recursive: true });

  const sanitizedTitle = topic
    .replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 60);

  // ── Step 1: Generate teaching script ─────────
  console.log("\n[1/4] Generating teaching script...");
  const script: CourseScript = await generateScript({
    topic,
    sourceFile,
    model,
  });
  console.log(
    `  Script: "${script.title}" — ${script.segments.length} segments`
  );

  // ── Step 2: TTS synthesis ────────────────────
  console.log("\n[2/4] Synthesizing narration...");
  const narrations = script.segments.map((s) => s.narration);
  const segmentAudios = await synthesizeAll(narrations, audioDir, {
    voice,
    language,
    cloneRef: cloneRef ? resolve(cloneRef) : undefined,
    voiceId,
  });
  const totalDurationMs = segmentAudios.reduce(
    (sum, a) => sum + a.durationMs,
    0
  );
  console.log(
    `  Total audio: ${(totalDurationMs / 1000).toFixed(1)}s across ${segmentAudios.length} segments`
  );

  // ── Step 2.5: Pre-render LaTeX formulas to SVG ─
  console.log("\n  Pre-rendering LaTeX formulas...");
  const formulaMap = preRenderFormulas(script);
  console.log(`  ${formulaMap.size} formulas rendered to SVG`);

  // Serialize formula map as JSON: { "segIdx-actionIdx": "data:image/svg+xml;base64,..." }
  const formulaMapJson: Record<string, string> = {};
  for (const [key, uri] of formulaMap) {
    formulaMapJson[key] = uri;
  }

  // ── Step 3: Render board animations (video only, no audio) ─
  console.log("\n[3/4] Rendering board animations...");
  const silentVideoPath = await renderVideo({
    projectFile: resolve("./src/renderer/project.tsx"),
    variables: {
      script: JSON.stringify(script),
      segmentAudios: JSON.stringify(
        segmentAudios.map((a) => ({
          filePath: "", // audio handled by FFmpeg, not Revideo
          durationMs: a.durationMs,
        }))
      ),
      formulaMap: JSON.stringify(formulaMapJson),
    },
    settings: {
      outFile: `${sanitizedTitle}-silent.mp4`,
      outDir: absOutputDir,
      logProgress: true,
    },
  });

  // ── Step 4: Merge audio + video via FFmpeg ───
  console.log("\n[4/4] Merging audio and video...");

  // Revideo outputs: {name}-0.mp4 (combined) + {name}-visuals.mp4 + {name}-audio.wav
  // renderVideo returns the -0.mp4 path. We want -visuals.mp4 for merge.
  const baseName = silentVideoPath.replace(/(-0)?\.mp4$/, "");
  const visualsPath = `${baseName}-visuals.mp4`;
  const revideoAudioPath = `${baseName}-audio.wav`;

  // Concatenate all WAV segments into one audio file
  const concatListPath = join(audioDir, "concat.txt");
  const concatList = segmentAudios
    .map((a) => `file '${resolve(a.filePath)}'`)
    .join("\n");
  writeFileSync(concatListPath, concatList);

  const mergedAudioPath = join(audioDir, "merged.wav");
  execSync(
    `ffmpeg -y -f concat -safe 0 -i "${concatListPath}" -c copy "${mergedAudioPath}"`,
    { stdio: "pipe" }
  );

  // Merge visuals-only video + TTS audio (strip any existing audio from video with -an, then add new)
  const finalVideoPath = join(absOutputDir, `${sanitizedTitle}.mp4`);
  execSync(
    `ffmpeg -y -i "${visualsPath}" -i "${mergedAudioPath}" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 128k -shortest "${finalVideoPath}"`,
    { stdio: "pipe" }
  );

  // Clean up ALL intermediate files — output/ should only contain the final .mp4
  for (const f of [silentVideoPath, visualsPath, revideoAudioPath]) {
    try { unlinkSync(f); } catch {}
  }
  rmSync(audioDir, { recursive: true, force: true });

  console.log(`\nDone! Video saved to: ${finalVideoPath}`);

  return { videoPath: finalVideoPath, script, totalDurationMs };
}

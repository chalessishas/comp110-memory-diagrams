#!/usr/bin/env node

import { runPipeline } from "./pipeline.js";

function printUsage() {
  console.log(`
Usage: course-video generate <topic> [options]

Options:
  --model <claude|deepseek>   LLM to use (default: deepseek)
  --source <file>             Reference material file path
  --output <dir>              Output directory (default: ./output)
  --voice <name>              TTS voice (default: longanyang for Chinese)
  --language <lang>           TTS language (default: Chinese)
  --clone <file>              Reference audio for voice cloning (10-30s WAV)
  --voice-id <id>             Use existing cloned voice ID (skip registration)

Examples:
  course-video generate "二次方程求根公式"
  course-video generate "图论：BFS 遍历" --model deepseek
  course-video generate "极限的定义" --clone ./voice/reference.wav
`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    printUsage();
    process.exit(0);
  }

  if (args[0] !== "generate") {
    console.error(`Unknown command: ${args[0]}. Use "generate".`);
    printUsage();
    process.exit(1);
  }

  const topic = args[1];
  if (!topic) {
    console.error("Error: topic is required.");
    printUsage();
    process.exit(1);
  }

  // Parse flags
  const flags: Record<string, string> = {};
  for (let i = 2; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, "");
    flags[key] = args[i + 1] ?? "";
  }

  console.log(`\nCourse Video Generator`);
  console.log(`Topic: ${topic}`);
  console.log(`Model: ${flags.model ?? "deepseek"}`);
  console.log(`Language: ${flags.language ?? "Chinese"}`);
  if (flags.clone) console.log(`Voice clone: ${flags.clone}`);
  if (flags.source) console.log(`Source: ${flags.source}`);
  console.log("─".repeat(40));

  try {
    const result = await runPipeline({
      topic,
      sourceFile: flags.source,
      model: flags.model ?? "deepseek",
      outputDir: flags.output,
      voice: flags.voice,
      language: flags.language ?? "Chinese",
      cloneRef: flags.clone,
      voiceId: flags["voice-id"],
    });

    console.log(`\nVideo: ${result.videoPath}`);
    console.log(
      `Duration: ${(result.totalDurationMs / 1000).toFixed(1)}s`
    );
    console.log(`Segments: ${result.script.segments.length}`);
  } catch (err) {
    console.error("\nPipeline failed:", (err as Error).message);
    process.exit(1);
  }
}

main();

import { makeProject, useScene } from "@revideo/core";
import { makeScene2D } from "@revideo/2d";
import { waitFor } from "@revideo/core";
import { renderBoard } from "./scenes/board.js";

const boardScene = makeScene2D("board", function* (view) {
  const vars = useScene().variables;
  const scriptJson = vars.get("script", "{}")();
  const segmentAudiosJson = vars.get("segmentAudios", "[]")();
  const formulaMapJson = vars.get("formulaMap", "{}")();

  const script = JSON.parse(scriptJson as string);
  const segmentAudios = JSON.parse(segmentAudiosJson as string) as {
    filePath: string;
    durationMs: number;
  }[];
  const formulaMap = JSON.parse(formulaMapJson as string) as Record<string, string>;

  // Render board animations only — audio is merged by FFmpeg in pipeline.ts
  yield* renderBoard(view, script.segments, segmentAudios, formulaMap);

  yield* waitFor(1); // 1s padding at the end
});

export default makeProject({
  scenes: [boardScene],
  variables: {
    script: "{}",
    segmentAudios: "[]",
    formulaMap: "{}",
  },
  settings: {
    shared: {
      size: { x: 1920, y: 1080 },
      background: "#1a3a2a", // dark green chalkboard
    },
  },
});

import { z } from "zod";

// ── Board Actions ──────────────────────────────

const WriteText = z.object({
  type: z.literal("write_text"),
  id: z.string().optional(),
  text: z.string(),
});

const ShowFormula = z.object({
  type: z.literal("show_formula"),
  id: z.string().optional(),
  latex: z.string(),
});

const DrawArrow = z.object({
  type: z.literal("draw_arrow"),
  from: z.string(),
  to: z.string(),
});

const Highlight = z.object({
  type: z.literal("highlight"),
  target: z.string(),
  color: z.string().optional(),
});

const Erase = z.object({
  type: z.literal("erase"),
  target: z.union([z.literal("all"), z.string()]),
});

const Pause = z.object({
  type: z.literal("pause"),
  duration: z.number(),
});

export const BoardActionSchema = z.discriminatedUnion("type", [
  WriteText,
  ShowFormula,
  DrawArrow,
  Highlight,
  Erase,
  Pause,
]);

// ── Segment & Script ───────────────────────────

export const SegmentSchema = z.object({
  narration: z.string(),
  board: z.array(BoardActionSchema),
});

export const CourseScriptSchema = z.object({
  title: z.string(),
  segments: z.array(SegmentSchema),
});

// ── TypeScript types (inferred from Zod) ───────

export type BoardAction = z.infer<typeof BoardActionSchema>;
export type Segment = z.infer<typeof SegmentSchema>;
export type CourseScript = z.infer<typeof CourseScriptSchema>;

// ── Pipeline types ─────────────────────────────

export interface SegmentAudio {
  filePath: string;
  durationMs: number;
}

export interface PipelineResult {
  videoPath: string;
  script: CourseScript;
  totalDurationMs: number;
}

// ── Time allocation ────────────────────────────

/** Weight for each board action type, used to proportionally distribute time */
export function actionWeight(action: BoardAction): number {
  switch (action.type) {
    case "write_text":
      return action.text.length;
    case "show_formula":
      return action.latex.length * 1.5;
    case "draw_arrow":
      return 10;
    case "highlight":
      return 5;
    case "erase":
      return 3;
    case "pause":
      return 0; // pause uses its own duration, not proportional
  }
}

/** Allocate time (ms) to each board action within a segment */
export function allocateTime(
  actions: BoardAction[],
  totalMs: number
): number[] {
  const pauseTotal = actions.reduce(
    (sum, a) => sum + (a.type === "pause" ? a.duration * 1000 : 0),
    0
  );
  const available = Math.max(0, totalMs - pauseTotal);
  const weights = actions.map(actionWeight);
  const totalWeight = weights.reduce((a, b) => a + b, 0) || 1;

  return actions.map((action, i) => {
    if (action.type === "pause") return action.duration * 1000;
    return (weights[i] / totalWeight) * available;
  });
}

import { Txt, Rect, Line, Img } from "@revideo/2d";
import { all, createRef, waitFor } from "@revideo/core";
import type { View2D } from "@revideo/2d";
import { BoardAction, Segment, SegmentAudio, allocateTime } from "../../types.js";
import { ElementRegistry, ElementEntry } from "../registry.js";

// ── Layout state ───────────────────────────────

const BOARD_PADDING = 80;
const LINE_HEIGHT = 60;
const FONT_SIZE = 36;
const FORMULA_HEIGHT = 80;
const BOARD_WIDTH = 1920;
const BOARD_HEIGHT = 1080;

let cursorX = BOARD_PADDING;
let cursorY = BOARD_PADDING + LINE_HEIGHT;
let formulaMap: Record<string, string> = {};
let segmentIdx = 0;
let actionIdx = 0;
const registry = new ElementRegistry();

function resetCursor() {
  cursorX = BOARD_PADDING;
  cursorY = BOARD_PADDING + LINE_HEIGHT;
}

function advanceCursor(height: number) {
  cursorY += height + 20;
  if (cursorY > BOARD_HEIGHT - BOARD_PADDING) {
    cursorY = BOARD_HEIGHT - BOARD_PADDING;
  }
}

// ── Render one action ──────────────────────────

function* renderAction(
  view: View2D,
  action: BoardAction,
  durationMs: number
) {
  const durationS = durationMs / 1000;

  switch (action.type) {
    case "write_text": {
      const id = action.id ?? registry.autoId("text");
      const ref = createRef<Txt>();
      const x = cursorX;
      const y = cursorY;

      view.add(
        <Txt
          ref={ref}
          text={""}
          fill={"#f0f0e8"}
          fontSize={FONT_SIZE}
          fontFamily={"'IBM Plex Sans', sans-serif"}
          x={x - BOARD_WIDTH / 2 + 200}
          y={y - BOARD_HEIGHT / 2}
          opacity={0}
        />
      );

      // Typewriter effect: fade in + text reveal
      yield* all(
        ref().opacity(1, 0.2),
        ref().text(action.text, durationS * 0.8)
      );

      const entry: ElementEntry = {
        id,
        type: "text",
        x: x - BOARD_WIDTH / 2 + 200,
        y: y - BOARD_HEIGHT / 2,
        width: action.text.length * FONT_SIZE * 0.5,
        height: LINE_HEIGHT,
      };
      registry.register(entry);
      advanceCursor(LINE_HEIGHT);
      break;
    }

    case "show_formula": {
      const id = action.id ?? registry.autoId("formula");
      const x = 0; // centered
      const y = cursorY - BOARD_HEIGHT / 2;

      // Check for pre-rendered SVG from Node.js MathJax
      const svgKey = `${segmentIdx}-${actionIdx}`;
      const svgDataUri = formulaMap[svgKey];

      if (svgDataUri) {
        // Real LaTeX rendering via pre-rendered SVG
        const ref = createRef<Img>();
        view.add(
          <Img
            ref={ref}
            src={svgDataUri}
            height={FORMULA_HEIGHT}
            x={x}
            y={y}
            opacity={0}
          />
        );

        yield* ref().opacity(1, durationS * 0.4);
        yield* waitFor(durationS * 0.6);
      } else {
        // Fallback: plain text
        const ref = createRef<Txt>();
        view.add(
          <Txt
            ref={ref}
            text={""}
            fill={"#ffe066"}
            fontSize={36}
            fontFamily={"'IBM Plex Mono', monospace"}
            x={x}
            y={y}
            opacity={0}
          />
        );

        yield* all(
          ref().opacity(1, 0.3),
          ref().text(action.latex, durationS * 0.7)
        );
        yield* waitFor(durationS * 0.3);
      }

      const entry: ElementEntry = {
        id,
        type: "formula",
        x,
        y,
        width: FORMULA_HEIGHT * 4, // approximate width for arrows
        height: FORMULA_HEIGHT,
      };
      registry.register(entry);
      advanceCursor(FORMULA_HEIGHT);
      break;
    }

    case "draw_arrow": {
      const fromEl = registry.get(action.from);
      const toEl = registry.get(action.to);
      if (!fromEl || !toEl) {
        yield* waitFor(durationS);
        break;
      }

      const ref = createRef<Line>();
      view.add(
        <Line
          ref={ref}
          points={[
            [fromEl.x + fromEl.width / 2, fromEl.y + fromEl.height],
            [toEl.x + toEl.width / 2, toEl.y - 10],
          ]}
          stroke={"#f0f0e8"}
          lineWidth={2}
          endArrow
          arrowSize={12}
          opacity={0}
        />
      );

      yield* ref().opacity(1, durationS);
      break;
    }

    case "highlight": {
      const el = registry.get(action.target);
      if (!el) {
        yield* waitFor(durationS);
        break;
      }

      const ref = createRef<Rect>();
      const color = action.color === "red" ? "#ff6b6b44" : "#ffe06644";

      view.add(
        <Rect
          ref={ref}
          x={el.x}
          y={el.y}
          width={el.width + 20}
          height={el.height + 10}
          fill={color}
          radius={4}
          opacity={0}
        />
      );

      yield* ref().opacity(1, durationS * 0.5);
      yield* waitFor(durationS * 0.5);
      break;
    }

    case "erase": {
      if (action.target === "all") {
        yield* waitFor(durationS * 0.3);
        for (const child of view.children()) {
          child.remove();
        }
        registry.clear();
        resetCursor();
        yield* waitFor(durationS * 0.7);
      } else {
        registry.remove(action.target);
        yield* waitFor(durationS);
      }
      break;
    }

    case "pause": {
      yield* waitFor(durationS);
      break;
    }
  }
}

// ── Render all segments ────────────────────────

export function* renderBoard(
  view: View2D,
  segments: Segment[],
  segmentAudios: SegmentAudio[],
  formulas?: Record<string, string>
) {
  resetCursor();
  formulaMap = formulas ?? {};

  for (let i = 0; i < segments.length; i++) {
    segmentIdx = i;
    const segment = segments[i];
    const audio = segmentAudios[i];
    if (!audio) continue;

    const durations = allocateTime(segment.board, audio.durationMs);

    for (let j = 0; j < segment.board.length; j++) {
      actionIdx = j;
      yield* renderAction(view, segment.board[j], durations[j]);
    }
  }
}

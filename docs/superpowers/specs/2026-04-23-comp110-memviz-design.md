# COMP110 Memory Diagram Viewer — Design Spec

**Date**: 2026-04-23  
**Author**: opus-0423a (Claude Opus 4.7)  
**Status**: Approved by user ("你做吧"), proceeding to implementation.

## Goal

Interactive web tool that renders Python memory diagrams following the exact conventions taught in UNC COMP110 (Spring 2026 site: https://comp110-26s.github.io/). Target: replace the static `.jpg` diagrams in QZ00 practice quizzes with a live, step-through viewer that can be iframe-embedded into the course site.

## Scope (MVP, 5 must-have features)

1. **Code editor + Run** — CodeMirror 6, Python syntax highlighting, v0 subset
2. **Step-by-step playback** — prev/next buttons + auto-play, highlight current line
3. **Error visualization** — NameError / arg-count mismatch shown as red banner + pointed line
4. **iframe embed mode** — `?embed=1` URL param hides header/footer for clean embedding
5. **Preloaded problem library** — 7 QZ00 problems one-click loadable

Out of scope (v2): URL-share, responsive mobile, answer-compare, dark mode.

## Python v0 Subset (supported constructs)

Strictly matches `memory_diagrams_v0.pdf` rules:

- Function definitions (with type annotations, docstrings — docstrings ignored)
- Function calls (keyword args only, matching COMP110 style)
- Return statements
- `print()` (single argument, goes to Output column)
- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Integer / float / string literals
- String operations: `+`, `len()`, indexing `s[i]`, `str()`, `int()`
- Name resolution (current frame → globals → NameError)
- Comments (`#`) and docstrings — ignored

**Not supported** (v0 excludes): classes, lists/dicts, `if`/`while`/`for`, imports, exceptions, mutation, closures.

## Diagram Model (mirrors COMP110 rules)

Three columns:

```
┌──────────────────┬──────────────────┬──────────────────┐
│ Function Call    │      Heap        │  Printed Output  │
│     Stack        │                  │                  │
│                  │  ID:0 "Fn L1-3"  │  14              │
│  ┌─────────┐     │  ID:1 "Fn L5-6"  │  31              │
│  │ frame2  │     │                  │                  │
│  │ RA: 12  │     │                  │                  │
│  │ RV: 7   │     │                  │                  │
│  │ x=3,y=4 │     │                  │                  │
│  ├─────────┤     │                  │                  │
│  │ Globals │     │                  │                  │
│  │ f→ID:0  │     │                  │                  │
│  └─────────┘     │                  │                  │
└──────────────────┴──────────────────┴──────────────────┘
```

State snapshot per step:

```ts
type Snapshot = {
  step: number;
  currentLine: number;
  stack: Frame[];        // frames[0] = Globals, last = active
  heap: HeapObject[];    // ID:0, ID:1, ...
  output: string[];      // printed lines
  error?: string;        // NameError, etc.
};

type Frame = {
  name: "Globals" | string;
  returnAddress?: number;
  returnValue?: Value;
  bindings: Record<string, Value>;
};

type Value =
  | { kind: "int"; v: number }
  | { kind: "float"; v: number }
  | { kind: "str"; v: string }
  | { kind: "ref"; id: number };  // heap ID reference

type HeapObject = {
  id: number;
  kind: "function";
  name: string;
  lineStart: number;
  lineEnd: number;
};
```

## Architecture

```
┌──────────────────────────────────────────────────┐
│                 App.tsx (root)                   │
├──────────────────────────────────────────────────┤
│ Header (hidden in ?embed=1)                      │
│ ┌──────────────┬──────────────────────────────┐  │
│ │ CodeEditor   │  DiagramCanvas               │  │
│ │ (CodeMirror) │  ┌────┬────┬────┐            │  │
│ │              │  │stk │heap│out │            │  │
│ │ [Run]        │  └────┴────┴────┘            │  │
│ │ [Problems ▾] │  ← Step: 3/42 →  [▶ auto]    │  │
│ └──────────────┴──────────────────────────────┘  │
│ Footer (hidden in ?embed=1)                      │
└──────────────────────────────────────────────────┘
```

### Module boundaries

| Module | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `interpreter/tokenizer.ts` | Source → tokens | `string` | `Token[]` |
| `interpreter/parser.ts` | Tokens → AST | `Token[]` | `Program` AST |
| `interpreter/evaluator.ts` | AST → snapshot sequence | `Program` | `Snapshot[]` |
| `components/CodeEditor.tsx` | Edit source | — | `onChange(source)` |
| `components/DiagramCanvas.tsx` | Render snapshot | `Snapshot` | — |
| `components/StepControl.tsx` | Navigate snapshots | `total, current` | `onStep(n)` |
| `data/qz00Problems.ts` | 7 preloaded problems | — | `Problem[]` |

Data flow: `source → Snapshot[]` (pure function, runs on Run click) → array stored in state → current index selected by StepControl → DiagramCanvas renders snapshot at that index.

### Key design decisions

1. **Mini-interpreter over Pyodide**: v0 rules ARE a simplified Python semantics. Implementing them directly gives perfect pedagogical alignment, 0 WASM load, instant eval.
2. **Snapshots are immutable** — "stepping back" is just reading an earlier array index. No rollback logic needed.
3. **No React Flow**: 3-column layout with flexbox + SVG arrows (heap references). React Flow is overkill and adds 200KB.
4. **CodeMirror 6 over Monaco**: 400KB vs 2MB, modern tree-shakable API.
5. **Vite + React + TypeScript, no SSR**: static site, deploys anywhere, simplest toolchain.

## Error Handling

- NameError: render red banner "NameError on line N: name 'x' not defined"
- Function call error: "Function Call Error on Line N: expected (a, b) got (a)"
- Parse error: "SyntaxError on line N: unexpected token"
- Unsupported construct: "NotSupportedInV0: <construct> not part of COMP110 v0 subset"

All errors are terminal — evaluator returns snapshots up to the error + a final error snapshot.

## Testing

- Unit tests per interpreter stage (tokenizer, parser, evaluator) — Vitest
- Snapshot-compare test: for each of the 7 QZ00 problems, verify `Snapshot[]` last element matches expected output
- Playwright end-to-end: load app → paste code → click Run → step through → verify final render

## Deployment

- `vite build` → static `dist/` folder
- `vercel deploy --prod` from project root
- Target URL: `comp110-memviz.vercel.app` (default) — can be custom-domained later
- Headers: `Content-Security-Policy: frame-ancestors 'self' https://comp110-26s.github.io https://*.github.io` (so it can be iframed from the course site but not from random attacker sites)

## Visual Style

Pending subagent research return. Default until then: neutral light theme, system fonts. Will refactor once brand tokens arrive.

## Build Sequence

1. Scaffold Vite project + deps
2. Interpreter (tokenizer → parser → evaluator) + unit tests for QZ00 calzones example
3. DiagramCanvas static render (given a snapshot, draw it)
4. CodeEditor + StepControl + wire up
5. Load 7 QZ00 problems
6. iframe embed mode (URL param)
7. Apply COMP110 visual style (when research returns)
8. Playwright e2e
9. Deploy to Vercel

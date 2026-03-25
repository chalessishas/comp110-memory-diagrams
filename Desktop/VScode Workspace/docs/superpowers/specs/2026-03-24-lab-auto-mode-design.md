# Lab: Writing Center Auto-Execution Mode

**Date**: 2026-03-24
**Status**: Draft (v3 — post self-criticism)
**Project**: ai-text-detector (Writing Center)

## Problem

Writing Center has 21 blocks that guide users through a structured writing process. Currently, users must manually walk through each block, doing all the writing themselves. Users who already know what they want to say but struggle with expression (e.g., ESL students) face unnecessary friction — they have good ideas but the mechanical writing is the bottleneck.

## Brand Narrative

> "You think, we write."

Blocks are AI behavior regulations, not teaching tools. When a user assembles blocks, they're defining what AI is allowed to do at each step. The same block set supports two execution modes:

- **Manual mode** (existing): User walks each block, writes everything themselves. AI guides, questions, gives feedback.
- **Auto mode** (Lab): AI executes each block according to its constraints. User provides ideas and makes decisions at checkpoints. AI handles the mechanical writing.

This is not ghostwriting — it's a regulated AI pipeline where the user is the decision-maker and every AI action is constrained by the block's definition.

## Design

### MVP Scope: TOEFL Preset

MVP supports auto-mode for the **TOEFL preset** (6 blocks: `thesis`, `outline`, `hook`, `draft`, `analyze`, `grammar`).

Why TOEFL, not Quick Write:
- Quick Write (draft → analyze → grammar) has zero "thinking" blocks — user only provides topic, AI does everything. That's ChatGPT, not "you think, we write."
- TOEFL has 3 chat blocks (thesis/outline/hook) as mandatory checkpoints where user provides ideas + 3 editor blocks (draft/analyze/grammar) that AI auto-executes. This is the literal mapping of "you think, we write."
- TOEFL has standardized quality criteria (score rubric), making it easy to evaluate output quality.

Other presets with unsupported block modes show "Auto-start" as disabled with tooltip.

### Two Block Behaviors in Auto Mode

| Block mode | Auto behavior |
|-----------|---------------|
| `editor` (draft, analyze, grammar) | **Auto-executable**: AI runs the block, produces output, advances. |
| `chat` (thesis, outline, hook, etc.) | **Idea checkpoint**: Pipeline pauses. UI shows the block's purpose and a text input. User provides their idea (thesis statement, outline points, hook concept). AI does NOT evaluate or challenge — it accepts and uses whatever the user provides. |
| `checklist` (peer-review, submit-ready, self-review) | Skipped in auto mode. |
| `lab` (voice-lab) | Skipped in auto mode. |

**Critical design principle for idea checkpoints:** The AI is an executor, not a coach. In auto mode, thesis checkpoint collects the user's thesis — it does not Socratic-question it. The user's ideas are the input; quality of expression is the AI's responsibility.

### Block `auto` Field

Each block in `blocks.ts` gets a new optional `auto` field:

```ts
interface BlockAutoConfig {
  needs: string[]        // Required inputs from user or previous block
  produces: string       // Key name for this block's output in PipelineState.outputs
  checkpoint: boolean    // Whether to pause for user input before proceeding
  promptKey: string      // Key into AUTO_PROMPTS map (prompts live in auto-prompts.ts)
}

// On BlockDefinition:
auto?: BlockAutoConfig | null  // null = not auto-executable
```

Prompts live in `auto-prompts.ts`, NOT in block definitions. `promptKey` is a lookup key. This avoids bloating `blocks.ts` and keeps a single source of truth for prompts.

### Block Output Schemas

```ts
// Idea checkpoints produce user input (not AI output)
interface IdeaCheckpointOutput {
  userInput: string    // What the user typed at the checkpoint
}

// draft block: produces a plain-text document
interface DraftOutput {
  document: string     // Plain text with paragraph breaks (\n\n)
  // Frontend wraps each paragraph in <p> tags for Tiptap
}

// analyze block: produces annotations + trait scores
interface AnalyzeOutput {
  annotations: Annotation[]    // Reuses existing Annotation type from types.ts
  traitScores: Record<string, number>
  summary: string
}

// grammar block: produces corrected document + diff
interface GrammarOutput {
  document: string             // Plain text (corrected)
  corrections: Array<{
    original: string
    corrected: string
    reason: string
  }>
}

// Pipeline outputs are typed by block
type PipelineOutputs = {
  thesis?: IdeaCheckpointOutput
  outline?: IdeaCheckpointOutput
  hook?: IdeaCheckpointOutput
  draft?: DraftOutput
  analyze?: AnalyzeOutput
  grammar?: GrammarOutput
}
```

**Plain text, not HTML.** Draft and grammar blocks output plain text with `\n\n` paragraph separators. The frontend converts to Tiptap-compatible HTML: `text.split('\n\n').map(p => '<p>' + escapeHtml(p) + '</p>').join('')`. This avoids the HTML-in-JSON escaping problem (DeepSeek producing escaped `<p>` tags inside JSON strings).

### Checkpoint UI

Two types of checkpoints:

**Idea checkpoint** (thesis, outline, hook):
```
┌─────────────────────────────┐
│  📝 What's your thesis?     │
│                             │
│  State your main argument   │
│  in 1-2 sentences.          │
│                             │
│  ┌───────────────────────┐  │
│  │ [text input area]     │  │
│  │                       │  │
│  └───────────────────────┘  │
│                             │
│  [▶ Continue]               │
│  [⏹ Stop here]              │
└─────────────────────────────┘
```

**Review checkpoint** (after auto blocks):
```
┌─────────────────────────────┐
│  ✅ Draft complete           │
│                             │
│  AI wrote a 350-word essay  │
│  based on your thesis and   │
│  outline.                   │
│                             │
│  Review the document, then: │
│                             │
│  [▶ Continue to 七维分析]    │
│  [✏️ Edit document]          │
│  [⏹ Stop here]              │
│                             │
│  ▸ What AI did (expand)     │
└─────────────────────────────┘
```

Actions:
- **Continue**: Accept output, advance to next block
- **Edit**: Unlock editor for manual changes. Pipeline pauses. User clicks "Resume" when done.
- **Stop**: End pipeline early. All output so far is preserved.

No backward navigation in MVP.

### Execution Engine: `AutoExecutor`

New component `AutoExecutor.tsx` — a state machine that runs blocks sequentially:

```
States: idle → checkpoint → executing → checkpoint → ... → done
                                                     ↘ cancelled
                                             error → (retry)
```

Note: pipeline STARTS with a checkpoint (thesis), not an execution. First block in TOEFL is a chat block.

```ts
interface PipelineState {
  blocks: BlockInstance[]
  currentIndex: number
  outputs: PipelineOutputs
  status: 'idle' | 'executing' | 'checkpoint' | 'done' | 'cancelled' | 'error'
  document: string              // The evolving article content (HTML for Tiptap)
  language: string              // 'en' | 'zh' — set at pipeline start, passed to all prompts
  executionLog: Array<{
    blockType: string
    dialogue: string
    timestamp: number
  }>
}
```

**Editor behavior during execution:**
- `status: 'executing'` → Tiptap editor is **read-only**
- `status: 'checkpoint'` → editor is read-only by default; clicking "Edit" unlocks it
- `status: 'done' | 'cancelled'` → editor is fully editable

**Error recovery:**
- If API call fails → status becomes `'error'`, show error + **Retry** button
- Retry re-runs the current block with the same inputs
- User can also Stop from error state to keep partial output

### UI Changes

**Workbench**: After assembling blocks, two buttons appear:
- "Start writing" → existing manual mode (no change)
- "Auto-start" → enters auto execution mode (enabled only for TOEFL preset in MVP; other presets show disabled tooltip)

**Entry validation:** Auto-start requires topic to be non-empty. Genre defaults to the preset's natural genre (TOEFL → "academic").

**Auto mode renders as a completely separate branch in WritingCenter.tsx:**
```tsx
if (executionMode === 'auto') {
  return <AutoExecutor board={board} genre={genre} topic={topic} language={language} ... />
}
// else: existing manual mode rendering (untouched)
```

**Auto mode layout** (reuses existing split-pane):

```
┌─ Block progress bar ───────────────────────────────────────┐
│ [✅ thesis] → [✅ outline] → [✅ hook] → [🔄 draft] → ...  │
├────────────────────────────┬────────────────────────────────┤
│                            │                                │
│  Document Area             │  Execution Area                │
│  (Tiptap editor, reused)   │                                │
│                            │  Idea input OR block status     │
│  READ-ONLY during          │  Checkpoint controls            │
│  execution                 │                                │
│                            │  Collapsible execution history  │
│  Editable at checkpoints   │                                │
│  (after clicking Edit)     │                                │
├────────────────────────────┴────────────────────────────────┤
│  Status bar: "Your idea → AI draft (4/6)" │ 350 words │ ⏹  │
└─────────────────────────────────────────────────────────────┘
```

### API

Single new action added to existing `/api/writing-assist` route. **Non-streaming for MVP.**

```ts
// Request
interface AutoExecuteRequest {
  action: "auto-execute"
  blockType: "draft" | "analyze" | "grammar"  // Only auto-executable blocks call API
  genre: string
  topic: string
  language: string              // 'en' | 'zh'
  document?: string             // Current document state (plain text)
  previousOutputs?: PipelineOutputs  // Context from earlier blocks (includes user's thesis/outline/hook)
}

// Response (non-streaming, JSON)
interface AutoExecuteResponse {
  dialogue: string              // Explanation of what AI did
  documentUpdate?: string       // Plain text output (draft/grammar blocks)
  analysisResult?: AnalyzeOutput  // Only for analyze block
  grammarResult?: GrammarOutput   // Only for grammar block
}
```

**Idea checkpoints (thesis/outline/hook) do NOT call the API.** They just collect user input and store it in `PipelineOutputs`. The user's ideas are passed to subsequent auto blocks via `previousOutputs`.

**Analyze block in auto mode** skips the 100-word minimum check. The draft prompt guarantees ≥ 200 words, but even if it somehow produces less, auto-mode analyze should still attempt analysis rather than hard-failing the pipeline.

### What Changes vs. What Doesn't

**Changed files:**
- `blocks.ts` — Add `auto` field to 6 TOEFL blocks; other 15 get `auto: null`
- `WritingCenter.tsx` — Add `executionMode` state + `language` state + separate render branch (~25 lines added)
- New: `AutoExecutor.tsx` — Execution engine + checkpoint UI + progress bar (~400 lines)
- New: `auto-prompts.ts` — Auto-mode system prompts for 3 auto blocks (draft/analyze/grammar) + checkpoint descriptions for 3 idea blocks
- `route.ts` — Add `auto-execute` action handler (non-streaming, `json_object` for analyze/grammar, plain `text` for draft)
- `Workbench.tsx` — Add "Auto-start" button (enabled only for TOEFL preset)
- `types.ts` — Add `BlockAutoConfig`, `PipelineState`, `PipelineOutputs`, `IdeaCheckpointOutput`, `AutoExecuteRequest/Response`

**Unchanged:**
- All 21 block definitions (existing fields untouched)
- Manual mode behavior (all existing interactions preserved)
- Editor.tsx (reused as-is, `disabled` prop already supported)
- ChatPanel.tsx, BlockChat.tsx, ChecklistPanel.tsx (manual mode only)
- LabPanel.tsx (existing temperature comparison lab)
- Storage/profile system
- Analyze/expand/guide API actions

### Known MVP Limitations

- **No pipeline persistence**: If user refreshes mid-pipeline, progress is lost. Acceptable for MVP (~90s total).
- **No backward navigation**: User must Stop and re-run.
- **TOEFL preset only**: Other presets show "Auto-start" disabled.
- **No streaming**: Draft block may take 10-15s with no incremental feedback.
- **No language auto-detection**: User must select language manually.

### Not in MVP

Deferred to post-validation:
- Auto configs for remaining 15 blocks
- Quick Write auto mode (simpler onboarding path)
- Streaming for draft block (SSE)
- Pipeline state persistence to localStorage
- Backward navigation / re-run from block N

### Success Criteria

1. User selects TOEFL preset, clicks "Auto-start", provides topic
2. Pipeline pauses at thesis/outline/hook — user provides ideas at each checkpoint
3. AI drafts article based on user's ideas, analyzes it, fixes grammar — all automatically
4. Review checkpoints after each auto block let user review, edit, continue, or stop
5. Manual mode is completely unaffected — zero regressions
6. Total execution time: under 60 seconds for 3 auto blocks (excluding user input time at checkpoints)

### Risks

| Risk | Mitigation |
|------|-----------|
| Auto-mode prompts need tuning | Only 3 auto prompts for MVP; iterate quickly |
| Non-streaming draft feels slow (10-15s) | Show spinner + "Writing your draft based on your thesis..." status |
| WritingCenter.tsx already 889 lines | AutoExecutor is separate component; WC gets ~25 new lines |
| Draft output format unpredictable | Draft uses plain text (no JSON), analyze/grammar use `json_object` mode |
| User provides minimal input at checkpoints | AI works with whatever it gets — quality of expression is AI's job, ideas are user's |

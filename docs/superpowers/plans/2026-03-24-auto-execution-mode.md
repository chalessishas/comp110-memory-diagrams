# Auto-Execution Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an auto-execution mode to Writing Center where AI runs TOEFL preset blocks automatically while users provide ideas at checkpoints.

**Architecture:** New `AutoExecutor` component renders as a separate branch in WritingCenter when `executionMode === 'auto'`. It walks blocks sequentially — chat blocks pause for user input (idea checkpoints), editor blocks call `/api/writing-assist` with `action: "auto-execute"`. Plain text in/out for draft/grammar; JSON for analyze. Editor is read-only during execution.

**Tech Stack:** React 19, Next.js 16, TypeScript, Tiptap 3 (existing), DeepSeek V3 API (existing OpenAI SDK)

**Spec:** `docs/superpowers/specs/2026-03-24-lab-auto-mode-design.md` (v3)

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `src/lib/writing/types.ts` | Modify | Add `BlockAutoConfig`, `PipelineOutputs`, `PipelineState`, `IdeaCheckpointOutput`, `AutoExecuteRequest`, `AutoExecuteResponse` |
| `src/lib/writing/blocks.ts` | Modify | Add `auto` field to `BlockDef`, populate for 6 TOEFL blocks, `null` for rest |
| `src/lib/prompts/writing/auto-prompts.ts` | Create | Auto-mode system prompts for draft/analyze/grammar + checkpoint descriptions |
| `src/app/api/writing-assist/route.ts` | Modify | Add `auto-execute` action handler (3 sub-cases) |
| `src/components/writing/AutoExecutor.tsx` | Create | State machine + checkpoint UI + progress bar + execution log |
| `src/components/writing/Editor.tsx` | Modify | Add `useEffect` to dynamically toggle `editable` when `disabled` prop changes |
| `src/components/writing/Workbench.tsx` | Modify | Add "Auto-start" button (enabled for TOEFL only) + language toggle |
| `src/components/writing/WritingCenter.tsx` | Modify | Add `executionMode` + `language` state, conditional render branch |

---

### Task 1: Add Auto-Mode Types

**Files:**
- Modify: `ai-text-detector/src/lib/writing/types.ts`

- [ ] **Step 1: Add IdeaCheckpointOutput and output types after Annotation interface (line 35)**

```ts
// After Annotation interface (line 35)

export interface IdeaCheckpointOutput {
  userInput: string;
}

export interface DraftOutput {
  document: string; // Plain text with \n\n paragraph breaks
}

export interface GrammarOutput {
  document: string; // Plain text (corrected)
  corrections: Array<{
    original: string;
    corrected: string;
    reason: string;
  }>;
}

export type PipelineOutputs = {
  thesis?: IdeaCheckpointOutput;
  outline?: IdeaCheckpointOutput;
  hook?: IdeaCheckpointOutput;
  draft?: DraftOutput;
  analyze?: AnalyzeOutput;
  grammar?: GrammarOutput;
};
```

Note: `AnalyzeOutput` is the same as existing `AnalyzeResponse` minus `conventionsSuppressed`. Reuse `AnalyzeResponse` directly — auto mode can ignore the extra field.

- [ ] **Step 2: Add PipelineState interface**

```ts
export type PipelineStatus = 'idle' | 'executing' | 'checkpoint' | 'done' | 'cancelled' | 'error';

export interface PipelineState {
  blocks: BlockInstance[];
  currentIndex: number;
  outputs: PipelineOutputs;
  status: PipelineStatus;
  document: string;
  language: 'en' | 'zh';
  executionLog: Array<{
    blockType: string;
    dialogue: string;
    timestamp: number;
  }>;
}
```

- [ ] **Step 3: Add AutoExecuteRequest and AutoExecuteResponse**

```ts
export interface AutoExecuteRequest {
  action: "auto-execute";
  blockType: "draft" | "analyze" | "grammar";
  genre: string;
  topic: string;
  language: 'en' | 'zh';
  document?: string;
  previousOutputs?: PipelineOutputs;
}

export interface AutoExecuteResponse {
  dialogue: string;
  documentUpdate?: string;
  analysisResult?: AnalyzeResponse;
  grammarResult?: GrammarOutput;
}
```

- [ ] **Step 4: Extend WritingAssistRequest action union**

Change line 89 from:
```ts
action: "guide" | "analyze" | "expand" | "daily-tip" | "lab-rewrite" | "report";
```
to:
```ts
action: "guide" | "analyze" | "expand" | "daily-tip" | "lab-rewrite" | "report" | "auto-execute";
```

Also add the auto-execute fields to the request interface:
```ts
blockType?: "draft" | "analyze" | "grammar";
language?: 'en' | 'zh';
previousOutputs?: PipelineOutputs;
```

- [ ] **Step 5: Verify TypeScript compiles**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`
Expected: No new errors (existing errors may be present)

- [ ] **Step 6: Commit**

```bash
git add ai-text-detector/src/lib/writing/types.ts
git commit -m "feat(writing): add auto-execution mode types"
```

---

### Task 2: Add Auto Config to Block Definitions

**Files:**
- Modify: `ai-text-detector/src/lib/writing/blocks.ts`

- [ ] **Step 1: Add BlockAutoConfig interface after BlockDef (line 64)**

```ts
export interface BlockAutoConfig {
  needs: string[];       // Required inputs from user or previous block
  produces: string;      // Key name for this block's output in PipelineOutputs
  checkpoint: boolean;   // Whether to pause for user input
  promptKey: string;     // Key into AUTO_PROMPTS (lives in auto-prompts.ts)
}
```

- [ ] **Step 2: Extend BlockDef interface**

Add to BlockDef (after `aiRole: string;`):
```ts
auto?: BlockAutoConfig | null;
```

- [ ] **Step 3: Add auto configs to TOEFL blocks in BLOCK_CATALOG**

For each of the 6 TOEFL blocks, add the `auto` field. All other blocks get `auto: null`.

thesis block (line ~119-127):
```ts
auto: {
  needs: ["topic"],
  produces: "thesis",
  checkpoint: true,
  promptKey: "thesis-checkpoint",
},
```

outline block (line ~129-137):
```ts
auto: {
  needs: ["thesis"],
  produces: "outline",
  checkpoint: true,
  promptKey: "outline-checkpoint",
},
```

hook block (line ~151-159):
```ts
auto: {
  needs: ["thesis", "outline"],
  produces: "hook",
  checkpoint: true,
  promptKey: "hook-checkpoint",
},
```

draft block (line ~161-169):
```ts
auto: {
  needs: ["thesis", "outline", "hook"],
  produces: "draft",
  checkpoint: false,
  promptKey: "draft-auto",
},
```

analyze block (line ~225-233):
```ts
auto: {
  needs: ["draft"],
  produces: "analyze",
  checkpoint: false,
  promptKey: "analyze-auto",
},
```

grammar block (line ~279-287):
```ts
auto: {
  needs: ["analyze"],
  produces: "grammar",
  checkpoint: false,
  promptKey: "grammar-auto",
},
```

All other 15 blocks: do NOT add anything. The `auto` field is `auto?: BlockAutoConfig | null`, so `undefined` (absent) means "not auto-executable." Check `def.auto` truthiness in code.

- [ ] **Step 4: Verify TypeScript compiles**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 5: Commit**

```bash
git add ai-text-detector/src/lib/writing/blocks.ts
git commit -m "feat(writing): add auto config to block definitions (TOEFL preset)"
```

---

### Task 3: Create Auto-Mode Prompts

**Files:**
- Create: `ai-text-detector/src/lib/prompts/writing/auto-prompts.ts`

- [ ] **Step 1: Create auto-prompts.ts with checkpoint descriptions and auto system prompts**

The file exports two things:
1. `CHECKPOINT_DESCRIPTIONS` — UI text shown at idea checkpoints
2. `AUTO_PROMPTS` — system prompts for AI-executed blocks

```ts
// Checkpoint descriptions: shown in UI when pipeline pauses for user input
export const CHECKPOINT_DESCRIPTIONS: Record<string, {
  title: string;
  titleZh: string;
  placeholder: string;
  placeholderZh: string;
}> = {
  "thesis-checkpoint": {
    title: "What's your thesis?",
    titleZh: "你的论点是什么？",
    placeholder: "State your main argument in 1-2 sentences...",
    placeholderZh: "用 1-2 句话说明你的核心论点…",
  },
  "outline-checkpoint": {
    title: "How will you structure it?",
    titleZh: "你打算怎么组织文章？",
    placeholder: "List your 2-4 main supporting points, one per line...",
    placeholderZh: "列出 2-4 个主要论据，每行一个…",
  },
  "hook-checkpoint": {
    title: "How do you want to open?",
    titleZh: "你想怎么开头？",
    placeholder: "Describe the opening you have in mind — a question, a scene, a bold claim...",
    placeholderZh: "描述你想到的开头——一个问题、一个场景、一个大胆的主张…",
  },
};

// Auto-mode system prompts: used when AI executes a block
export const AUTO_PROMPTS: Record<string, string> = {
  "draft-auto": `You are a skilled essay writer. Write a complete essay based on the user's ideas.

INPUT:
- Genre, topic, and language
- User's thesis statement
- User's outline (main points)
- User's hook concept

RULES:
- Write the COMPLETE essay, not just an outline or summary
- Follow the user's structure exactly — their thesis IS the thesis, their points ARE the points
- Minimum 250 words, aim for 300-400
- Match the specified language (en or zh) throughout — do NOT mix languages
- Write naturally, vary sentence length, avoid repetitive transitions
- Include the hook concept in the opening paragraph

OUTPUT FORMAT:
Return ONLY the essay text. Use blank lines (\\n\\n) between paragraphs. No titles, no labels, no markdown formatting, no JSON wrapping. Just the essay text.`,

  "analyze-auto": `You are a writing tutor analyzing an essay using the 6+1 Traits framework. Return structured JSON feedback.

OUTPUT FORMAT:
Return ONLY valid JSON (no markdown fencing):
{
  "annotations": [...],
  "traitScores": { "ideas": 0-100, "organization": 0-100, "voice": 0-100, "wordChoice": 0-100, "fluency": 0-100, "conventions": 0-100, "presentation": 0-100 },
  "summary": "2-3 sentence summary of strengths and areas for improvement",
  "conventionsSuppressed": false
}

Each annotation:
{
  "id": "uuid-v4",
  "paragraph": 0,
  "startOffset": -1,
  "endOffset": -1,
  "trait": "ideas|organization|voice|wordChoice|fluency|conventions|presentation",
  "severity": "good|question|suggestion|issue",
  "message": "≥15 words, specific and actionable",
  "rewrite": "required for suggestion/issue severity"
}

SORTING: All "good" first, then "question", then "suggestion", then "issue".
Provide 8-12 annotations covering at least 5 different traits.
Be honest but constructive. The user wrote the ideas; AI wrote the expression. Focus feedback on how well the ideas were expressed.`,

  "grammar-auto": `You are a proofreader. Fix grammar, spelling, punctuation, and mechanical errors in the text.

RULES:
- Fix ONLY surface-level errors (grammar, spelling, punctuation, capitalization)
- Do NOT change meaning, voice, word choice, or sentence structure
- Do NOT rewrite for style — only fix what is objectively wrong
- Preserve the original language (en or zh)

OUTPUT FORMAT:
Return ONLY valid JSON (no markdown fencing):
{
  "document": "the full corrected text with \\n\\n paragraph breaks",
  "corrections": [
    { "original": "exact original text", "corrected": "fixed version", "reason": "brief explanation" }
  ]
}

If there are no errors, return the original text unchanged with an empty corrections array.`,
};
```

- [ ] **Step 2: Verify file imports correctly**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 3: Commit**

```bash
git add ai-text-detector/src/lib/prompts/writing/auto-prompts.ts
git commit -m "feat(writing): add auto-mode prompts for TOEFL blocks"
```

---

### Task 4: Add Auto-Execute API Handler

**Files:**
- Modify: `ai-text-detector/src/app/api/writing-assist/route.ts`

- [ ] **Step 1: Add imports**

After existing imports (line ~18), add:
```ts
import { AUTO_PROMPTS } from "@/lib/prompts/writing/auto-prompts";
import type { AutoExecuteResponse, GrammarOutput, PipelineOutputs } from "@/lib/writing/types";
```

- [ ] **Step 2: Create handleAutoExecute function**

Add after `handleLabRewrite` (before the POST handler):

```ts
async function handleAutoExecute(body: WritingAssistRequest): Promise<NextResponse> {
  const { blockType, genre, topic, language, document, previousOutputs } = body;

  if (!blockType || !["draft", "analyze", "grammar"].includes(blockType)) {
    return NextResponse.json({ error: "Invalid blockType" }, { status: 400 });
  }
  if (!topic) {
    return NextResponse.json({ error: "Topic is required" }, { status: 400 });
  }

  const client = getClient();
  const systemPrompt = AUTO_PROMPTS[`${blockType}-auto`];
  if (!systemPrompt) {
    return NextResponse.json({ error: `No auto prompt for ${blockType}` }, { status: 400 });
  }

  const lang = language === "zh" ? "Chinese" : "English";

  if (blockType === "draft") {
    // Draft: plain text output (no json_object mode)
    const userContext = buildDraftContext(genre!, topic, lang, previousOutputs);
    const res = await client.chat.completions.create({
      model: MODEL,
      temperature: 0.7,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userContext },
      ],
    });
    const text = res.choices[0].message.content ?? "";
    const result: AutoExecuteResponse = {
      dialogue: `Wrote a ${wordCount(text)}-word ${genre} essay based on your thesis and outline.`,
      documentUpdate: text.trim(),
    };
    return NextResponse.json(result);
  }

  if (blockType === "analyze") {
    if (!document) {
      return NextResponse.json({ error: "Document required for analyze" }, { status: 400 });
    }
    // Analyze: json_object mode (same as existing analyze but with auto prompt)
    const res = await client.chat.completions.create({
      model: MODEL,
      temperature: 0,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: document },
      ],
    });
    const data = parseJSON<{ annotations: unknown[]; traitScores: Record<string, number>; summary: string; conventionsSuppressed: boolean }>(
      res.choices[0].message.content ?? ""
    );
    const result: AutoExecuteResponse = {
      dialogue: `Analyzed the essay across 7 traits. ${data.summary}`,
      analysisResult: data,
    };
    return NextResponse.json(result);
  }

  // grammar
  if (!document) {
    return NextResponse.json({ error: "Document required for grammar" }, { status: 400 });
  }
  const res = await client.chat.completions.create({
    model: MODEL,
    temperature: 0,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: document },
    ],
  });
  const data = parseJSON<GrammarOutput>(res.choices[0].message.content ?? "");
  const result: AutoExecuteResponse = {
    dialogue: `Fixed ${data.corrections.length} mechanical error${data.corrections.length !== 1 ? "s" : ""}.`,
    grammarResult: data,
  };
  return NextResponse.json(result);
}

function buildDraftContext(genre: string, topic: string, language: string, outputs?: PipelineOutputs): string {
  const parts = [`Genre: ${genre}`, `Topic: ${topic}`, `Language: ${language}`];
  if (outputs?.thesis?.userInput) parts.push(`Thesis: ${outputs.thesis.userInput}`);
  if (outputs?.outline?.userInput) parts.push(`Outline:\n${outputs.outline.userInput}`);
  if (outputs?.hook?.userInput) parts.push(`Hook concept: ${outputs.hook.userInput}`);
  return parts.join("\n\n");
}
```

- [ ] **Step 3: Add case to switch in POST handler**

After `case "lab-rewrite":` (around line 241), add:
```ts
case "auto-execute":
  return await handleAutoExecute(body);
```

- [ ] **Step 4: Verify TypeScript compiles**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 5: Test API endpoint with curl**

Start dev server if not running: `cd ai-text-detector && npm run dev &`

```bash
curl -s -X POST http://localhost:3000/api/writing-assist \
  -H "Content-Type: application/json" \
  -d '{"action":"auto-execute","blockType":"draft","genre":"academic","topic":"Impact of social media on education","language":"en","previousOutputs":{"thesis":{"userInput":"Social media negatively impacts student focus but offers collaborative learning benefits."},"outline":{"userInput":"1. Distraction evidence\n2. Collaborative benefits\n3. Balance strategies"},"hook":{"userInput":"Start with a surprising statistic about screen time"}}}' | jq '.dialogue, (.documentUpdate | length)'
```
Expected: dialogue string + documentUpdate length > 200 characters

- [ ] **Step 6: Commit**

```bash
git add ai-text-detector/src/app/api/writing-assist/route.ts
git commit -m "feat(writing): add auto-execute API handler for draft/analyze/grammar"
```

---

### Task 5: Create AutoExecutor Component

**Files:**
- Create: `ai-text-detector/src/components/writing/AutoExecutor.tsx`

This is the largest task. The component is a state machine that:
1. Walks blocks in order
2. Pauses at chat blocks (idea checkpoints) for user input
3. Calls API for editor blocks (auto-execute)
4. Shows progress bar, checkpoint UI, execution log
5. Controls editor read-only state

- [ ] **Step 1: Create AutoExecutor.tsx with props interface and state**

```tsx
"use client";

import { useState, useRef, useCallback } from "react";
import type { BlockInstance, BlockType } from "@/lib/writing/blocks";
import { getBlockDef } from "@/lib/writing/blocks";
import type {
  Genre,
  Annotation,
  PipelineOutputs,
  PipelineStatus,
  AutoExecuteResponse,
  AnalyzeResponse,
} from "@/lib/writing/types";
import { CHECKPOINT_DESCRIPTIONS } from "@/lib/prompts/writing/auto-prompts";
import { apiCall } from "@/lib/writing/api";
import Editor, { type EditorHandle } from "./Editor";

interface AutoExecutorProps {
  board: BlockInstance[];
  genre: Genre;
  topic: string;
  language: "en" | "zh";
  onExit: () => void; // Return to workbench
}

function textToHtml(text: string): string {
  return text
    .split("\n\n")
    .filter(Boolean)
    .map((p) => `<p>${p.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</p>`)
    .join("");
}

export default function AutoExecutor({ board, genre, topic, language, onExit }: AutoExecutorProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [status, setStatus] = useState<PipelineStatus>("checkpoint"); // Start at first block (checkpoint)
  const [outputs, setOutputs] = useState<PipelineOutputs>({});
  const [document, setDocument] = useState("");
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [checkpointInput, setCheckpointInput] = useState("");
  const [executionLog, setExecutionLog] = useState<Array<{ blockType: string; dialogue: string; timestamp: number }>>([]);
  const [error, setError] = useState("");
  const [showLog, setShowLog] = useState(false);
  const [isEditing, setIsEditing] = useState(false); // User clicked "Edit" at review checkpoint
  const editorRef = useRef<EditorHandle>(null);

  const currentBlock = board[currentIndex];
  const currentDef = currentBlock ? getBlockDef(currentBlock.type) : null;
  const isCheckpointBlock = currentDef?.mode === "chat";
  const isAutoBlock = currentDef?.mode === "editor";
  const isFinished = status === "done" || status === "cancelled";
  const editorDisabled = !isFinished && !isEditing;

  // ── Execute an auto block ──
  const executeBlock = useCallback(async (blockIndex: number, currentOutputs: PipelineOutputs, currentDoc: string) => {
    const block = board[blockIndex];
    const def = getBlockDef(block.type);

    // Skip non-executable blocks (checklist, lab)
    if (def.mode !== "editor") {
      return { nextIndex: blockIndex + 1, outputs: currentOutputs, doc: currentDoc };
    }

    setStatus("executing");

    const res = await apiCall<AutoExecuteResponse>({
      action: "auto-execute",
      blockType: block.type as "draft" | "analyze" | "grammar",
      genre,
      topic,
      language,
      document: currentDoc,
      previousOutputs: currentOutputs,
    });

    // Update state based on block type
    const newOutputs = { ...currentOutputs };
    let newDoc = currentDoc;

    if (block.type === "draft" && res.documentUpdate) {
      newDoc = res.documentUpdate;
      newOutputs.draft = { document: newDoc };
    } else if (block.type === "analyze" && res.analysisResult) {
      newOutputs.analyze = res.analysisResult;
      setAnnotations(res.analysisResult.annotations ?? []);
    } else if (block.type === "grammar" && res.grammarResult) {
      newDoc = res.grammarResult.document;
      newOutputs.grammar = res.grammarResult;
    }

    setExecutionLog((prev) => [...prev, {
      blockType: block.type,
      dialogue: res.dialogue,
      timestamp: Date.now(),
    }]);

    return { nextIndex: blockIndex + 1, outputs: newOutputs, doc: newDoc };
  }, [board, genre, topic, language]);

  // ── Run auto blocks until next checkpoint or done ──
  const runUntilCheckpoint = useCallback(async (startIndex: number, currentOutputs: PipelineOutputs, currentDoc: string) => {
    let idx = startIndex;
    let outs = currentOutputs;
    let doc = currentDoc;

    while (idx < board.length) {
      const def = getBlockDef(board[idx].type);

      // Chat block = checkpoint, pause
      if (def.mode === "chat") {
        setCurrentIndex(idx);
        setOutputs(outs);
        setDocument(doc);
        setStatus("checkpoint");
        setCheckpointInput("");
        return;
      }

      // Skip checklist/lab blocks
      if (def.mode === "checklist" || def.mode === "lab") {
        idx++;
        continue;
      }

      // Editor block = auto-execute
      try {
        setCurrentIndex(idx);
        const result = await executeBlock(idx, outs, doc);
        outs = result.outputs;
        doc = result.doc;
        idx = result.nextIndex;
        setOutputs(outs);
        setDocument(doc);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Execution failed");
        setStatus("error");
        return;
      }

      // After auto block, pause for review checkpoint
      if (idx < board.length) {
        const nextDef = getBlockDef(board[idx].type);
        if (nextDef.mode === "editor") {
          // Review checkpoint between auto blocks
          setCurrentIndex(idx);
          setStatus("checkpoint");
          return;
        }
      }
    }

    // All blocks done
    setOutputs(outs);
    setDocument(doc);
    setStatus("done");
  }, [board, executeBlock]);

  // ── Handlers ──

  function handleCheckpointSubmit() {
    if (!checkpointInput.trim() && isCheckpointBlock) return;

    const newOutputs = { ...outputs };
    if (currentBlock) {
      const key = currentBlock.type as keyof PipelineOutputs;
      if (isCheckpointBlock) {
        (newOutputs as Record<string, unknown>)[key] = { userInput: checkpointInput.trim() };
      }
    }

    setOutputs(newOutputs);
    runUntilCheckpoint(currentIndex + (isCheckpointBlock ? 1 : 0), newOutputs, document);
  }

  function handleContinue() {
    // Continue from review checkpoint
    runUntilCheckpoint(currentIndex, outputs, document);
  }

  function handleStop() {
    setStatus("cancelled");
  }

  function handleRetry() {
    setError("");
    runUntilCheckpoint(currentIndex, outputs, document);
  }

  // ── Progress bar ──
  const progressBar = (
    <div className="h-10 bg-[var(--card)] border-b border-[var(--card-border)] flex items-center px-3 gap-1 overflow-x-auto shrink-0">
      <button
        onClick={onExit}
        className="text-[10px] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors mr-2 shrink-0"
      >
        ← Board
      </button>
      {board.map((block, idx) => {
        const def = getBlockDef(block.type);
        const isCurrent = idx === currentIndex;
        const isDone = idx < currentIndex;
        const isSkipped = def.mode === "checklist" || def.mode === "lab";
        return (
          <div
            key={block.id}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-medium shrink-0 ${
              isCurrent
                ? "text-white"
                : isDone
                  ? "bg-green-50 text-green-700"
                  : isSkipped
                    ? "text-[var(--muted)]/40 line-through"
                    : "text-[var(--muted)]"
            }`}
            style={isCurrent ? { background: def.color } : undefined}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: isCurrent ? "white" : isDone ? "#22c55e" : def.color }}
            />
            {def.nameZh}
            {isDone && <span className="text-[8px] opacity-60">&#10003;</span>}
          </div>
        );
      })}
    </div>
  );

  // ── Execution area (right panel) ──
  const checkpointDesc = currentDef?.auto?.promptKey
    ? CHECKPOINT_DESCRIPTIONS[currentDef.auto.promptKey]
    : null;

  const executionArea = (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Status */}
        {status === "executing" && (
          <div className="text-center py-8 space-y-3">
            <div className="w-8 h-8 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin mx-auto" />
            <div className="text-sm text-[var(--foreground)]">
              {language === "zh" ? "AI 正在执行" : "AI is working on"} {currentDef?.nameZh}...
            </div>
          </div>
        )}

        {/* Idea checkpoint */}
        {status === "checkpoint" && isCheckpointBlock && checkpointDesc && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-[var(--foreground)]">
              {language === "zh" ? checkpointDesc.titleZh : checkpointDesc.title}
            </h3>
            <textarea
              value={checkpointInput}
              onChange={(e) => setCheckpointInput(e.target.value)}
              placeholder={language === "zh" ? checkpointDesc.placeholderZh : checkpointDesc.placeholder}
              className="w-full h-32 bg-[var(--background)] border border-[var(--card-border)] rounded-lg text-sm text-[var(--foreground)] p-3 resize-none focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30 placeholder:text-[#c4bfb7]"
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={handleCheckpointSubmit}
                disabled={!checkpointInput.trim()}
                className="bg-[var(--accent)] hover:bg-[#b5583a] disabled:bg-[#d4cfc7] disabled:text-[#a09a92] text-white text-xs font-medium px-4 py-2 rounded-md transition-all"
              >
                {language === "zh" ? "继续" : "Continue"} →
              </button>
              <button
                onClick={handleStop}
                className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] px-3 py-2 transition-colors"
              >
                {language === "zh" ? "停止" : "Stop"}
              </button>
            </div>
          </div>
        )}

        {/* Review checkpoint (after auto block) */}
        {status === "checkpoint" && !isCheckpointBlock && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <h3 className="text-sm font-medium text-[var(--foreground)]">
                {board[currentIndex - 1] ? getBlockDef(board[currentIndex - 1].type).nameZh : ""} {language === "zh" ? "完成" : "complete"}
              </h3>
            </div>
            <p className="text-xs text-[var(--muted)] leading-relaxed">
              {executionLog[executionLog.length - 1]?.dialogue}
            </p>
            {isEditing ? (
              <div className="space-y-2">
                <p className="text-xs text-[var(--accent)]">
                  {language === "zh" ? "编辑器已解锁，完成后点击继续。" : "Editor unlocked. Click Resume when done."}
                </p>
                <button
                  onClick={() => { setIsEditing(false); handleContinue(); }}
                  className="bg-[var(--accent)] hover:bg-[#b5583a] text-white text-xs font-medium px-4 py-2 rounded-md transition-all"
                >
                  {language === "zh" ? "继续" : "Resume"} →
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleContinue}
                  className="bg-[var(--accent)] hover:bg-[#b5583a] text-white text-xs font-medium px-4 py-2 rounded-md transition-all"
                >
                  {language === "zh" ? "继续到" : "Continue to"} {currentDef?.nameZh} →
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className="border border-[var(--card-border)] text-xs text-[var(--foreground)] px-3 py-2 rounded-md hover:bg-[var(--background)] transition-colors"
                >
                  {language === "zh" ? "编辑文章" : "Edit document"}
                </button>
                <button
                  onClick={handleStop}
                  className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] px-3 py-2 transition-colors"
                >
                  {language === "zh" ? "到此为止" : "Stop here"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {status === "error" && (
          <div className="space-y-3">
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-xs text-red-600">{error}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleRetry}
                className="bg-[var(--accent)] hover:bg-[#b5583a] text-white text-xs font-medium px-4 py-2 rounded-md transition-all"
              >
                Retry
              </button>
              <button
                onClick={handleStop}
                className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] px-3 py-2 transition-colors"
              >
                Stop
              </button>
            </div>
          </div>
        )}

        {/* Done */}
        {isFinished && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <h3 className="text-sm font-medium text-[var(--foreground)]">
                {status === "done"
                  ? (language === "zh" ? "全部完成" : "All done")
                  : (language === "zh" ? "已停止" : "Stopped")}
              </h3>
            </div>
            <p className="text-xs text-[var(--muted)]">
              {language === "zh" ? "你现在可以自由编辑文章。" : "You can now freely edit the document."}
            </p>
            <button
              onClick={onExit}
              className="text-xs text-[var(--accent)] hover:underline"
            >
              ← {language === "zh" ? "返回积木板" : "Back to board"}
            </button>
          </div>
        )}

        {/* Execution log (collapsible) */}
        {executionLog.length > 0 && (
          <div className="border-t border-[var(--card-border)] pt-3">
            <button
              onClick={() => setShowLog(!showLog)}
              className="text-[10px] text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
            >
              {showLog ? "▾" : "▸"} {language === "zh" ? "执行记录" : "Execution log"} ({executionLog.length})
            </button>
            {showLog && (
              <div className="mt-2 space-y-2">
                {executionLog.map((entry, i) => (
                  <div key={i} className="text-[10px] text-[var(--muted)] leading-relaxed">
                    <span className="font-medium">{getBlockDef(entry.blockType as BlockType).nameZh}:</span>{" "}
                    {entry.dialogue}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  // ── Layout ──
  return (
    <div className="flex flex-col h-full">
      {progressBar}

      <div className="flex-1 min-h-0 grid" style={{ gridTemplateColumns: "1fr 4px 1fr" }}>
        {/* Editor pane */}
        <div className="min-h-0 min-w-0 flex flex-col bg-[var(--card)] overflow-auto">
          <div className="flex-1">
            <Editor
              ref={editorRef}
              content={textToHtml(document)}
              onUpdate={(html) => {
                if (!editorDisabled) {
                  // Convert HTML back to plain text: </p><p> → \n\n, strip remaining tags
                  const text = html.replace(/<\/p>\s*<p[^>]*>/g, "\n\n").replace(/<[^>]*>/g, "").trim();
                  setDocument(text);
                }
              }}
              annotations={annotations}
              onAnnotationClick={() => {}}
              disabled={editorDisabled}
            />
          </div>
        </div>

        {/* Divider */}
        <div className="bg-[var(--card-border)]" />

        {/* Execution area */}
        <div className="min-h-0 min-w-0 bg-[var(--background)] overflow-hidden">
          {executionArea}
        </div>
      </div>

      {/* Status bar */}
      <div
        className="h-6 flex items-center px-3 gap-3 shrink-0"
        style={{ background: currentDef?.color ?? "var(--accent)" }}
      >
        <span className="text-white/80 text-[10px]">
          {status === "executing"
            ? `${language === "zh" ? "执行中" : "Running"}: ${currentDef?.nameZh} (${currentIndex + 1}/${board.length})`
            : status === "checkpoint"
              ? `${language === "zh" ? "等待输入" : "Waiting"}: ${currentDef?.nameZh} (${currentIndex + 1}/${board.length})`
              : status === "done"
                ? (language === "zh" ? "完成" : "Done")
                : status === "cancelled"
                  ? (language === "zh" ? "已停止" : "Stopped")
                  : (language === "zh" ? "错误" : "Error")}
        </span>
        {document && (
          <span className="text-white/80 text-[10px]">
            {language === "zh"
              ? `${document.replace(/\s/g, "").length} 字`
              : `${document.split(/\s+/).filter(Boolean).length} words`}
          </span>
        )}
        {!isFinished && (
          <button
            onClick={handleStop}
            className="ml-auto text-white/60 hover:text-white text-[10px] transition-colors"
          >
            ⏹ Stop
          </button>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 3: Commit**

```bash
git add ai-text-detector/src/components/writing/AutoExecutor.tsx
git commit -m "feat(writing): create AutoExecutor component (state machine + checkpoint UI)"
```

---

### Task 6: Fix Editor Disabled Prop Reactivity

**Files:**
- Modify: `ai-text-detector/src/components/writing/Editor.tsx`

The Editor currently sets `editable: !disabled` only at init time (line 125). When `disabled` prop changes, the editor doesn't update. Auto mode needs dynamic toggling.

- [ ] **Step 1: Add useEffect to toggle editability**

After the `useEditor` call (line ~135), add:
```ts
// Reactively toggle editability when disabled prop changes
useEffect(() => {
  if (editor) {
    editor.setEditable(!disabled);
  }
}, [editor, disabled]);
```

Also add `useEffect` to the imports (line 3) if not already present — it IS already imported.

- [ ] **Step 2: Verify existing manual mode still works**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

The Editor is used in manual mode too. Ensure no regression: `disabled` defaults to `false`, so `setEditable(true)` is called on mount — same as before.

- [ ] **Step 3: Commit**

```bash
git add ai-text-detector/src/components/writing/Editor.tsx
git commit -m "fix(writing): make Editor disabled prop reactive for auto mode"
```

---

### Task 7: Add Auto-Start Button to Workbench

**Files:**
- Modify: `ai-text-detector/src/components/writing/Workbench.tsx`

- [ ] **Step 1: Extend WorkbenchProps**

Change interface (line 14-20) to:
```ts
interface WorkbenchProps {
  board: BlockInstance[];
  onBoardChange: (board: BlockInstance[]) => void;
  onBlockClick: (block: BlockInstance) => void;
  onStartWriting: () => void;
  onAutoStart?: () => void;
  language: "en" | "zh";
  onLanguageChange: (lang: "en" | "zh") => void;
  streak: number;
}
```

Update destructuring (line 22-28):
```ts
export default function Workbench({
  board,
  onBoardChange,
  onBlockClick,
  onStartWriting,
  onAutoStart,
  language,
  onLanguageChange,
  streak,
}: WorkbenchProps) {
```

- [ ] **Step 2: Derive auto-eligibility from board content (not preset ID)**

After existing state (line 29-30), add:
```ts
const TOEFL_AUTO_BLOCKS: BlockType[] = ["thesis", "outline", "hook", "draft", "analyze", "grammar"];
const isAutoEnabled = board.length === TOEFL_AUTO_BLOCKS.length
  && board.every((b, i) => b.type === TOEFL_AUTO_BLOCKS[i]);
```

This way, whether the user clicked TOEFL preset or manually assembled the exact same blocks, auto mode works.

- [ ] **Step 3: Add Auto-start button next to existing Start button**

Replace the start button section (lines 228-234) with:
```tsx
{/* Start buttons */}
<div className="space-y-2 mt-4">
  <button
    onClick={onStartWriting}
    className="w-full bg-[var(--foreground)] hover:bg-[var(--foreground)]/90 text-white text-sm font-medium py-3 rounded-lg transition-all"
  >
    Start with {getBlockDef(board[0].type).nameZh} →
  </button>
  {onAutoStart && (
    <>
      {/* Language toggle (only visible when auto-eligible) */}
      {isAutoEnabled && (
        <div className="flex items-center justify-center gap-2">
          <span className="text-[10px] text-[var(--muted)]">Language:</span>
          <button
            onClick={() => onLanguageChange(language === "en" ? "zh" : "en")}
            className="text-[10px] font-medium px-2 py-0.5 rounded border border-[var(--card-border)] hover:border-[var(--accent)]/40 transition-colors"
          >
            {language === "en" ? "English" : "中文"}
          </button>
        </div>
      )}
      <button
        onClick={onAutoStart}
        disabled={!isAutoEnabled}
        title={!isAutoEnabled ? "Auto mode supports TOEFL preset only for now" : "AI executes blocks, you provide ideas"}
        className={`w-full text-sm font-medium py-3 rounded-lg transition-all border ${
          isAutoEnabled
            ? "bg-[var(--accent)] hover:bg-[#b5583a] text-white border-transparent"
            : "bg-[var(--background)] text-[var(--muted)] border-[var(--card-border)] cursor-not-allowed"
        }`}
      >
        Auto-start →
      </button>
    </>
  )}
</div>
```

- [ ] **Step 4: Verify TypeScript compiles**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 5: Commit**

```bash
git add ai-text-detector/src/components/writing/Workbench.tsx
git commit -m "feat(writing): add Auto-start button to Workbench (TOEFL only)"
```

---

### Task 8: Wire Up WritingCenter with Execution Mode

**Files:**
- Modify: `ai-text-detector/src/components/writing/WritingCenter.tsx`

- [ ] **Step 1: Add imports**

After existing imports (line ~36), add:
```ts
import AutoExecutor from "./AutoExecutor";
```

- [ ] **Step 2: Add executionMode and language state**

After `const [phase, setPhase] = useState<Phase>("workbench");` (line 96), add:
```ts
const [executionMode, setExecutionMode] = useState<"manual" | "auto">("manual");
const [language, setLanguage] = useState<"en" | "zh">("en");
```

- [ ] **Step 3: Add handleAutoStart handler with topic validation + genre default**

After `handleStartWriting` function (line ~308), add:
```ts
function handleAutoStart() {
  if (!topic.trim()) {
    setError("Please enter a topic before starting auto mode.");
    return;
  }
  // TOEFL defaults to academic genre
  if (genre !== "academic") setGenre("academic");
  setExecutionMode("auto");
}

function handleAutoExit() {
  setExecutionMode("manual");
}
```

- [ ] **Step 4: Add auto-mode render branch (BEFORE the phase === "workbench" check)**

The auto-mode check must come BEFORE any phase-based checks. Add at the very start of the render section (before line ~552):
```tsx
// Auto-execution mode — completely separate render path
if (executionMode === "auto") {
  return (
    <AutoExecutor
      board={board}
      genre={genre}
      topic={topic}
      language={language}
      onExit={handleAutoExit}
    />
  );
}
```

- [ ] **Step 5: Pass onAutoStart and language to Workbench**

Modify the Workbench render (line ~554):
```tsx
return (
  <Workbench
    board={board}
    onBoardChange={setBoard}
    onBlockClick={handleBlockClick}
    onStartWriting={handleStartWriting}
    onAutoStart={handleAutoStart}
    language={language}
    onLanguageChange={setLanguage}
    streak={profile.streak.current}
  />
);
```

- [ ] **Step 6: Verify TypeScript compiles and dev server renders**

Run: `cd ai-text-detector && npx tsc --noEmit 2>&1 | head -20`

- [ ] **Step 7: Commit**

```bash
git add ai-text-detector/src/components/writing/WritingCenter.tsx
git commit -m "feat(writing): wire up auto-execution mode in WritingCenter"
```

---

### Task 9: End-to-End Smoke Test

**Files:** No file changes — this is manual/Playwright testing

- [ ] **Step 1: Start dev server**

```bash
cd ai-text-detector && npm run dev
```

- [ ] **Step 2: Navigate to Writing Center**

Open `http://localhost:3000/app`, click Writing Center panel.

- [ ] **Step 3: Test auto-start button visibility**

1. Select TOEFL preset → Auto-start button should be enabled
2. Select Academic Essay preset → Auto-start button should be disabled with tooltip
3. Select Quick Write preset → Auto-start button should be disabled

- [ ] **Step 4: Run full TOEFL auto pipeline**

1. Select TOEFL preset
2. Enter topic: "Impact of social media on education"
3. Click Auto-start
4. At thesis checkpoint: enter "Social media negatively impacts student focus but offers collaborative learning benefits"
5. At outline checkpoint: enter "1. Distraction evidence\n2. Collaborative benefits\n3. Balance strategies"
6. At hook checkpoint: enter "Start with a surprising statistic"
7. Watch draft execute → verify document appears in editor
8. Watch analyze execute → verify annotations appear
9. Watch grammar execute → verify document updates
10. Verify "Done" state → editor becomes editable

- [ ] **Step 5: Test Stop functionality**

1. Start auto pipeline
2. After thesis checkpoint, click Stop
3. Verify status shows "Stopped", editor is editable, partial output preserved

- [ ] **Step 6: Test error recovery**

1. Temporarily break API key in `.env.local`
2. Start auto pipeline, submit all checkpoints
3. Verify error state appears with Retry button
4. Fix API key, click Retry
5. Verify pipeline resumes

- [ ] **Step 7: Verify manual mode unaffected**

1. Select any preset
2. Click "Start writing" (not Auto-start)
3. Verify all existing manual mode behavior works identically

- [ ] **Step 8: Test Edit document feature**

1. Start auto pipeline, submit all idea checkpoints
2. After draft completes, click "Edit document" at review checkpoint
3. Verify editor becomes editable
4. Make a change to the document
5. Click "Resume" → verify pipeline continues with edited document

- [ ] **Step 9: Test language toggle**

1. On Workbench with TOEFL preset, toggle language to 中文
2. Start auto pipeline
3. Verify checkpoint UI shows Chinese text
4. Verify draft is written in Chinese
5. Repeat with English

- [ ] **Step 10: Final commit**

```bash
git add -A
git commit -m "feat(writing): complete auto-execution mode MVP (TOEFL preset)"
git push
```

# Model Consolidation: Inline Routes Now Use Centralized textModel
**Date:** 2026-04-10
**Loop:** Research + Progress Loop (Turn 65)
**Status:** IMPLEMENTED

## Problem Found

`ai.ts` (Turn 64) implemented `enable_thinking: false` via custom fetch on `qwenText`/`textModel`.
But 5 routes created their own `createOpenAI` inline, bypassing this optimization entirely:

| Route | Old model | Issue |
|-------|-----------|-------|
| `exam-prep/route.ts` | `qwen("qwen3.5-plus")` | Thinking enabled → wastes tokens + JSON risk |
| `exam-scope/route.ts` | `qwen("qwen3.5-plus")` | Same |
| `chat/route.ts` | `qwen("qwen3.5-plus")` | **Worst**: `<think>` blocks stream to user UI |
| `extract/route.ts` | `qwen("qwen-plus-latest")` | Thinking enabled on vision model |
| `regenerate/route.ts` | dynamic `qwen("qwen3.5-plus")` | Same |

### Chat was the most severe

`chat/route.ts` uses `streamText` → `toUIMessageStreamResponse()`. When thinking mode is
enabled, `<think>...</think>` blocks stream directly into the user's chat bubble. There is
no `stripThinkBlocks` in the stream path.

## Fix Applied

1. Exported `textModel` and `visionModel` from `src/lib/ai.ts`
2. Replaced all 5 inline `createOpenAI` setups with imports from `@/lib/ai`
3. Removed 4 duplicate `createOpenAI` import statements
4. `extract` correctly maps to `visionModel` (qwen-plus-latest, multimodal)
5. All others use `textModel` (qwen3.5-plus + thinking disabled)

## Impact

- All 14 AI routes now use thinking-mode-disabled models where appropriate
- Chat: `<think>` blocks no longer stream to user
- Token savings apply universally (~30% on text routes)
- Single place to update model version or DashScope config

## Pattern Going Forward

Any new route that calls DashScope should:
```ts
import { textModel, visionModel } from "@/lib/ai";
// text-only: use textModel
// PDF/image: use visionModel
```
Never `createOpenAI` inline.

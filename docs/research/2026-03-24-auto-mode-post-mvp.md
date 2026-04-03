# Research: Auto-Execution Mode — Post-MVP Improvements

Date: 2026-03-24
Context: Auto-execution mode MVP just deployed (TOEFL preset, non-streaming). Three areas need improvement.

## 1. Vercel Timeout + Streaming for Draft Block

**Problem:** Draft block calls DeepSeek API (~10-15s). Vercel Hobby plan has 10s default timeout for serverless functions. Non-streaming means no incremental feedback.

**Solution: Vercel Fluid Compute (recommended)**
- Source: https://vercel.com/docs/functions/configuring-functions/duration
- Fluid Compute extends default timeout to **5 minutes** across all plans (including Hobby/Free)
- Enable by adding to route config:
  ```ts
  export const maxDuration = 60; // seconds
  ```
- No plan upgrade needed. Just set `maxDuration` in `route.ts`.

**Solution: Edge Functions (alternative)**
- Source: https://vercel.com/blog/gpt-3-app-next-js-vercel-edge-functions
- Edge Functions have 25s timeout and **unlimited when streaming**
- But: Edge runtime has limited Node.js API support, may break existing imports

**Solution: Streaming with OpenAI SDK**
- Source: https://itsrakesh.com/blog/integrating-deepseek-api-in-nextjs-and-expressjs-app
- DeepSeek supports `stream: true` via OpenAI SDK
- Use `ReadableStream` in Next.js route handler:
  ```ts
  const stream = await client.chat.completions.create({ ...opts, stream: true });
  return new Response(stream.toReadableStream());
  ```
- Frontend: use `fetch` + `ReadableStream` reader, or Vercel AI SDK's `useChat`

**Recommendation:**
1. **Immediate fix:** Add `export const maxDuration = 60;` to route.ts — prevents timeout, zero effort
2. **Post-MVP:** Switch draft block to streaming (SSE), keep analyze/grammar as JSON. Use `ReadableStream` pattern, not Vercel AI SDK (to avoid new dependency)

## 2. Tiptap Content Update Flickering

**Problem:** AutoExecutor calls `textToHtml(document)` on every render and passes it as `content` prop to Editor. This may cause cursor jumps or content flickering, especially when user edits at "done" state.

**Key Finding: `setContent` with selection preservation**
- Source: https://github.com/ueberdosis/tiptap/issues/2216
- Source: https://tiptap.dev/docs/editor/api/commands/content/set-content
- Calling `editor.commands.setContent()` resets cursor to start. Fix:
  ```ts
  queueMicrotask(() => {
    const sel = editor.state.selection;
    editor.chain().setContent(content).setTextSelection(sel).run();
  });
  ```
- Use `emitUpdate: false` to prevent feedback loop:
  ```ts
  editor.commands.setContent(html, false, { preserveWhitespace: true });
  ```

**Recommendation for AutoExecutor:**
1. Don't pass `content` prop on every render — only call `setContent` when document state actually changes (via `useEffect` with document dependency)
2. When editor is in "done" state (user editing), don't sync state back from Editor → plain text → HTML → Editor — this is a lossy round-trip. Instead, keep the Tiptap HTML as source of truth in done state
3. When editor is read-only (executing/checkpoint), sync is safe because user isn't typing

## 3. Competitive Analysis: AI Writing Pipeline UX

**Jenni AI (closest competitor)**
- Source: https://jenni.ai/
- Source: https://skywork.ai/blog/jenni-ai-review-2025-academic-citation-workflow/
- **Line-by-line generation**: AI suggests next sentence, user accepts/rejects each one
- **Autocomplete toggle**: Users can turn AI suggestions on/off to maintain control
- **Sleek, minimalist UI**: Google Docs-like, no flashy animations
- **Core insight**: Jenni operates at sentence level, not paragraph level. This is the line between "writing assistant" and "ghostwriter"

**Relevance to our Auto Mode:**
- Our auto mode generates the ENTIRE draft at once → user sees nothing until it's done → low engagement
- Jenni's sentence-by-sentence approach gives user continuous control
- **Post-MVP consideration**: Could draft block stream paragraph-by-paragraph into the editor? User sees article growing in real-time, can stop early if direction is wrong

**Agentic Workflow Patterns (2025-2026)**
- Source: https://vellum.ai/blog/agentic-workflows-emerging-architectures-and-design-patterns
- Source: https://dextralabs.com/blog/ai-agentic-workflow-patterns-for-enterprises/
- **Human-in-the-loop checkpoints** are becoming standard in production AI workflows
- Users trust AI agents more when they can "follow and interact with its work through a dedicated, interactive interface"
- Our checkpoint design (Continue/Edit/Stop) aligns with this pattern

## Concrete Next Steps (Priority Order)

1. **Add `maxDuration = 60` to route.ts** — prevents Vercel timeout, 1 line change, do now
2. **Fix Editor content sync** — use `useEffect` to call `setContent` only on document change, not on every render
3. **Add streaming for draft block** — SSE with `ReadableStream`, show text appearing in editor in real-time
4. **Consider paragraph-by-paragraph streaming** — stream each paragraph as it completes, pause between for user to preview

Sources:
- [Vercel Function Duration Config](https://vercel.com/docs/functions/configuring-functions/duration)
- [AI SDK Timeout Troubleshooting](https://ai-sdk.dev/docs/troubleshooting/timeout-on-vercel)
- [Tiptap setContent Docs](https://tiptap.dev/docs/editor/api/commands/content/set-content)
- [Tiptap Cursor Issue #2216](https://github.com/ueberdosis/tiptap/issues/2216)
- [Jenni AI Review 2026](https://effortlessacademic.com/jenni-ai-review-for-students-and-researchers-2026/)
- [Agentic Workflow Patterns](https://vellum.ai/blog/agentic-workflows-emerging-architectures-and-design-patterns)
- [DeepSeek + Next.js Integration](https://itsrakesh.com/blog/integrating-deepseek-api-in-nextjs-and-expressjs-app)

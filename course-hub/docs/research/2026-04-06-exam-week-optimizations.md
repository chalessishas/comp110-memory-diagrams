# Exam Week Optimizations Research

**Date**: 2026-04-06
**Context**: Calculus II midterm on April 10 (4 days away), CourseHub system stable with 12 commits deployed
**Researcher**: Claude Opus 4.6

---

## 1. "Last 4 Days Before Exam" Study Strategies

### Sources
- [Cornell Five-Day Study Plan](https://lsc.cornell.edu/how-to-study/studying-for-and-taking-exams/the-five-day-study-plan/)
- [Pitt Seven-Day Test Prep Plan](https://www.asundergrad.pitt.edu/study-lab/study-skills-tools-resources/seven-day-test-prep-plan/)
- [Med School Insiders: Week Before Exam](https://medschoolinsiders.com/study-strategies/how-to-prepare-a-week-before-an-exam/)
- [MIT AgeLab: Cramming vs Spacing](https://agelab.mit.edu/blog/cramming-may-help-for-next-day-exams-but-for-long-term-memory-spacing-out-study-is-what-works)
- [PMC: Interleaved Practice Enhances Memory](https://pmc.ncbi.nlm.nih.gov/articles/PMC8589969/)
- [APA: Study Smart](https://www.apa.org/gradpsych/2011/11/study-smart)

### Key Insights

**Spacing still beats cramming, even in 4 days.** 10 hours across 4 days outperforms 10 hours across 2 days. The critical factor is distributing study sessions with sleep between them -- sleep consolidates memory. Cramming can help pass a next-day test but the advantage is extremely short-lived.

**Retrieval practice is the highest-leverage technique.** Actively recalling information (blank-page testing, self-quizzing, practice problems) produces 50-125% improvement on novel problems compared to re-reading. This is exactly what CourseHub's flashcard system does.

**Interleaving is critical for calculus.** Mixing problem types (integration by parts, then trig substitution, then partial fractions) forces the brain to select the right strategy, not just execute a known one. Research shows students rate interleaving as "harder" but score significantly better on exams. Median improvement: 50% on test 1, 125% on test 2.

**Optimal 4-day schedule (evidence-based):**
| Day | Focus | Method |
|-----|-------|--------|
| Day 1 (Apr 6) | Diagnostic -- identify weak topics | Practice test or CourseHub pretest across all 12 topics |
| Day 2 (Apr 7) | Deep work on weakest 4-5 topics | Interleaved problem sets, 15-min chunks with topic switching |
| Day 3 (Apr 8) | Full practice under timed conditions | Simulate exam conditions, then error analysis |
| Day 4 (Apr 9) | Targeted review of persistent gaps | Light review (2 hrs max), prioritize sleep |

**Day-before rule:** Do NOT take a practice test the day before. Instead: 1 hour reviewing notes, 1 hour light skim of high points, then rest. Sleep > last-minute cramming.

### Actionable Recommendations for CourseHub

1. **Implement "Exam Sprint Mode"** -- a 4-day countdown UI that suggests daily focus areas based on FSRS stability data, prioritizing weakest topics first
2. **Add interleaved practice sets** -- instead of topic-by-topic review, generate mixed-topic problem sets that force strategy selection
3. **Enforce cognitive load limits** -- cap sessions at 15-min focused blocks with enforced breaks, show a "take a break" prompt after each chunk
4. **Add a "Day Before" mode** -- lighter review, no new material, emphasis on confidence building

| Recommendation | Effort |
|----------------|--------|
| Exam Sprint Mode (countdown + daily plan) | Medium |
| Interleaved practice generation | Medium |
| Session time limits + break prompts | Quick |
| Day-Before mode | Quick |

---

## 2. DashScope qwen3.5-plus JSON Output Reliability

### Sources
- [Alibaba Cloud: Enforce Structured JSON Output](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output)
- [Alibaba Cloud: JSON Mode](https://www.alibabacloud.com/help/en/model-studio/json-mode)
- [Qwen 3.5 API Guide (Macaron)](https://macaron.im/blog/qwen-3-5-api-guide)
- [HuggingFace: Reasoning Content Leaks into message.content](https://huggingface.co/Qwen/Qwen3.5-35B-A3B/discussions/18)
- [GitHub QwenLM Issue #26: Missing reasoning_content in Tool Calling](https://github.com/QwenLM/Qwen3.5/issues/26)
- [vLLM Issue #18819: Broken Structured Output with enable_thinking=False](https://github.com/vllm-project/vllm/issues/18819)
- [Alibaba Cloud: OpenAI Compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)

### Key Insights

**Known critical bug: reasoning content leaks into JSON output.** When thinking mode is enabled, `<think>` blocks get injected into `message.content` alongside the JSON payload, breaking parsing. This is documented across HuggingFace, GitHub Issues, and vLLM bug trackers. The issue affects tool calling and structured output.

**The enable_thinking paradox:**
- `enable_thinking=true` + structured output: reasoning text leaks into content field, breaking JSON parsing
- `enable_thinking=false` + structured output: on some model variants, output produces invalid JSON (extra braces, markdown code blocks, gibberish)
- **DashScope API (hosted)** with `enable_thinking=false`: structured output works correctly for qwen3.5-plus specifically. The issues above primarily affect self-hosted model variants

**Reliable JSON pattern for DashScope API:**
1. Set `response_format: { type: "json_object" }` (or `json_schema` with strict validation)
2. Include the word "JSON" in the system/user prompt (required by API)
3. Set `enable_thinking: false` explicitly
4. Provide the exact schema in the prompt as an example

**Qwen thinking-mode models do NOT support structured output** -- this is an official limitation per Alibaba Cloud docs.

### Actionable Recommendations for CourseHub

1. **Always set `enable_thinking: false`** when calling qwen3.5-plus for structured JSON generation -- this is the safe path on DashScope hosted API
2. **Use `response_format: { type: "json_schema" }` with strict validation** rather than just `json_object` -- this adds server-side schema enforcement
3. **Add a JSON sanitization layer** as defense-in-depth -- strip any `<think>...</think>` blocks before parsing, in case the model occasionally leaks reasoning content
4. **Validate output against Zod schema** before using it in the UI -- fail gracefully with a retry if schema validation fails

| Recommendation | Effort |
|----------------|--------|
| Set enable_thinking: false globally | Quick |
| Switch to json_schema with strict mode | Quick |
| Add think-block sanitization regex | Quick |
| Add Zod validation + retry logic | Quick |

---

## 3. Vercel AI SDK streamObject for Progressive Lesson Rendering

### Sources
- [AI SDK Core: streamObject Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-object)
- [AI SDK UI: Object Generation](https://ai-sdk.dev/docs/ai-sdk-ui/object-generation)
- [Vercel Template: Object Generation Streaming with useObject](https://vercel.com/templates/next.js/use-object)
- [Streaming Objects with Vercel AI SDK (AI Hero)](https://www.aihero.dev/streaming-objects-with-vercel-ai-sdk)
- [GitHub Discussion: streamObject in Next.js API Route](https://github.com/vercel/ai/discussions/1962)
- [Vercel AI SDK 3.3 Blog](https://vercel.com/blog/vercel-ai-sdk-3-3)
- [DEV Community: AI-Powered Web Apps with AI SDK 2026](https://dev.to/bean_bean/the-ultimate-guide-to-building-ai-powered-web-apps-with-the-vercel-ai-sdk-in-2026-1c6a)

### Key Insights

**streamObject is purpose-built for this use case.** It returns a `partialObjectStream` that yields incomplete-but-valid partial objects as the model generates each field. The client-side `useObject` hook consumes this stream and re-renders on each chunk. Users see content appearing progressively -- name first, then description, then nested arrays populating one by one.

**Architecture:**
- **Server**: API route uses `streamObject()` with a Zod schema, returns the stream
- **Client**: `useObject({ api: '/api/lesson', schema: lessonSchema })` consumes it
- **Rendering**: The partial object updates on each token, so lesson chunks appear as they generate

**Key considerations:**
- Schema validation happens per-chunk -- complex nested structures may introduce parsing delays
- The stream uses SSE (Server-Sent Events) since AI SDK 5, which is more stable than WebSocket-based streaming
- Works with any OpenAI-compatible provider -- DashScope's OpenAI-compatible endpoint should work

**Feasibility for CourseHub lesson chunks:**
Currently CourseHub waits for the full lesson response before rendering. With streamObject, each lesson chunk (explanation, example, practice question) could appear as it generates. For a typical lesson with 5-8 chunks, this could reduce perceived latency from ~15s to ~2-3s for first content.

### Actionable Recommendations for CourseHub

1. **Replace `generateObject` with `streamObject`** in the lesson generation API route -- this is a near drop-in replacement
2. **Use `useObject` on the client** to progressively render lesson chunks as they stream in
3. **Design chunk-level loading states** -- show skeleton UI for not-yet-generated chunks while rendering completed ones
4. **Keep the Zod schema flat where possible** -- deeply nested schemas add parsing overhead during streaming

| Recommendation | Effort |
|----------------|--------|
| Swap generateObject -> streamObject in API | Quick |
| Add useObject hook on client | Quick |
| Progressive chunk rendering UI | Medium |
| Skeleton loading states per chunk | Medium |

---

## 4. FSRS Optimal Parameters for 1-4 Day Window

### Sources
- [FSRS Wiki: The Optimal Retention](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention)
- [FSRS Wiki: ABC of FSRS](https://github.com/open-spaced-repetition/fsrs4anki/wiki/ABC-of-FSRS)
- [Anki Forums: How Do I Use FSRS for Exam?](https://forums.ankiweb.net/t/how-do-i-use-fsrs-for-exam/43631)
- [Anki Issue #2803: Consider Increasing Retention Limit Above 0.97](https://github.com/ankitects/anki/issues/2803)
- [Anki Forums: Approximate Workload When Changing Desired Retention](https://forums.ankiweb.net/t/questions-about-approximate-workload-when-changing-desired-retention/63860)
- [Expertium: Understanding Retention in FSRS](https://expertium.github.io/Retention.html)
- [FSRS Tutorial](https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md)

### Key Insights

**0.95 is already near-optimal for a 4-day window. Going to 0.97 is not recommended.**

The FSRS community explicitly warns against setting retention above 0.97:
- It significantly increases daily workload
- Reviews become so frequent they feel like massed repetition (cramming), undermining the spacing effect
- 0.97 is the hard upper limit in Anki's implementation for good reason

**The "actual vs desired" retention gap matters.** If desired retention is 0.90, actual retrievability on a random card at a random time averages ~0.95. This means your current 0.95 desired retention likely yields ~0.97 actual retention in practice -- you are already at the effective ceiling.

**For a 4-day exam window, the critical lever is maxInterval, not retention.** Setting `maxInterval = daysToExam` (which CourseHub already does) ensures no card gets scheduled past exam day. This is the correct approach per FSRS forum recommendations.

**Workload implications:**
- 0.90 retention: baseline workload
- 0.95 retention: ~1.5-2x workload vs 0.90
- 0.97 retention: ~3-4x workload vs 0.90 (diminishing returns)

**What actually helps more than raising retention:**
1. Focus reviews on cards with lowest stability (weakest knowledge)
2. Prioritize cards that haven't been seen yet (new cards > over-reviewing mature cards)
3. Use the "Compute minimum recommended retention" feature to find the sweet spot for your time budget

### Actionable Recommendations for CourseHub

1. **Keep retention at 0.95** -- this is already near-optimal. Raising to 0.97 would roughly double review workload for marginal gain
2. **Add priority sorting by stability** -- surface the lowest-stability cards first in review sessions so limited study time hits the weakest spots
3. **Cap daily new cards intelligently** -- with 4 days left, new cards introduced on Day 3-4 won't have time for meaningful spacing. Reduce new card introduction on Days 3-4
4. **Show "knowledge coverage" metric** -- display what percentage of exam topics have cards above 0.90 stability to give the student confidence and focus

| Recommendation | Effort |
|----------------|--------|
| Keep retention at 0.95 (no change) | None |
| Priority sorting by stability | Quick |
| Dynamic new-card cap based on days remaining | Medium |
| Knowledge coverage dashboard | Medium |

---

## Summary: Priority Matrix

| Priority | Action | Impact | Effort |
|----------|--------|--------|--------|
| P0 | Keep FSRS at 0.95, sort by lowest stability first | High -- focuses limited time on weakest areas | Quick |
| P0 | Set enable_thinking: false + json_schema strict mode | High -- prevents JSON parsing failures | Quick |
| P0 | Add think-block sanitization regex | High -- defense against reasoning leaks | Quick |
| P1 | Swap to streamObject for lesson generation | High -- perceived latency drops from ~15s to ~2-3s | Quick |
| P1 | Add interleaved practice mode | High -- 50-125% improvement on novel problems | Medium |
| P2 | Exam Sprint Mode (4-day countdown) | Medium -- guides daily study focus | Medium |
| P2 | Progressive chunk rendering UI + skeleton states | Medium -- better UX during generation | Medium |
| P3 | Session time limits + break prompts | Low-Medium -- prevents cognitive overload | Quick |
| P3 | Day-Before light review mode | Low -- nice-to-have for exam eve | Quick |

# Backend Improvements Research (2026-04-09)

## Current State
- AI: Qwen 3.5-Plus via DashScope (`dashscope.aliyuncs.com`), using `generateText` + manual JSON extraction
- Pain points: 10-20s per AI call, malformed JSON ~15% of the time, no background processing, exam-prep timeout risk

---

## 1. AI Response Speed

### Switch to International Endpoint (Quick Win)
- Current: `https://dashscope.aliyuncs.com/compatible-mode/v1` (China Beijing)
- International: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` (Singapore)
- For non-China users, Singapore endpoint has lower network latency. One-line change in `ai.ts`
- Source: https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope

### Switch to qwen3.5-flash for Non-Vision Tasks (Recommended)
- **qwen3.5-flash**: Released Feb 2026, hybrid linear-attention + sparse MoE architecture
- Pricing: $0.065/M input, $0.260/M output (vs Plus: $0.26/$1.56 per M) -- **4x cheaper**
- Designed for lower latency while maintaining quality for structured tasks
- Use flash for: study tasks, lesson generation, question generation, study notes
- Keep qwen-plus-latest for: PDF/image vision tasks (syllabus parsing, exam parsing)
- Source: https://pricepertoken.com/pricing-page/model/qwen-qwen3.5-flash

### Streaming + Progressive UI (Medium Effort)
- AI SDK supports `streamText` with `Output.object()` for streaming structured data
- `partialOutputStream` gives incremental object updates (cannot be validated until complete)
- `elementStream` for arrays: emits each completed, validated element as generated
- Best for: question generation (stream questions one-by-one), lesson chunks
- Trade-off: Streaming JSON cannot use `json_object` response_format on DashScope
- Source: https://ai-sdk.dev/docs/ai-sdk-core/generating-structured-data

### Parallel Calls (Already Partially Done)
- `generateLessonChunks` already uses `Promise.all` for 4 parallel chunk generations
- Apply same pattern to exam-prep: split KP batches and run in parallel
- Watch DashScope rate limits (429 errors) -- add retry with exponential backoff

---

## 2. Structured JSON Output

### Current Approach (Fragile)
- Prompt says "return ONLY valid JSON"
- Manual `extractJSON()` with balanced-brace parser + fallback greedy regex
- `stripThinkBlocks()` to remove `<think>` tags that corrupt JSON
- Zod validation with lenient transforms (handles various AI output shapes)

### DashScope json_object Mode (Quick Win)
- Set `response_format: { type: "json_object" }` in the API call
- **Requirement**: System or user message must contain the word "JSON" (case-insensitive)
- **Limitation**: Thinking mode must be disabled (`enable_thinking: false`)
- **Limitation**: Do NOT set `max_tokens` -- it may truncate JSON mid-output
- **Limitation**: Only `json_object` is supported (NOT `json_schema` with strict schema enforcement)
- Supported models: qwen-plus, qwen-flash, qwen-turbo, qwen-max (non-thinking mode)
- Source: https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output

### AI SDK generateObject (Best Practice)
- Replace `generateText` + manual extraction with `generateObject` / `Output.object()`
- Pass Zod schema directly: SDK handles mode selection (json/tool) per provider
- For OpenAI-compatible providers: SDK sends `response_format` + `tools` as needed
- Code change: `generateText({...})` -> `generateText({ output: Output.object({ schema: myZodSchema }), ...})`
- Eliminates: `extractJSON()`, `stripThinkBlocks()`, manual `JSON.parse()`, manual Zod parse
- Source: https://ai-sdk.dev/docs/reference/ai-sdk-core/generate-object

### Tool Calling as Structured Output (Fallback)
- DashScope supports OpenAI-compatible function calling / tools
- Define a "tool" whose parameters match your desired JSON schema
- Model "calls the tool" with structured arguments = guaranteed schema compliance
- More reliable than json_object for complex nested schemas
- Trade-off: Slightly more tokens used for tool definition overhead

### Recommended Migration Path
1. **Phase 1**: Add `response_format: { type: "json_object" }` to all non-vision calls (1 hour)
2. **Phase 2**: Migrate to AI SDK `Output.object()` with Zod schemas (half day)
3. **Phase 3**: Keep `extractJSON()` as fallback for vision model calls where json_object may not work

---

## 3. Background Job Processing

### The Problem
- Exam-prep generates questions for 5-15 KPs, each taking 10-20s = 50-300s total
- Vercel has 60s timeout on API routes (Pro plan)
- Current workaround: reduce batch size, but still risky for large courses

### Option A: Trigger.dev v3 (Recommended for This Project)
- **Architecture**: Jobs run on Trigger.dev's infrastructure, no Vercel timeout limits
- Jobs can run for minutes or hours
- Has first-class Supabase integration (trigger from DB changes, write results back)
- React hooks for real-time job status in frontend (`useRealtimeRun`)
- Free tier: 5,000 runs/month
- **Best for**: Long-running AI generation (exam-prep, bulk question generation)
- Source: https://trigger.dev/docs/guides/frameworks/supabase-guides-overview

### Option B: Inngest
- **Architecture**: Calls your serverless endpoints, step-based retry
- More advanced workflow orchestration (sleep, fan-out, debounce)
- Larger free tier: 50,000 runs/month
- Code runs on your Vercel functions = still subject to Vercel timeout
- **Best for**: Event-driven workflows, lighter tasks that fit within Vercel limits
- Source: https://www.inngest.com/blog/run-nextjs-functions-in-the-background

### Option C: Supabase Edge Functions + DB Polling
- Create a `job_queue` table, insert job requests from API routes
- Supabase Edge Function polls or is triggered by DB webhook
- Edge Functions have 150s wall-time limit (better than Vercel's 60s)
- No additional service to manage, stays within Supabase ecosystem
- **Best for**: Simple queue without external dependencies

### Option D: Vercel Cron (Not Recommended for AI Tasks)
- Only for scheduled periodic tasks (cleanup, reports)
- Subject to same 60s timeout as regular functions
- No event-driven triggering, no job queuing
- Source: https://drew.tech/posts/cron-jobs-in-nextjs-on-vercel

### Recommended Architecture
```
User clicks "Generate Exam Prep"
  -> API route creates job record in Supabase (status: "pending")
  -> Returns job_id immediately to frontend (< 1s)
  -> Trigger.dev picks up job, runs AI generation (no timeout)
  -> Updates Supabase row as each topic completes (status: "processing", progress: 3/10)
  -> Frontend polls or subscribes to job status via Supabase realtime
  -> Job completes -> status: "done", questions available
```

---

## 4. Question Quality

### Common AI-Generated MCQ Failure Modes
- **Implausible distractors**: 23% of AI-generated items contain at least one obviously wrong option (source: PMC study on AI MCQ quality)
- **Poor difficulty calibration**: Agreement between AI-predicted and expert-rated difficulty is near-random (kappa = 0.06)
- **Violation of item-writing principles**: 46.7-48.9% of AI-generated certification exam items violate standard MCQ design rules
- **Surface-level questions**: AI defaults to recall/definition questions unless explicitly prompted for higher Bloom's levels
- Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12934029/

### Best Practices for Distractor Generation
1. **Misconception-based prompting**: Instruct LLM to first identify common student errors, THEN generate distractors based on those errors. Chain-of-thought approach:
   - "What mistakes would a student typically make on this problem?"
   - "Generate wrong answers that result from each mistake"
2. **Context-aware distractor reuse**: Retrieve high-quality distractors from existing items and adapt them. Raises teacher-rated quality by 30% vs static templates
3. **Formatting rules**: Distractors should match correct answer in length, grammar, and specificity. All options should be parallel in structure
4. **Avoid "none of the above" and "all of the above"** -- these reduce item discrimination
- Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11623049/
- Source: https://arxiv.org/html/2501.13125v2

### Difficulty Calibration Strategy
Current prompt uses Bloom's taxonomy mapping (1=Recall through 5=Evaluate/Create). Research suggests:
1. **Two-pass generation**: First generate question, then have a separate call rate its difficulty (self-consistency check)
2. **Anchoring examples**: Include 1-2 example questions at each difficulty level in the prompt
3. **Student performance feedback loop**: After students answer, use attempt data to recalibrate difficulty labels (empirical Item Response Theory)
4. **Constraint in prompt**: "At least 40% of questions must be Apply level (3) or above" -- forces diversity

### Validation Pipeline (Post-Generation)
1. **Structural check**: Every MCQ has exactly 4 options, answer matches one option label, no duplicate options
2. **Distractor uniqueness**: No two options are semantically identical (cosine similarity check)
3. **Answer distribution**: Correct answers should be roughly evenly distributed across A/B/C/D
4. **Bloom's distribution**: Flag if > 60% of questions are Bloom's level 1-2
5. **KP coverage**: Every knowledge point should have at least 1 question
6. **Flagging system**: Already have `questions.flagged` column -- use it for auto-flagged low-confidence items

---

## Priority Recommendations

| Priority | Change | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Switch to intl endpoint | 5 min | Reduce latency for non-China users |
| P0 | Add `response_format: json_object` | 30 min | Eliminate ~80% of JSON parse failures |
| P1 | Switch non-vision calls to qwen3.5-flash | 1 hour | 4x cheaper, lower latency |
| P1 | Migrate to AI SDK `Output.object()` | 4 hours | Eliminate extractJSON, type-safe output |
| P2 | Add Trigger.dev for exam-prep | 1 day | No timeout limit, real-time progress |
| P2 | Add question validation pipeline | 4 hours | Flag bad distractors, ensure quality |
| P3 | Streaming for question generation | 1 day | Progressive UI, perceived speed boost |
| P3 | Two-pass difficulty calibration | 2 hours | Better difficulty distribution |

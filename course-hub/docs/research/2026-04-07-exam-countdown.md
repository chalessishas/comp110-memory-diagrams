# Exam Countdown Research (April 7, 2026)

> Calculus II midterm: April 10, 2026 (3 days away)
> Researched by: Claude Opus 4.6 agent

---

## 1. Vercel AI SDK streamObject -- Current State (April 2026)

### 1.1 streamObject + DashScope via OpenAI-Compatible API

- **Source**: [Community Providers: Qwen - AI SDK](https://ai-sdk.dev/providers/community-providers/qwen)
- **Core finding**: The `qwen-ai-provider` community package supports `generateText`, `streamText`, `generateObject`, and `streamObject` with DashScope's Qwen models. DashScope exposes an OpenAI-compatible endpoint at `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`, so the `@ai-sdk/openai-compatible` package also works.
- **Relevance**: CourseHub already uses DashScope qwen3.5-plus. streamObject can progressively render structured quiz/outline data instead of waiting for the full response.
- **Recommended action**: Switch outline and quiz generation routes from `streamText` + manual JSON parse to `streamObject` with Zod schema. **Effort: small** (1-2 hours per route).

### 1.2 Gotchas with Streaming JSON Objects

- **Source**: [AI SDK Core: streamObject Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-object)
- **Core finding**: Partial objects during streaming are **not validated** against the schema. Only the final object is guaranteed to match. If you use `Output.json()`, the SDK only checks valid JSON -- not structure/types. Use `Output.object()` or `Output.array()` for schema enforcement.
- **Relevance**: CourseHub quiz generation needs validated output. Using `Output.object()` with Zod ensures type safety on the final result while still allowing progressive UI.
- **Recommended action**: Always use `Output.object(zodSchema)` not `Output.json()`. Handle partial objects defensively in the UI (null-check nested fields). **Effort: trivial**.

### 1.3 AI SDK 5 Changes

- **Source**: [AI SDK 5 Announcement - Vercel Blog](https://vercel.com/blog/ai-sdk-5)
- **Core finding**: AI SDK 5 introduced breaking changes to the provider interface. The `@ai-sdk/openai-compatible` package is the recommended way to connect non-first-party providers. streamObject is stable and unchanged in v5.
- **Relevance**: CourseHub should pin its AI SDK version and check compatibility before upgrading to v5.
- **Recommended action**: Stay on current AI SDK version for now; upgrade to v5 after the exam. **Effort: N/A (defer)**.

### 1.4 qwen-ai-provider Package

- **Source**: [GitHub: Younis-Ahmed/qwen-ai-provider](https://github.com/Younis-Ahmed/qwen-ai-provider)
- **Core finding**: Community-maintained provider with 15+ Qwen model support. API key defaults to `DASHSCOPE_API_KEY` env var. Supports structured output generation via Zod schemas.
- **Relevance**: Could replace the manual OpenAI-compatible setup in CourseHub, but adds a community dependency.
- **Recommended action**: Evaluate post-exam. Current `@ai-sdk/openai-compatible` setup is fine. **Effort: trivial to switch if needed**.

---

## 2. FSRS localStorage to Supabase Migration Pattern

### 2.1 Existing Patterns: NerdClash + sr-cards-api

- **Source**: [NerdClash Dev Update - RouterFreak](https://routerfreak.com/nerdclash-dev-update/)
- **Core finding**: NerdClash uses ts-fsrs + Supabase with PostgreSQL, RLS, and real-time subscriptions. Their conflict resolution approach: **recalculate FSRS state from the full review history** rather than trying to merge card-level state. This is the safest pattern -- review logs are append-only, so conflicts are impossible at the log level.
- **Relevance**: Directly applicable to CourseHub. Store review logs in Supabase, compute FSRS state on demand.
- **Recommended action**: Design the `review_logs` table (card_id, rating, review_time, user_id). Compute FSRS scheduling from logs server-side. **Effort: medium** (4-6 hours for table + API + migration script).

### 2.2 sr-cards-api Architecture

- **Source**: [GitHub: drewsamsen/sr-cards-api](https://github.com/drewsamsen/sr-cards-api)
- **Core finding**: RESTful API using Express + PostgreSQL + Supabase Auth. FSRS runs server-side in Node.js. Cards table stores current FSRS state (stability, difficulty, due date), and a separate reviews table stores the log.
- **Relevance**: This is a reference architecture for CourseHub's migration. Two-table pattern (cards + reviews) is the standard.
- **Recommended action**: Follow the two-table pattern. Cards table for current state (fast reads), reviews table for history (conflict resolution). **Effort: included in 2.1 estimate**.

### 2.3 ts-fsrs afterHandlers for DB Integration

- **Source**: [ts-fsrs DeepWiki - Examples and Integration](https://deepwiki.com/open-spaced-repetition/ts-fsrs/4-examples-and-integration)
- **Core finding**: ts-fsrs provides `afterHandler` callbacks that transform return values for database storage. This means you can hook into the scheduling pipeline to persist state without wrapping every call manually.
- **Relevance**: Simplifies the integration layer between ts-fsrs and Supabase RPC calls.
- **Recommended action**: Use afterHandlers when integrating ts-fsrs server-side. **Effort: trivial** (part of the migration work).

### 2.4 Conflict Resolution Strategy

- **Source**: [NerdClash Dev Update - RouterFreak](https://routerfreak.com/nerdclash-dev-update/) + [Offline-First Architecture - DEV Community](https://dev.to/anurag_dev/implementing-offline-first-architecture-in-flutter-part-1-local-storage-with-conflict-resolution-4mdl)
- **Core finding**: Best pattern for SRS conflict resolution is **append-only review logs + server-side state recomputation**. When client and server diverge, merge all review logs (deduplicate by timestamp + card_id), then replay through FSRS to get the canonical state. This is idempotent and deterministic.
- **Relevance**: CourseHub currently has localStorage-only state. Migration path: (1) export localStorage reviews to Supabase, (2) keep writing to both during transition, (3) switch to server-only once verified.
- **Recommended action**: Implement the 3-phase migration. Phase 1 (export) can be done pre-exam as a background task. **Effort: medium** overall, but Phase 1 alone is **small** (2 hours).

---

## 3. Vercel Serverless Monitoring for DashScope API Calls

### 3.1 Built-in Vercel Monitoring

- **Source**: [Vercel Functions Docs](https://vercel.com/docs/functions)
- **Core finding**: Vercel auto-collects `console.log/error/warn` and displays them in the dashboard per deployment. Basic function execution time and invocation count are visible. However, there is no AI-specific visibility (no token throughput, cost per user, or LLM latency breakdown).
- **Relevance**: Sufficient for debugging but not for understanding DashScope cost/performance.
- **Recommended action**: Use `console.log` with structured JSON for immediate wins. **Effort: trivial**.

### 3.2 OpenTelemetry on Vercel

- **Source**: [Instrument Vercel Serverless Functions with OpenTelemetry - OneUptime](https://oneuptime.com/blog/post/2026-02-06-opentelemetry-vercel-serverless-functions/view)
- **Core finding**: Use `@vercel/otel` for optimized initialization. In serverless, use `SimpleSpanProcessor` (not batched) to avoid data loss from function freezing. Call `forceFlush()` at handler end. The `instrumentation.ts` file in project root auto-initializes on startup.
- **Relevance**: Gives distributed tracing for DashScope calls. Can measure time-to-first-token, total latency, and error rates.
- **Recommended action**: Add `instrumentation.ts` with OTEL setup. **Effort: small** (1-2 hours). Defer to post-exam.

### 3.3 Sentry vs Vercel Built-in

- **Source**: [Sentry for Vercel - Vercel Marketplace](https://vercel.com/marketplace/sentry)
- **Core finding**: Sentry auto-captures unhandled exceptions, correlates with distributed traces and release versions. Integrated billing via Vercel Marketplace. Vercel's built-in monitoring covers basics (logs, function duration), but Sentry adds error grouping, stack traces, and performance monitoring. They are complementary, not competing.
- **Relevance**: For DashScope timeout/error detection, Sentry would catch unhandled rejections and timeout errors automatically.
- **Recommended action**: Install Sentry via Vercel Marketplace for error tracking. Use built-in logs for quick debugging. **Effort: small** (30 min setup). Defer to post-exam.

### 3.4 LLM-Specific Observability: Helicone vs Langfuse

- **Source**: [Helicone GitHub](https://github.com/Helicone/helicone), [Langfuse - Vercel AI SDK Integration](https://langfuse.com/integrations/frameworks/vercel-ai-sdk)
- **Core finding**: Helicone is proxy-based (swap base URL, instant observability for cost + latency). Langfuse adds deeper tracing (prompt templates, retrieval steps, evaluations). Common pattern: Helicone for cost tracking + Langfuse for trace analysis. Both have free tiers (Helicone: 10K requests free; Langfuse: 50K units/mo free).
- **Relevance**: For CourseHub's DashScope calls, Helicone would be the fastest win -- just change the base URL to proxy through Helicone. Gets cost tracking and latency monitoring immediately.
- **Recommended action**: Add Helicone proxy for DashScope calls (one URL change). **Effort: trivial** (15 min). Consider Langfuse later for deeper tracing. **Effort: small** (1-2 hours).

### 3.5 Detecting Slow DashScope Calls Without AbortSignal

- **Source**: [Vercel Serverless Function Timeout Guide](https://codegive.com/blog/vercel_serverless_function_timeout.php), [Upstash: Reduce Vercel Costs](https://upstash.com/blog/vercel-cost-workflow)
- **Core finding**: Implement retry with exponential backoff. Ensure idempotent operations. Use `maxDuration` in route config (already set to 55s in CourseHub). For AI API calls with variable GPU response times, the function risks timeout. Monitor via structured logging: log `startTime`, `endTime`, `tokenCount`, `model` per call.
- **Relevance**: CourseHub already has `maxDuration` set. Adding structured logging per AI call would catch slow responses without needing AbortSignal.
- **Recommended action**: Add a `logAICall()` wrapper that logs timing + metadata. **Effort: small** (1 hour).

---

## 4. Last 3 Days Before Exam -- Optimal Study Tool Features

### 4.1 Should FSRS Parameters Change in Last 72 Hours?

- **Source**: [FSRS FAQ - AnkiWeb](https://faqs.ankiweb.net/frequently-asked-questions-about-fsrs.html), [Anki Forums: How to use FSRS for exam](https://forums.ankiweb.net/t/how-do-i-use-fsrs-for-exam/43631)
- **Core finding**: Yes. Use the "Advance" feature (from FSRS4Anki Helper) to decrease intervals of undue cards based on current and requested retention. The "Compute minimum recommended retention" feature calculates optimal retention rate for a target exam date. For a 3-day window, desired retention should be pushed to ~95% (higher than the typical 90%) to prioritize recall on exam day, accepting more reviews as the trade-off.
- **Relevance**: CourseHub's FSRS implementation should support an "exam mode" that temporarily increases desired retention and pulls forward undue cards.
- **Recommended action**: Add an "Exam in X days" setting that adjusts `desiredRetention` to 0.95 and advances undue cards. **Effort: medium** (3-4 hours for UI + logic).

### 4.2 Cramming vs Spaced Repetition: What Research Shows

- **Source**: [Spaced Repetition vs Cramming Research - ByHeart](https://byheart.io/blog/spaced-repetition-vs-cramming-research), [UCSD Spaced Practice](https://psychology.ucsd.edu/undergraduate-program/undergraduate-resources/academic-writing-resources/effective-studying/spaced-practice.html)
- **Core finding**: For next-day exams, cramming and spaced repetition perform almost identically. But within a week, crammers lose 70-80% while spaced learners retain 70-80%. Since the exam is in 3 days (not tomorrow), there is still enough time for 2-3 spaced sessions to meaningfully outperform pure cramming. The ideal pattern: review today, review Day 2, light review Day 3 morning.
- **Relevance**: CourseHub should guide the user toward 3 distributed sessions rather than one marathon session. The tool should actively discourage 4+ hour continuous sessions.
- **Recommended action**: Add a "3-day exam plan" view that schedules 3 sessions with decreasing intensity. **Effort: medium** (3-4 hours).

### 4.3 Optimal Review Session Length

- **Source**: [How Long to Study - The Blog Timer](https://theblogtimer.com/guides/how-long-to-study), [APA: Study Smart](https://www.apa.org/gradpsych/2011/11/study-smart)
- **Core finding**: Cognitive performance declines after 25-50 minutes of focused work. The Pomodoro pattern (25 min study / 5 min break) is well-supported by research. For math-heavy subjects like Calculus II, 50-minute sessions allow reaching flow state without fatigue. Maximum productive study per day: ~4-6 hours of focused work.
- **Relevance**: CourseHub should implement session timing with break reminders.
- **Recommended action**: Add a Pomodoro-style timer overlay (25/50 min modes) with break reminders. **Effort: small** (2 hours for basic timer).

### 4.4 What Features Matter Most in Final 3 Days

- **Source**: [Mindgrasp: How to Cram Smart](https://www.mindgrasp.ai/blog/how-to-cram-for-exams-the-smart-way), [Knowt: Spaced Repetition](https://knowt.com/blog/spaced-repetition-power-up-your-learning)
- **Core finding**: The most impactful features for last-minute exam prep are: (1) **Weak-card prioritization** -- surface cards with lowest retrievability first, (2) **Practice under test conditions** -- timed questions that simulate exam format, (3) **Progress dashboard** -- show coverage % so the student knows what is not yet reviewed, (4) **Input test date** -- auto-adjust scheduling to ensure all material is touched before exam.
- **Relevance**: CourseHub should prioritize weak-card surfacing and coverage tracking over adding new content.
- **Recommended action**: Build a "coverage dashboard" showing % of cards reviewed at >= 90% retrievability. Surface lowest-retrievability cards first in review queue. **Effort: medium** (4-5 hours).

### 4.5 FSRS-Specific Exam Optimization

- **Source**: [FSRS Technical Explanation - Expertium](https://expertium.github.io/Algorithm.html), [ABC of FSRS - GitHub Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/ABC-of-FSRS)
- **Core finding**: FSRS can compute retrievability for any future date. For exam prep, calculate each card's predicted retrievability on exam day. Sort by ascending retrievability = optimal review order. Cards already at high retrievability for exam day can be skipped, saving time for weak cards.
- **Relevance**: ts-fsrs can calculate `retrievability(card, examDate)`. This is the core of an "exam mode" feature.
- **Recommended action**: Compute per-card retrievability for April 10 and sort the review queue by it. Skip cards above 0.95 retrievability. **Effort: small** (2 hours -- ts-fsrs already has this API).

---

## Priority Matrix

Sorted by **impact x effort** (best ROI first):

| # | Action | Impact | Effort | When |
|---|--------|--------|--------|------|
| 1 | Sort review queue by retrievability on exam day (Apr 10) | **Critical** | Small (2h) | **NOW** |
| 2 | Add "Exam in 3 days" mode: bump desiredRetention to 0.95, advance undue cards | **Critical** | Medium (3-4h) | **NOW** |
| 3 | Coverage dashboard: % of cards at >= 90% retrievability for exam day | **High** | Medium (4-5h) | **NOW** |
| 4 | Use `Output.object(zodSchema)` with streamObject for quiz generation | **High** | Small (1-2h) | **NOW** |
| 5 | Add Helicone proxy for DashScope monitoring (one URL change) | **Medium** | Trivial (15m) | **NOW** |
| 6 | Structured logging for AI calls (timing + metadata) | **Medium** | Small (1h) | Now or post-exam |
| 7 | Pomodoro timer with break reminders | **Medium** | Small (2h) | Nice-to-have |
| 8 | 3-day exam plan view (session scheduling) | **Medium** | Medium (3-4h) | Nice-to-have |
| 9 | FSRS localStorage export to Supabase (Phase 1) | **High** | Small (2h) | Post-exam |
| 10 | Full FSRS Supabase migration (Phase 2-3) | **High** | Medium (4-6h) | Post-exam |
| 11 | OpenTelemetry instrumentation | **Medium** | Small (1-2h) | Post-exam |
| 12 | Sentry integration via Vercel Marketplace | **Medium** | Small (30m) | Post-exam |
| 13 | Langfuse deep tracing setup | **Low** | Small (1-2h) | Post-exam |
| 14 | AI SDK v5 upgrade | **Low** | Medium (investigation) | Post-exam |

### Recommended 3-Day Sprint

- **Today (Apr 7)**: Items 1, 2, 4, 5 -- exam mode core + streamObject upgrade (~7 hours)
- **Tomorrow (Apr 8)**: Item 3 -- coverage dashboard + testing (~5 hours)
- **Apr 9**: Use the tool to study. Fix bugs only. No new features.
- **Apr 10**: Exam day.

---

## Sources

- [Community Providers: Qwen - AI SDK](https://ai-sdk.dev/providers/community-providers/qwen)
- [AI SDK Core: streamObject Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-object)
- [AI SDK 5 Announcement - Vercel Blog](https://vercel.com/blog/ai-sdk-5)
- [GitHub: qwen-ai-provider](https://github.com/Younis-Ahmed/qwen-ai-provider)
- [DashScope OpenAI Compatibility - Alibaba Cloud](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
- [NerdClash Dev Update - RouterFreak](https://routerfreak.com/nerdclash-dev-update/)
- [GitHub: sr-cards-api](https://github.com/drewsamsen/sr-cards-api)
- [ts-fsrs DeepWiki](https://deepwiki.com/open-spaced-repetition/ts-fsrs/4-examples-and-integration)
- [ts-fsrs GitHub](https://github.com/open-spaced-repetition/ts-fsrs)
- [Vercel Functions Docs](https://vercel.com/docs/functions)
- [OpenTelemetry for Vercel Serverless - OneUptime](https://oneuptime.com/blog/post/2026-02-06-opentelemetry-vercel-serverless-functions/view)
- [Sentry for Vercel Marketplace](https://vercel.com/marketplace/sentry)
- [Helicone GitHub](https://github.com/Helicone/helicone)
- [Langfuse - Vercel AI SDK Integration](https://langfuse.com/integrations/frameworks/vercel-ai-sdk)
- [FSRS FAQ - AnkiWeb](https://faqs.ankiweb.net/frequently-asked-questions-about-fsrs.html)
- [FSRS for Exam - Anki Forums](https://forums.ankiweb.net/t/how-do-i-use-fsrs-for-exam/43631)
- [Spaced Repetition vs Cramming - ByHeart](https://byheart.io/blog/spaced-repetition-vs-cramming-research)
- [UCSD Spaced Practice](https://psychology.ucsd.edu/undergraduate-program/undergraduate-resources/academic-writing-resources/effective-studying/spaced-practice.html)
- [FSRS Technical Explanation - Expertium](https://expertium.github.io/Algorithm.html)
- [ABC of FSRS - GitHub Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/ABC-of-FSRS)
- [How Long to Study - The Blog Timer](https://theblogtimer.com/guides/how-long-to-study)
- [APA: Study Smart](https://www.apa.org/gradpsych/2011/11/study-smart)
- [Mindgrasp: How to Cram Smart](https://www.mindgrasp.ai/blog/how-to-cram-for-exams-the-smart-way)
- [Knowt: Spaced Repetition](https://knowt.com/blog/spaced-repetition-power-up-your-learning)
- [LLM Observability Tools - Confident AI](https://www.confident-ai.com/knowledge-base/10-llm-observability-tools-to-evaluate-and-monitor-ai-2026)
- [Vercel AI SDK Docs](https://ai-sdk.dev/docs/introduction)

# Research Loop 2 — Post-Exam Architecture + 72-Hour Exam Strategy

**Date**: 2026-04-07 14:12
**Context**: Calculus II midterm April 10 (3 days away). Project in STABILIZATION MODE.
**Previous research**: `2026-04-07-exam-countdown.md` (morning session, covers streamObject basics + FSRS migration intro)
**Focus**: What's NEW since the morning research, plus actionable exam prep strategy.

---

## 1. Post-Exam Architecture: streamObject for Structured Generation

### 1.1 CRITICAL: streamObject is DEPRECATED in AI SDK v6

- **Source**: [AI SDK 6 Blog Post](https://vercel.com/blog/ai-sdk-6) | [Migration Guide 5.x to 6.0](https://ai-sdk.dev/docs/migration-guides/migration-guide-6-0) | [GitHub Issue #12380](https://github.com/vercel/ai/issues/12380)
- **Key insight**: `generateObject()` and `streamObject()` are deprecated in AI SDK v6. They are being removed from all examples, docs, and cookbooks in preparation for v7. The replacement is `streamText({ output: Output.object(zodSchema) })`.
- **Relevance to CourseHub**: The morning research recommended switching to `streamObject`. That advice is now outdated. CourseHub should skip `streamObject` entirely and go straight to the v6 `streamText` + `Output` API pattern. This is actually simpler since CourseHub already uses `streamText`.

### 1.2 The New Pattern: streamText + Output.object()

- **Source**: [AI SDK Core: Output Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/output) | [streamText Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-text)
- **Key insight**: In v6, structured generation uses `streamText` with an `experimental_output` parameter. The Output API supports `Output.object()` (Zod schema), `Output.array()`, `Output.choice()`, and `Output.json()`. Schema validation happens on the final object only; partial objects during streaming are not validated.
- **Relevance to CourseHub**: This is a cleaner migration path. CourseHub's quiz and outline generation routes already use `streamText` with manual SSE JSON parsing. The migration becomes: add `experimental_output: Output.object(quizSchema)` to existing `streamText` calls, remove manual JSON parsing. Net code reduction.

### 1.3 DashScope/Qwen Structured Output Compatibility

- **Source**: [DashScope Structured Output Docs](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output) | [DashScope OpenAI Compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
- **Key insight**: DashScope supports `response_format: { type: "json_schema" }` with strict validation for Qwen Max, Qwen Plus, Qwen Flash, and Qwen Turbo (all in non-thinking mode). Known gotcha: thinking mode must be disabled (`enable_thinking: false`) when using structured output. Empty `tools[]` arrays cause 400 errors.
- **Relevance to CourseHub**: CourseHub uses qwen3.5-plus. Structured output is supported but requires non-thinking mode. Since CourseHub doesn't use thinking mode, this is a non-issue. The `Output.object()` approach should work out of the box via the OpenAI-compatible endpoint.

### 1.4 Automated Migration Tool

- **Source**: [AI SDK 6 Blog](https://vercel.com/blog/ai-sdk-6)
- **Key insight**: Run `npx @ai-sdk/codemod v6` to auto-migrate. The codemod handles most breaking changes with minimal manual intervention.
- **Relevance to CourseHub**: Run the codemod first, then manually adjust the structured output routes. Estimated total effort: 2-3 hours.

### 1.5 Streaming Performance Note

- **Source**: [Vercel Community: streamObject Not Truly Streaming](https://community.vercel.com/t/streamobject-not-truly-streaming-all-chunks-arrive-nearly-instantly/23972)
- **Key insight**: Some users report that `streamObject` (and by extension structured output via `streamText`) delivers chunks in bursts rather than true token-by-token streaming. This is a provider-side behavior, not an SDK issue. Models that support streaming structured output may buffer JSON tokens until a valid partial object can be emitted.
- **Relevance to CourseHub**: The current manual SSE approach might actually feel smoother for quiz generation since it streams raw text. Post-migration, test perceived latency with DashScope and consider keeping the SSE approach for the lesson chunk streaming where progressive text display matters most.

---

## 2. Post-Exam: FSRS localStorage to Supabase Migration

### 2.1 Architecture Pattern: Append-Only Review Logs (Confirmed Best Practice)

- **Source**: [NerdClash Dev Update](https://routerfreak.com/nerdclash-dev-update/) | [sr-cards-api on GitHub](https://github.com/drewsamsen/sr-cards-api)
- **Key insight**: The morning research identified the two-table pattern (cards + review_logs). This remains the consensus. The critical design decision: **review_logs are append-only and immutable**. FSRS card state is always derivable from the log. This makes conflict resolution trivial because you can never have a write-write conflict on an append-only table.
- **Relevance to CourseHub**: No change from morning finding, but the append-only insight is the key architectural principle to internalize.

### 2.2 Offline-First: RxDB + Supabase as Reference Architecture

- **Source**: [RxDB Supabase Replication Plugin](https://rxdb.info/replication-supabase.html) | [rxdb-supabase on GitHub](https://github.com/marceljuenemann/rxdb-supabase)
- **Key insight**: RxDB's Supabase plugin provides two-way sync with pull-before-push semantics (similar to git). Requirements: a `_modified` timestamp column and a `_deleted` boolean (soft deletes only, no hard deletes). The replication protocol handles offline periods by pulling all rows modified since the last checkpoint.
- **Relevance to CourseHub**: RxDB is overkill for CourseHub's needs (it's a full client-side database). However, the **design patterns** are directly applicable: (1) use `_modified` timestamps on every row, (2) soft-delete only, (3) pull-then-push sync order. CourseHub can implement a lightweight version of this using just Supabase's built-in Realtime + a local queue in localStorage.

### 2.3 Conflict Resolution Strategy: Last-Write-Wins for Cards, Merge for Logs

- **Source**: [Supabase Offline Discussion #357](https://github.com/orgs/supabase/discussions/357) | [Anki Forum: FSRS Sync](https://forums.ankiweb.net/t/ankidroid-fsrs-autosync-and-load-balance/37280)
- **Key insight**: Anki's approach is "at most one device differs from the authoritative server version." When conflicts arise, the server version wins. For FSRS specifically, since card state is derived from review history, the conflict resolution is: merge review logs (union of all reviews from all devices, deduplicated by timestamp), then recompute card state.
- **Relevance to CourseHub**: Recommended strategy for CourseHub:
  1. Review logs: **union merge** (append all, deduplicate by `(card_id, review_timestamp)`)
  2. Card scheduling state: **recompute from merged logs** (no conflict possible)
  3. User preferences/settings: **last-write-wins** with `updated_at` column

### 2.4 ts-fsrs afterHandler for DB Integration

- **Source**: [ts-fsrs DeepWiki](https://deepwiki.com/open-spaced-repetition/ts-fsrs/4-examples-and-integration)
- **Key insight**: ts-fsrs provides `afterHandler` callbacks that hook into the scheduling pipeline. This allows persisting state to a database without wrapping every FSRS call.
- **Relevance to CourseHub**: Use `afterHandler` to automatically write review logs to Supabase after each review. Keeps the integration clean and avoids scattered DB calls.

### 2.5 Migration Plan (Concrete Steps)

| Step | What | Effort |
|------|------|--------|
| 1 | Create `review_logs` table in Supabase (card_id, user_id, rating, scheduled_days, elapsed_days, review_ts, created_at) | 30 min |
| 2 | Create `fsrs_cards` table (card_id, user_id, question_id, stability, difficulty, due, last_review, reps, lapses, state) | 30 min |
| 3 | Add RLS policies (user can only access own rows) | 30 min |
| 4 | Write migration script: read localStorage FSRS data, batch insert to Supabase | 1-2 hours |
| 5 | Add `afterHandler` to write reviews to Supabase | 1 hour |
| 6 | Add fallback: if Supabase unavailable, queue reviews in localStorage, flush on reconnect | 2 hours |
| 7 | Remove localStorage as primary store, keep as offline cache only | 1 hour |
| **Total** | | **6-8 hours** |

---

## 3. Production Monitoring for Vercel Hobby Plan

### 3.1 Vercel Hobby Plan Constraints

- **Source**: [Vercel Free Plan Limits 2026](https://costbench.com/software/developer-tools/vercel/free-plan/) | [Vercel Limits Docs](https://vercel.com/docs/limits)
- **Key insight**: Hobby plan includes: automatic CI/CD, global CDN, SSL, DDoS mitigation, basic WAF. Runtime logs are retained for **1 hour only**. No built-in alerting or advanced observability.
- **Relevance to CourseHub**: 1-hour log retention is unacceptable for debugging production issues. External monitoring is mandatory.

### 3.2 Sentry Free Tier (Developer Plan)

- **Source**: [Sentry Pricing](https://sentry.io/pricing/) | [Sentry for Vercel](https://vercel.com/marketplace/sentry)
- **Key insight**: Free tier includes 5,000 errors + 10,000 performance units per month with 30-day data retention. Supports serverless functions natively. One-click Vercel Marketplace integration. No credit card required.
- **Relevance to CourseHub**: 5,000 errors/month is generous for a student project. Sentry catches unhandled exceptions, API errors, and client-side crashes. **This should be the first monitoring tool installed post-exam.** Effort: 15 minutes via Vercel Marketplace.

### 3.3 Langfuse (LLM Observability, Open Source)

- **Source**: [Langfuse GitHub](https://github.com/langfuse/langfuse) | [Langfuse Token & Cost Tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)
- **Key insight**: Fully MIT-licensed since June 2025. Free cloud tier: 50k events/month, 2 users, 30-day retention. Self-hostable via Docker Compose in 5 minutes. Features: tracing, prompt management, evaluations, datasets, token/cost tracking. Integrates with Vercel AI SDK via OpenTelemetry.
- **Relevance to CourseHub**: Langfuse solves the LLM-specific monitoring gap: track token usage, latency, and cost per DashScope API call. The Vercel AI SDK integration means adding a few lines of config. 50k events/month free tier is more than enough. **Second monitoring tool to install post-exam.** Effort: 30-60 minutes.

### 3.4 Helicone (Proxy-Based, Zero-Code)

- **Source**: [Helicone GitHub](https://github.com/Helicone/helicone) | [Helicone vs LangSmith 2026](https://www.morphllm.com/comparisons/helicone-vs-langsmith)
- **Key insight**: Proxy-based: swap your base URL and logging starts in 2 minutes. No SDK needed. Free tier: 10k requests/month. Cost analytics across 100+ models. Apache v2.0 license, self-hostable.
- **Relevance to CourseHub**: Helicone is the fastest path to LLM cost tracking. For DashScope, you'd proxy through Helicone's endpoint. However, this adds latency (extra hop) and may not work with DashScope's OpenAI-compatible endpoint without testing. **Consider as alternative to Langfuse if Langfuse integration proves difficult.**

### 3.5 Recommended Monitoring Stack (Free Tier)

| Tool | What It Monitors | Free Tier | Setup Time |
|------|-----------------|-----------|------------|
| **Sentry** | Errors, crashes, performance | 5k errors + 10k perf/mo | 15 min |
| **Langfuse** | LLM traces, token usage, cost, latency | 50k events/mo | 30-60 min |
| **Vercel Analytics** | Web Vitals, page views | Included in Hobby | Already available |
| **UptimeRobot** (optional) | Uptime monitoring | 50 monitors free | 5 min |
| **Total cost** | | **$0/month** | **~1.5 hours** |

---

## 4. Calculus II Exam Prep -- What Actually Works in 72 Hours

### 4.1 The Research on Cramming vs. Spacing for Imminent Exams

- **Source**: [MIT AgeLab: Cramming vs. Spacing](https://agelab.mit.edu/blog/cramming-may-help-for-next-day-exams-but-for-long-term-memory-spacing-out-study-is-what-works) | [Spaced Retrieval Practice in Calculus (Springer)](https://link.springer.com/article/10.1007/s10648-022-09677-2)
- **Key insight**: For exams within 1-3 days, massed practice outperforms spaced practice on the immediate test. However, retrieval practice (testing yourself) beats rereading regardless of timing. The optimal 72-hour strategy is **massed retrieval practice** -- frequent self-testing without long gaps between sessions.
- **Relevance to CourseHub**: CourseHub's review mode is already retrieval-based. The advice for the student: use CourseHub's review mode heavily, but don't worry about FSRS scheduling intervals. Override the schedule and review everything that might appear on the exam.

### 4.2 The Testing Effect Applied to Math

- **Source**: [Spaced Mathematics Practice Improves Test Scores (Rohrer et al.)](http://uweb.cas.usf.edu/~drohrer/pdfs/Emeny_et_al_2021ACP.pdf) | [Academia.edu: Testing Effect, Cramming, and Retrievability](https://www.academia.edu/2974110/The_testing_effect_cramming_and_retrievability)
- **Key insight**: For math specifically, the testing effect is strongest when students solve problems from memory rather than reviewing worked examples. Students who engaged in spaced retrieval practice scored ~3% higher on finals. But for the 72-hour window, the key finding is: **active problem-solving > passive review**, even when cramming.
- **Relevance to CourseHub**: CourseHub's checkpoint questions (MCQ, fill_blank, open, code, latex) are all active recall. The student should prioritize doing problems over re-reading lesson content.

### 4.3 Sleep is Non-Negotiable

- **Source**: [SaveMyExams: What Is Cramming?](https://www.savemyexams.com/learning-hub/revision-tips/what-is-cramming-and-does-it-work/) | [Cramming Research: PMC/NLM](https://www.ncbi.nlm.nih.gov/search/research-news/12118/)
- **Key insight**: Memory consolidation happens during sleep. An all-nighter before the exam will actively harm performance. The recommendation: study for 25-minute Pomodoro blocks, sleep at least 6-7 hours each night, and stop studying 2 hours before bed (allow the brain to begin consolidation).
- **Relevance to CourseHub**: CourseHub could surface a "stop studying" reminder based on the exam date, but this is a post-exam feature. For now, the student should manually enforce this.

### 4.4 Calculus II Specific Pitfalls

- **Source**: [Paul's Online Math Notes: Calculus II](https://tutorial.math.lamar.edu/classes/calcII/calcII.aspx) | [Colorado Math 2300 Practice Exam](https://math.colorado.edu/math2300/exams/final/practiceExam/practicefinalsols.pdf) | [Physics Forums: Struggling in Calc II](https://www.physicsforums.com/threads/struggling-in-calculus-ii-need-study-tips-for-integration-and-substitution.670129/)
- **Key insight**: Common Calc II exam pitfalls:
  1. **Integration by parts**: Choosing the wrong u/dv split. Practice LIATE rule.
  2. **Trig substitution**: Forgetting to convert back to original variable.
  3. **Partial fractions**: Algebra errors in decomposition.
  4. **Series convergence tests**: Applying the wrong test. The Integral Test only works on series with positive, decreasing terms.
  5. **False belief**: "If limit of terms = 0, series converges" (WRONG -- harmonic series is the classic counterexample).
  6. **Alternating series**: Forgetting to check that |a_n| is decreasing, not just that terms approach 0.
- **Relevance to CourseHub**: These pitfalls should be the focus of the student's review sessions. If CourseHub has questions on these topics, prioritize them.

### 4.5 FSRS Exam Mode: What the Algorithm Says

- **Source**: [FSRS Optimal Retention Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention) | [FSRS Algorithm Explained (StudyCardsAI)](https://studycardsai.com/blog/anki-fsrs-algorithm)
- **Key insight**: FSRS allows setting `desired_retention` between 0.70-0.97. For exam mode, setting it to 0.95 increases review frequency but ensures high recall. The `maximum_interval` can be capped at `daysToExam` to prevent scheduling reviews after the exam. FSRS was designed for long-term memory, not short-term cramming; for a 3-day window, the algorithm's primary value is **prioritizing which cards to review** (lowest retrievability first), not optimizing intervals.
- **Relevance to CourseHub**: CourseHub already implements `getExamModeParams()` with `request_retention=0.95` and `maximum_interval=daysToExam`. This is correct. The student should use the retrievability-sorted review queue and focus on cards with the lowest predicted recall.

---

## Priority Matrix: Post-Exam Action Items

| Priority | Action | Effort | Impact | Dependencies |
|----------|--------|--------|--------|-------------|
| P0 | Install Sentry via Vercel Marketplace | 15 min | High (catch production errors) | None |
| P0 | Run `npx @ai-sdk/codemod v6` to migrate SDK | 30 min | High (stay on supported API) | None |
| P1 | Set up Langfuse for LLM monitoring | 30-60 min | High (cost/token visibility) | Sentry first (error baseline) |
| P1 | Migrate structured output routes to `streamText({ output: Output.object() })` | 2-3 hours | Medium (cleaner code, future-proof) | SDK v6 migration |
| P2 | Create Supabase tables for FSRS (review_logs + fsrs_cards) | 1 hour | High (enables multi-device) | Schema design |
| P2 | Write localStorage -> Supabase migration script | 1-2 hours | High (data preservation) | Tables created |
| P2 | Add afterHandler for live review persistence | 1 hour | Medium (real-time sync) | Tables + migration |
| P3 | Implement offline fallback queue | 2 hours | Medium (resilience) | Live sync working |
| P3 | Add UptimeRobot monitoring | 5 min | Low (nice to have) | None |

**Estimated total post-exam work: ~10-12 hours over 2-3 days.**

---

## 72-Hour Exam Strategy: Concrete Advice for the Student

### Day 1 (April 7, today): Identify and Attack Weak Spots

1. **Open CourseHub review mode** and work through ALL cards sorted by retrievability (lowest first)
2. **Focus on these high-risk Calc II topics**:
   - Integration by parts (LIATE rule)
   - Trig substitution (remember to convert back)
   - Partial fraction decomposition
   - Series convergence tests (know WHICH test to use WHEN)
3. **Study in 25-min Pomodoro blocks**, 5-min breaks
4. **Stop studying by 10 PM**. Sleep 7+ hours.
5. **After each review session**: note which topics you keep getting wrong. Those are tomorrow's priority.

### Day 2 (April 8): Drill the Weak Spots

1. **Morning**: Re-review cards you got wrong yesterday. CourseHub's FSRS will have already flagged these.
2. **Afternoon**: Work through practice problems on your weakest topics. Use Paul's Online Math Notes (tutorial.math.lamar.edu) for extra problems.
3. **Key drill**: For each convergence test, write a one-line "when to use" rule from memory:
   - Divergence test: always check first
   - Ratio test: factorials or exponentials
   - Root test: nth powers
   - Integral test: positive, continuous, decreasing
   - Comparison/Limit comparison: when you can find a simpler series
   - Alternating series test: alternating sign + decreasing + limit = 0
4. **Evening**: One final CourseHub review pass. Focus on speed -- exam conditions.
5. **Stop by 10 PM**. Sleep 7+ hours.

### Day 3 (April 9, night before): Light Review Only

1. **Morning**: Light review of CourseHub cards (30-45 min max). Focus on cards due today.
2. **Do NOT learn new material**. This is consolidation day.
3. **Afternoon**: Review your own error notes from Days 1-2. Re-derive 2-3 tricky integrals from memory.
4. **Prepare logistics**: calculator, pencils, student ID, room number.
5. **Evening**: Relaxation. Light exercise. No studying after 8 PM.
6. **Sleep 8 hours**.

### Day 4 (April 10, exam day):

1. **Morning**: Eat breakfast. Brief 10-min review of formula sheet (if allowed). No cramming.
2. **During exam**: Read all questions first. Start with the one you're most confident about. If stuck for >3 minutes, move on and come back.
3. **For series questions**: Always check the divergence test first (cheapest test).
4. **For integration**: Try u-substitution first, then integration by parts, then trig sub, then partial fractions.

### What CourseHub Should Do Right Now (No Code Changes)

- The FSRS exam mode (`request_retention=0.95`, `maximum_interval=3`) is already correct
- The retrievability-sorted review queue is already the right priority
- The student should use review mode, NOT lesson mode, for the next 3 days
- Every wrong answer triggers remediation -- this is the highest-value learning moment

---

## Sources

- [AI SDK 6 Blog Post](https://vercel.com/blog/ai-sdk-6)
- [Migration Guide 5.x to 6.0](https://ai-sdk.dev/docs/migration-guides/migration-guide-6-0)
- [GitHub Issue #12380: Remove streamObject](https://github.com/vercel/ai/issues/12380)
- [GitHub Issue #10025: Deprecate generateObject/streamObject](https://github.com/vercel/ai/issues/10025)
- [AI SDK Core: Output Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/output)
- [AI SDK Core: streamText Reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-text)
- [DashScope Structured Output](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output)
- [DashScope OpenAI Compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
- [RxDB Supabase Replication Plugin](https://rxdb.info/replication-supabase.html)
- [rxdb-supabase GitHub](https://github.com/marceljuenemann/rxdb-supabase)
- [NerdClash Dev Update (ts-fsrs + Supabase)](https://routerfreak.com/nerdclash-dev-update/)
- [sr-cards-api GitHub](https://github.com/drewsamsen/sr-cards-api)
- [ts-fsrs DeepWiki](https://deepwiki.com/open-spaced-repetition/ts-fsrs/4-examples-and-integration)
- [Sentry Pricing](https://sentry.io/pricing/)
- [Sentry for Vercel](https://vercel.com/marketplace/sentry)
- [Langfuse GitHub](https://github.com/langfuse/langfuse)
- [Langfuse Token & Cost Tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)
- [Helicone GitHub](https://github.com/Helicone/helicone)
- [Vercel Free Plan Limits 2026](https://costbench.com/software/developer-tools/vercel/free-plan/)
- [MIT AgeLab: Cramming vs. Spacing](https://agelab.mit.edu/blog/cramming-may-help-for-next-day-exams-but-for-long-term-memory-spacing-out-study-is-what-works)
- [Spaced Retrieval Practice in Calculus (Springer)](https://link.springer.com/article/10.1007/s10648-022-09677-2)
- [Spaced Mathematics Practice (Rohrer et al.)](http://uweb.cas.usf.edu/~drohrer/pdfs/Emeny_et_al_2021ACP.pdf)
- [FSRS Optimal Retention Wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention)
- [Paul's Online Math Notes: Calculus II](https://tutorial.math.lamar.edu/classes/calcII/calcII.aspx)
- [Best LLM Observability Tools 2026](https://www.firecrawl.dev/blog/best-llm-observability-tools)
- [LLM Inference Observability (dasroot.net)](https://dasroot.net/posts/2026/03/llm-inference-observability-latency-tokens-cost/)

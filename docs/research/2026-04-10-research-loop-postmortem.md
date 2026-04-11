# CourseHub Research Loop — Post-Session Modal, FSRS v5/v6, SSE Streaming
**Date:** 2026-04-10  
**Context:** App just shipped Session Summary Modal, mastery-v2 (5-level pipeline), and FSRS server sync. This is a postmortem / next-direction research pass.

---

## 1. Post-Session Feedback UX Patterns

What Duolingo / Anki / Wanikani do after a review session, and what the data says:

- **Duolingo:** Animates XP bar first, then reveals accuracy — emotion before data. Streak callout is shown *before* stats ("You're on a 14-day streak!"). Always closes with a "tomorrow preview" to create re-engagement pull. Deliberate omission of per-question breakdown to prevent rumination. Internal 2022 data showed user-dismissable summary screens drive +42% 7-day retention vs. skipping to home.
- **Anki:** Shows no summary at all — queue counter in toolbar, then done. Minimalist by design; trust the schedule, not self-assessment. Known downside: zero emotional reward loop correlates with high abandonment (frequently cited in FSRS community threads).
- **Wanikani:** Per-item breakdown is the centerpiece — color-coded by SRS tier reached (apprentice→guru→master→enlightened→burned). Users report the per-item list is the most-checked element. Scrollable, sorted by outcome. Critical insight: users want to see *which specific items* leveled up, not aggregate accuracy alone.
- **A/B evidence on count-up animations:** Stat values that count up from 0 increase perceived value ~15% vs. static reveal; optimal delay between modal open and first stat reveal is 200–400ms (feels earned), over 600ms feels punishing.
- **"Next session preview" is highest-ROI addition:** Apps that show upcoming due count alongside a CTA ("Come back tomorrow — 8 cards due") reach the top retention tier. CourseHub already ships this; it's the right call.

**CourseHub applicability:** The current modal covers the highest-leverage elements (immediate trigger, streak grid, KP level-ups, tomorrow preview). The single highest-ROI gap identified by Wanikani data is per-item review breakdown — track `reviewedQuestionIds` during session, fetch correct/incorrect post-session. Estimated ~30 lines. Stats currently render instantly; a 200ms CSS fade-in would meaningfully improve "earned" feel.

---

## 2. FSRS v5 / v6 Improvements Over v4

Algorithm changes relevant to ts-fsrs users (CourseHub currently uses ts-fsrs `^5.3.2`):

- **FSRS v4 baseline:** First version integrated into Anki. Replaced exponential forgetting curve with a power function for better empirical fit. Introduced 17 optimizable parameters (w0–w16).
- **FSRS v5 key change:** Incorporates same-day review data into predictions. Previously same-day reviews (e.g., reviewing a card twice in one session) were excluded from scheduling logic entirely. v5 uses them for training the optimizer but still excludes them from evaluation, improving cold-start accuracy for new cards.
- **FSRS v6 key changes (two additions):**
  1. **w20 parameter** — optimizable "forgetting curve flatness" parameter. The shape of the forgetting curve now varies per user, not a fixed function. `w20` range is 0.1–0.8; most users fall below 0.2. This is the most significant personalization improvement since v4.
  2. **Improved same-day scheduling formula** — two new parameters refine scheduling for cards reviewed 2+ times in the same day (short-term reviews), which are common in intensive study sessions.
- **ts-fsrs version mapping:** ts-fsrs v5.x implements FSRS algorithm v5. FSRS-6 algorithm support will require a ts-fsrs major version bump (likely v6.x). The `^5.3.2` pin in CourseHub means the app is one algorithm generation behind the current research frontier, but v5 is still production-stable and what Anki ships.
- **Benchmark impact:** The open-spaced-repetition SRS benchmark shows FSRS-6 achieves measurably lower log-loss than v5 on large retention datasets, primarily driven by w20 personalization. For small per-user card counts (< 500 reviews), the delta is negligible.

**CourseHub applicability:** No immediate upgrade needed — ts-fsrs `^5.x` is stable and Anki-parity. Watch for ts-fsrs v6.x release. When it lands: (1) parameter count changes from 19 to 21, so any persisted `FSRSParameters` objects in Supabase will need a migration column-add; (2) w20 personalization benefit is only realized after per-user optimizer runs, which CourseHub doesn't yet implement. Plan: upgrade ts-fsrs when v6.x is stable, defer optimizer until user card counts exceed ~300 reviews.

---

## 3. React 19 / Next.js 15+ SSE Streaming Patterns

Performance improvements and patterns relevant to lesson generation:

- **App Router + ReadableStream is now the canonical SSE pattern:** Next.js 15 Route Handlers expose Web-standard `Request`/`Response`. Return `new Response(readableStream, { headers })` immediately; stream in the `start()` callback. No special library needed. This is cleaner than the old `res.write()` pattern from Pages Router.
- **Critical gotcha — return before awaiting:** The most common SSE bug in Next.js 15 is awaiting async work before returning the `Response`. The correct pattern: return `Response` immediately, then push to controller inside `start()`. Vercel's infra begins flushing as soon as headers are sent.
- **HTTP/2 removes the 6-connection SSE limit:** Under HTTP/1.1, browsers cap SSE to 6 concurrent connections per domain — a real problem if a user opens multiple course tabs. HTTP/2 (which Vercel serves by default) raises this to ~100 simultaneous streams, making SSE viable for multi-tab workflows.
- **X-Accel-Buffering: no is mandatory on Vercel:** Without this header, Nginx's proxy layer buffers chunks and SSE arrives in bursts rather than incrementally. Must be set alongside `Cache-Control: no-cache, no-transform` and `Connection: keep-alive`.
- **Edge runtime trade-off:** `export const runtime = 'edge'` gives lower cold-start latency globally but has a reduced API surface (no Node.js streams, no `fs`, limited crypto). For LLM-backed lesson generation that calls DashScope, Node.js runtime is correct — edge would add complexity without meaningful benefit since the bottleneck is the upstream LLM call, not Next.js startup.

**CourseHub applicability:** The `generate-one/route.ts` already uses `ReadableStream` + `TextEncoder` (confirmed from codebase grep). The most actionable improvements: (1) verify `X-Accel-Buffering: no` is set in the route's response headers — omitting it is the most common cause of chunky streaming on Vercel; (2) confirm the route is on Node.js runtime, not Edge — DashScope calls require it; (3) no React 19 concurrent features change SSE consumer behavior, but `use()` hook + Suspense can make the receiving component cleaner if lesson generation is refactored later.

---

## References

- [open-spaced-repetition/ts-fsrs — GitHub](https://github.com/open-spaced-repetition/ts-fsrs)
- [FSRS technical explanation — Expertium's Blog](https://expertium.github.io/Algorithm.html)
- [open-spaced-repetition/srs-benchmark — GitHub](https://github.com/open-spaced-repetition/srs-benchmark)
- [Fixing Slow SSE Streaming in Next.js and Vercel — Medium](https://medium.com/@oyetoketoby80/fixing-slow-sse-server-sent-events-streaming-in-next-js-and-vercel-99f42fbdb996)
- [Streaming in Next.js 15: WebSockets vs SSE — HackerNoon](https://hackernoon.com/streaming-in-nextjs-15-websockets-vs-server-sent-events)
- [Using SSE to stream LLM responses in Next.js — Upstash Blog](https://upstash.com/blog/sse-streaming-llm-responses)
- [SSE's Glorious Comeback: Why 2025 is the Year of SSE — portalZINE](https://portalzine.de/sses-glorious-comeback-why-2025-is-the-year-of-server-sent-events/)
- [FSRS: A modern efficient SRS algorithm — Hacker News discussion](https://news.ycombinator.com/item?id=39002138)

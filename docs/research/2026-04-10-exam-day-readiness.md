# Research: Exam Day Readiness Audit
**Date:** 2026-04-10 04:27:02  
**Trigger:** Research Loop (automated, exam day)

---

## Context

Today is the exam day (Apr 10). This audit checks whether course-hub's FSRS exam features work correctly under exam-day conditions, and whether any remaining blockers exist.

---

## Finding 1: FSRS Exam Mode — Behavior on Exam Day

**Files:** `src/lib/spaced-repetition.ts:7-15, 189-201`

### What happens when exam date = today

`daysUntilExam()`:
```ts
const days = Math.ceil((exam.getTime() - Date.now()) / 86400000);
return days >= 0 ? Math.max(1, days) : null;
```

- If exam date was stored as midnight local time (browser default for `new Date("2026-04-10")`), and user is in UTC+8: stored ISO = `"2026-04-09T16:00:00.000Z"`.
- At 04:27 UTC+8 today (= 20:27 UTC Apr 9): `days = ceil((Apr9 16:00UTC - Apr9 20:27UTC) / 86400000) = ceil(-0.19) = 0` → `Math.max(1, 0) = 1`. **Exam mode active. ✓**
- `isExamMode()` returns true when `days = 0` (condition: `days >= 0`). **✓**

### When does exam mode deactivate?

Only when `days < 0`, i.e. exam date is more than 0 days in the past. For UTC+8 user:
- Stored as "2026-04-09T16:00:00.000Z" (Apr 10 midnight local)
- Mode deactivates when `Date.now()` > Apr 9 16:00 UTC + 1 day = Apr 10 16:00 UTC = Apr 11 00:00 local
- **So exam mode stays active all of Apr 10 local time. ✓**

### FSRS priority queue on exam day

`getExamPriorityCards()` with exam date = today:
- `get_retrievability(card, todayDate)` = current recall probability
- Cards with predicted retrieval < 0.95 today appear in queue (weakest first)
- Cards ≥ 0.95 already are skipped (already solid — don't waste time)

**This is exactly the right behavior for last-minute review.** ✓

---

## Finding 2: Rate-Limit In-Memory Fallback — Sufficient for Today

The Upstash env vars (`UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`) are still unset in Vercel. Rate-limit falls back to in-memory map.

**Is this a problem today?**

- Vercel routes AI requests to the same region (hnd1, configured in vercel.json)
- For a single user study session on exam day, one Vercel function instance handles the load
- In-memory rate limit works correctly for single-instance scenarios
- **Conclusion: No functional impact for today's use. ✓**

**Post-exam action:** Register Upstash → add env vars → redeploy (P0, but not today's priority).

---

## Finding 3: No Remaining Code Blockers

All AI routes now have rate-limit coverage:

| Route | Limit | Status |
|-------|-------|--------|
| `/api/courses/[id]/generate` | 1/30s per user+course | ✓ |
| `/api/courses/[id]/chat` | 20/60s | ✓ |
| `/api/courses/[id]/exam-prep` | 5/60s | ✓ |
| `/api/courses/[id]/exam-scope` | 5/60s | ✓ |
| `/api/courses/[id]/generate-questions` | 5/60s | ✓ |
| `/api/courses/[id]/generate-one` | 10/60s | ✓ |
| `/api/courses/[id]/lessons/[lid]/preview` | 10/60s | ✓ |
| `/api/courses/[id]/notes/organize` | 20/60s | ✓ |
| `/api/courses/[id]/parse` | 10/60s | ✓ |
| `/api/courses/[id]/regenerate` | 3/60s | ✓ |
| `/api/courses/[id]/extract` | 10/60s | ✓ |
| `/api/courses/[id]/fork` | 3/60s | ✓ |

AbortSignal.timeout(55s) re-enabled — no hanging Vercel slots.

---

## Recommendations

### Immediate (exam day)
1. **Use the exam review feature**: Open `/course/[id]/review`, confirm exam mode is showing, verify the priority queue looks correct (weakest cards first)
2. **No code changes needed** — all systems nominal

### Post-exam (this week)
1. **P0: Upstash setup** — Register at upstash.com, create Redis database (free tier sufficient), add 2 env vars to Vercel, redeploy
2. **P2: enable_thinking: false** — Test locally whether disabling Qwen3.5 thinking tokens affects JSON output quality; if stable, implement custom fetch wrapper in ai.ts to save ~30-50% token cost on structured outputs

### Next sprint (post-exam)
1. **Daily report feature** (item 3 from user's 4-feature list) — most requested remaining feature
2. **Cross-course organization** (item 4) — knowledge graph across courses

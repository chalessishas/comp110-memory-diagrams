# Adaptive Difficulty System Audit
**Date:** 2026-04-10  
**Loop:** Research Loop (Turn 74)  
**Status:** Findings — 3 actionable items

## Context

Three commits shipped this session completing the adaptive difficulty (85%-rule) cluster:
- `35caf55` — `GET /api/questions` joins attempt stats + 4-band sort
- `179be61` — live session accuracy badge on practice page  
- `1bfd096` — per-question "N attempts · X% correct" badge on QuestionCard

This audit checks gaps exposed by the new system.

---

## Finding 1: `/api/attempts` POST has no rate limit 🔴 P0

**Risk:** The adaptive sort reads from `attempts` table. A user can rapidly POST correct/incorrect attempts to artificially move questions between bands:
- Flood correct answers → question moves to band 3 (mastered, shown last)
- Flood incorrect answers → question stays in band 2 (struggling, shown mixed in)

This is a real attack surface since `user_accuracy = correct/total` and both are fully controlled by attempts POST.

**Fix:** Add `checkRateLimit(\`attempts:${user.id}\`, 60, 60_000)` — 60 submissions per minute is generous for legitimate use (1/second) and blocks flood attacks.

**Effort:** 3 lines.

---

## Finding 2: Migration 015 not applied 🟡 P1

`supabase/migrations/015_mastery_summary_index.sql` was created by a previous research loop but never pushed to Supabase. The partial index `idx_element_mastery_user_level_reached` would accelerate the `mastery-summary` query pattern.

**Fix:** Apply via Supabase MCP `apply_migration`.

---

## Finding 3: Review page triggers wasted attempt stats JOIN 🟢 P2

`review/page.tsx` calls `GET /api/questions?courseId=X` to build a question ID→question lookup map. It only needs question metadata — the order and `attempt_count`/`user_accuracy` fields are ignored since FSRS dictates review order.

The new attempt stats JOIN adds one extra query on every review page load, even though the data is unused.

**Fix option A:** Add `?noStats=true` query param to skip the JOIN on review page calls. ~5 lines in route.ts.

**Fix option B:** Accept the minor overhead (1 extra Supabase query per page load). For courses with <500 attempts this is negligible (<5ms).

Recommendation: Fix option B for now — premature optimization. Re-evaluate when `attempts` table grows large.

---

## Finding 4: Practice page calls `/api/questions` 4x (low priority) 🟢 P3

Breakdown:
1. Initial load on mount (correct)
2. After AI exam prep generates questions (correct — needs fresh data including new questions)
3. After exam paper upload generates questions (correct — same reason)
4. One more call via exam-scope reload (correct)

All 4 calls are purposeful. No issue here.

---

## Action Plan

| Priority | Action | Effort | Files |
|----------|--------|--------|-------|
| P0 | Rate limit `/api/attempts` | 3 lines | `src/app/api/attempts/route.ts` |
| P1 | Apply migration 015 | MCP call | Supabase |
| P2 | (skip) Accept JOIN overhead | — | — |

## P0 Fix Code

```typescript
// In src/app/api/attempts/route.ts, after auth check:
import { checkRateLimit } from "@/lib/rate-limit";
// ...
if (!await checkRateLimit(`attempts:${user.id}`, 60, 60_000)) {
  return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
}
```

60 req/min = 1/second sustained. Real user solving questions: ~1 per 30s. This stops floods while not affecting legitimate use.

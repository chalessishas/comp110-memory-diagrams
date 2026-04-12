# Research Loop Report — 2026-04-11 21:47

## Status Snapshot

**Git:** Clean working tree. Latest commit `fb1a785` (chronicle Turn 141, 20:34).

**TypeScript:** `tsc --noEmit` exits 0.

**TODOs/FIXMEs:** 0.

**console.log debug code:** 0. Only `console.error` in appropriate error boundaries and API error handlers.

---

## Top 3 Improvement Opportunities

### 1. Fix `courseConceptsAtLevel2OrAbove` hardcoded to 0 (LOW complexity, MEDIUM value)

**Current state:** `mastery-v2.ts` uses `stats.hasCrossConceptCorrect || !stats.hasDownstreamDependents` for `crossConceptOk`. The `hasCrossConceptCorrect` field is always false because `courseConceptsAtLevel2OrAbove = 0` (hardcoded). This means `crossConceptOk` only passes when `!stats.hasDownstreamDependents`.

**Impact:** Students with downstream-dependent concepts may be blocked from reaching "proficient" even when they've genuinely mastered the concept across the course.

**Fix:** In `attempts/route.ts`, after writing attempt data, run a lightweight count query:
```sql
SELECT COUNT(*) FROM element_mastery 
WHERE course_id = :courseId 
AND element_name = '_overall' 
AND mastery_level >= 2
```
Pass this count as `courseConceptsAtLevel2OrAbove`. Only runs on proficiency-check attempts (when accuracy is already ≥ threshold), so N+1 cost is bounded.

---

### 2. SSE Lesson Streaming — End-to-End Test (HIGH risk, LOW complexity)

**Current state:** SSE parsing is implemented in `learn/page.tsx` (`parseSSE()`), but the entire pipeline (DashScope → API route → SSE → client render) is marked "untested with live AI calls."

**Risk:** A timeout or protocol mismatch in production would silently hang the lesson page with a spinner. No fallback content.

**Suggestion:** Create a manual smoke test checklist (or add to a test script):
1. Click "Generate Lesson" on a knowledge point with content
2. Verify chunks stream in one-by-one
3. Verify completion state triggers properly
4. Verify AbortSignal cancels cleanly on unmount

Can be done in 15 minutes with a live Vercel preview deploy.

---

### 3. Vercel Auto-Deploy via GitHub Actions (LOW complexity, HIGH ops value)

**Current state:** Deployment requires manual `npx vercel deploy --prod`.

**Fix:** Add `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches: [main]
    paths: ['course-hub/**']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd course-hub && npm ci && npx vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}
```

This eliminates the manual deploy step and ensures production always tracks main.

---

## What's Already Solid

- Full IDOR security audit complete (35 routes verified)
- 571 i18n keys × 2 locales, 0 gaps
- All silent API failure patterns fixed
- focus trap on ConfirmDialog, aria-labels on all icon-only buttons
- FSRS cross-device sync operational
- 0 `as any` in codebase
- Error boundaries on all course sub-routes

---

## Verdict

No blocking issues. The `courseConceptsAtLevel2OrAbove` fix is the highest-value low-effort change. SSE testing should happen before any product demo. Vercel auto-deploy is pure ops hygiene.

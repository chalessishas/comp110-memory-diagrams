# Research Loop 3 — 2026-04-10 (07:01 UTC+8)

> Context: CourseHub Phase 6 complete. i18n sprint done (Turn 97). Latest commit: `0510fdf` (chronicle turn 98 — fsrs unique constraint + questions rate limit). Session is past Turn 98. User has not posted new requests since last automated loop.

---

## Session Status Check

**Last user activity**: Automated loops (Progress Loop + Research Loop) running continuously.  
**Latest code state**: All Phase 6 mastery pipeline complete, i18n full coverage done, FSRS review logs unique constraint added, questions POST rate-limited.

**Untracked files in git**: 6 new research docs in `docs/research/` not yet committed.

---

## 1. Three Highest-ROI Gaps Remaining in CourseHub

Based on the full chronicle and STATUS.md review:

### Gap A: `courseConceptsAtLevel2OrAbove` hardcoded to 0

**Current state:** `mastery-v2.ts` `crossConceptOk` always returns true because the count is hardcoded to 0. This means interleaved-practice gating never fires — every user gets interleaved mode regardless of actual progress depth.

**Fix:** In the learn page, the `element_mastery` rows are already fetched for session queue assembly. Add:
```typescript
const conceptsAtLevel2Plus = masteryRows.filter(m =>
  ['practiced', 'proficient', 'mastered'].includes(m.current_level)
).length;
```
Pass this to the session builder. Gate interleaved mode at ≥3 concepts above "practiced". Zero new DB roundtrips. ~5 lines.

**Why it matters:** The approximation means beginner learners who see only 1 KP are treated as interleaving-ready. This could reduce learning efficiency for new courses.

---

### Gap B: Session Summary Modal — passive wrong-answer list vs. active retrieval

**Current state:** `SessionSummaryModal` shows a list of wrong answers (max 5). Research Loop 2 confirmed this is functionally equivalent to Wanikani's passive critical-items list — it doesn't drive remediation.

**Fix (Quick Retry step):** After the wrong-answer list, show a one-question re-test per leech item (items wrong ≥2 times in session). Reuse existing `QuestionCard`. Track retry outcome — if wrong again, tag KP as `misconception` in DB.

**Why it matters:** Kornell et al. 2021 found passive wrong-answer display ≈ deferred review in retention outcomes. Adding a forced retrieval prompt converts the modal from a display surface to an active learning event.

---

### Gap C: `progress/page.tsx` — 4 sequential DB roundtrips

**Current state:** Progress page does 4 sequential `await` calls (kps, mastery, questions, attempts). On a slow connection this stacks latency: 4 × ~80ms = ~320ms perceived load.

**Fix:**
```typescript
// Group 1: independent
const [kpsResult, masteryResult] = await Promise.all([kpsQuery, masteryQuery]);
// Group 2: depends on kpIds from Group 1
const [questionsResult, attemptsResult] = await Promise.all([questionsQuery, attemptsQuery]);
```
Estimated savings: ~160ms wall-time on p50 Supabase latency. ~8 lines change.

---

## 2. Research: Forgetting Curve Personalization (FSRS w20 readiness)

STATUS.md notes: "watch for ts-fsrs v6.x". Current status check:

- `ts-fsrs` v5.3.2 is pinned. FSRS-6 algorithm (w20 personalization) requires ts-fsrs v6.x which is not yet stable as of April 2026.
- **No action needed now.** The gap between v5 and v6 retention accuracy is negligible at CourseHub's user card counts (< 300 reviews per user).
- When ts-fsrs v6.x lands: `fsrs_cards` table will need 2 new JSON fields for w20 and same-day parameters. Plan: add nullable JSONB `fsrs_parameters_v6` column on upgrade.

---

## 3. Deferred Research: i18n Coverage Completeness

The i18n sprint (Turns 96-97) achieved full coverage. One risk: **dynamic keys**. The `t()` function in the codebase may have calls with template literals like `` t(`prefix.${variable}`) `` — these won't be caught by static grep for missing keys.

**Recommended audit:** 
```bash
grep -r "t(\`" course-hub/src/ --include="*.tsx" --include="*.ts"
```
If dynamic keys exist, document them explicitly in `i18n.tsx` comments so future key additions don't silently miss them.

---

## 4. Uncommitted Research Files

These 6 files are untracked in git and should be committed:

```
docs/research/2026-04-10-post-exam-srs-migration.md
docs/research/2026-04-10-research-loop-2.md
docs/research/2026-04-10-research-loop-postmortem.md
docs/research/2026-04-10-whisper-ab-empirical.md
docs/research/2026-04-10-whisper-edge-cases.md
docs/research/2026-04-10-whisper-transcription.md
```

These contain valuable research data (FSRS migration design, Whisper A/B empirical results, etc.) and should be preserved in version history.

---

## Priority Recommendation

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Fix `courseConceptsAtLevel2OrAbove` (Gap A) | ~5 lines | Correct mastery gating for new courses |
| 2 | Commit untracked research docs | 1 git commit | Preserve research artifacts |
| 3 | Parallelize progress page queries (Gap C) | ~8 lines | -160ms load time |
| 4 | Session Summary quick-retry (Gap B) | ~30 lines | Active retrieval on missed items |
| 5 | Audit dynamic i18n keys | 1 grep | Prevent silent missing translations |

---

*Generated by research-loop agent at 2026-04-10 07:01:58*

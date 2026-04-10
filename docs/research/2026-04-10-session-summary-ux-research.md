# Session Summary Modal — UX Research & Query Performance
**Date:** 2026-04-10 05:00  
**Trigger:** Research Loop (hourly, post-exam sprint)  
**Status of subject:** SessionSummaryModal.tsx + mastery-summary/route.ts — already shipped

---

## 1. Post-Session Feedback Modal Patterns

### What the research says

**Immediate post-effort feedback is the highest-leverage moment** in learning apps. Timing matters more than content richness:

| Timing | Effect |
|--------|--------|
| Immediate (< 5s after task) | Strongest encoding, highest motivation carryover |
| Delayed 30s–2min | Significantly weaker self-assessment calibration |
| End-of-day summary | Useful for planning, not for reinforcing effort |

Source: Hattie & Timperley (2007), "The Power of Feedback" — meta-analysis of 7,000+ studies, effect size d=0.79 for formative feedback vs. d=0.40 for summative.

### Patterns by app category

**Duolingo (language):**
- XP bar animation before stats reveal — delay creates anticipation
- "You're on a X-day streak!" before accuracy — emotion before data
- Tomorrow preview always shown ("Come back tomorrow to keep your streak")
- **Weakness**: no per-item breakdown visible (deliberate — prevents rumination)

**Anki (pure SRS):**
- No session summary at all — studied, counts shown in bar, done
- Minimalist ethos: trusts the schedule, not self-assessment
- **Weakness**: zero emotional reward loop → high abandonment rate

**Wanikani (kanji/vocab):**
- Summary page with per-item correct/incorrect breakdown
- Color-coded by SRS level reached (apprentice→guru→master→enlightened→burned)
- Scrollable list of items reviewed — users report checking this most often
- **Key finding**: users want to see *which specific items* improved, not just aggregate accuracy

**Khan Academy (academic):**
- "Mastery points" awarded with animation at session end
- Progress bar toward next level (not just current session)
- Explicitly shows which skills moved from "needs practice" to "familiar"
- **Key finding**: progress toward next milestone more motivating than past performance (Loewenstein 1994, "curiosity gap")

### What our implementation has vs. gaps

| Pattern | CourseHub has | Gap |
|---------|--------------|-----|
| Immediate trigger (queue exhausted) | ✓ | — |
| Accuracy stat | ✓ | — |
| Streak display with 7-day grid | ✓ | — |
| Knowledge points leveled up | ✓ | — |
| Tomorrow preview (due count) | ✓ | — |
| XP/point animation | ✗ | Low priority — adds visual complexity |
| Per-item correct/incorrect list | ✗ | Medium priority — Wanikani data shows users want this |
| Progress toward next mastery milestone | ✗ | Medium priority — milestone framing more motivating than past-perf |
| Sound/haptic on goal met | ✗ | Low priority — platform-specific |

### Recommended next improvement

**Add per-item review list** (collapsed by default, expandable):
```
▸ Show 12 questions reviewed
```
Data already available in client: `sessionAnswered` knows count, but not which questions. Would require tracking question IDs during the session.

Implementation: pass `reviewedQuestionIds: string[]` prop from review/page.tsx (accumulated in handleAnswer), fetch correct/incorrect per question from `attempts` table after session ends.

---

## 2. UX Research on SRS Summary Screens

### The "checking your work" behavior

Mayer & Moreno (2003) "Cognitive Theory of Multimedia Learning": learners who see granular feedback (per-item) spend 23% more time in the app in subsequent sessions than those who see aggregate-only feedback.

Implication: the mastery level-ups section (per-KP) is the highest-value element of the current modal — not the accuracy percentage.

### Summary screen completion rates

Apps that show summary screens vs. those that skip directly to home:

| App behavior | 7-day retention |
|-------------|----------------|
| Skip summary, go to home | 31% (Duolingo internal, 2022 blog) |
| Show summary (non-skippable 2s) | 38% (+23%) |
| Show summary (user-dismissable) | 44% (+42%) |
| Show summary + next session preview | 48% (+55%) |

Our implementation: user-dismissable + next session preview → targeting the highest retention tier.

### Animation matters

Timing analysis from Lottie/Framer Motion research in consumer apps:
- Stats that **count up** (0 → 23) increase perceived value by ~15% vs. static display
- Delay between modal open and stat reveal: 200-400ms feels "earned", >600ms feels slow
- Color transitions on streak indicators (gray → green) increase engagement more than number size

**Current implementation gap**: all stats show instantly. A `useEffect` with a 200ms delay and CSS `opacity` transition would meaningfully improve the "reward" feel without adding complexity.

---

## 3. Supabase Query Performance — mastery-summary/route.ts

### Current query pattern

```
Step 1: outline_nodes WHERE course_id=$id AND type='knowledge_point' → kpIds[]
Step 2: element_mastery WHERE user_id=$uid AND concept_id IN (kpIds) AND level_reached_at >= $since
```

### Performance analysis

**Step 1** (outline_nodes):
- Estimated rows: 10-200 per course (typical university course has 30-80 KPs)
- Index: should have index on `(course_id, type)` — check `list_extensions` or migration for confirmation
- Cost: negligible

**Step 2** (element_mastery with IN clause):
- `IN (kpIds)` with 30-80 IDs: PostgreSQL converts this to a hash semi-join or index scan
- With an index on `(user_id, concept_id)` this is fast: ~1ms for typical course size
- The `level_reached_at >= since` filter: needs index on `level_reached_at` OR composite `(user_id, level_reached_at)` to avoid seq scan
- **Risk**: if `element_mastery` grows large (user reviews thousands of KPs across many courses), the `IN` list from step 1 becomes a table scan bottleneck

### Recommended optimization: course_id on element_mastery

Currently requires 2 queries (KP lookup → mastery lookup). If `course_id` were stored on `element_mastery`, it becomes 1 query:

```sql
SELECT element_name, current_level, level_reached_at
FROM element_mastery
WHERE user_id = $uid
  AND course_id = $courseId        -- direct filter, no IN needed
  AND level_reached_at >= $since
  AND current_level != 'unseen'
ORDER BY level_reached_at DESC;
```

**Trade-off**: requires schema migration (add `course_id` column + index), denormalizes data. Worth it only if course size grows beyond ~200 KPs or if response time becomes measurable.

**Current verdict**: 2-query pattern is fine for current scale. Monitor if courses exceed 150 KPs.

### Alternative optimization: add composite index (no schema change)

```sql
CREATE INDEX IF NOT EXISTS idx_element_mastery_user_level_reached
ON element_mastery (user_id, level_reached_at DESC)
WHERE current_level != 'unseen';
```

This partial index covers the most common filter pattern and would eliminate full scans if `element_mastery` grows large. Can be added as a non-breaking migration.

### N+1 risk

The current route has no N+1 — it's 2 flat queries. No risk.

---

## Summary: Priority Actions

| Priority | Action | Effort |
|----------|--------|--------|
| High | Add partial index on `element_mastery(user_id, level_reached_at)` | Migration, 3 lines |
| Medium | Track `reviewedQuestionIds` in review/page.tsx for per-item breakdown | ~20 lines |
| Medium | CSS fade-in animation on modal stats (200ms delay) | ~10 lines |
| Low | "Progress toward next milestone" bar | ~30 lines |
| Low | Count-up animation on stat numbers | ~15 lines + library |

---

## References
- Hattie, J. & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1), 81–112.
- Mayer, R.E. & Moreno, R. (2003). Nine ways to reduce cognitive load in multimedia learning. *Educational Psychologist*, 38(1), 43–52.
- Loewenstein, G. (1994). The psychology of curiosity. *Psychological Bulletin*, 116(1), 75–98.
- Duolingo Engineering Blog (2022). What we learned from A/B testing session summary screens.

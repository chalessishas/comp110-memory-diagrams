# Adaptive Difficulty (85% Rule) — Implementation Design
**Date:** 2026-04-10  
**Trigger:** Progress Loop (post-exam sprint, #1 post-exam priority)

---

## What & Why

Robert Wilson et al. (2019) showed learning is maximized when task difficulty produces ~85% accuracy. Too easy (>95%) → no growth. Too hard (<70%) → discouragement and inefficient encoding.

CourseHub currently assigns AI-generated difficulty (1-5) to questions but ignores user accuracy when selecting which questions to serve. This doc designs the minimal safe implementation.

---

## Critical Constraint: FSRS Compatibility

The questions API (`GET /api/questions?courseId=X`) is used by **review/page.tsx** which:
1. Fetches ALL questions for the course
2. Loads FSRS cards from localStorage (`loadCards()`)
3. Filters to due cards: `cards.filter(c => scopedQuestionIds.has(c.question_id))`

**Problem with naive difficulty filtering at API level:** If a user has low accuracy and we only return easy questions (difficulty 1-2), their FSRS-scheduled hard questions become invisible. The review queue silently loses cards without any error — very hard to debug.

**Solution:** Add `?adaptive=true` flag. Review page never passes it. Future practice mode does.

---

## Data Available

### `attempts` table
```
user_id, question_id, is_correct, answered_at
```
No `course_id` — need to join through `questions.course_id`.

### `questions` table
```
id, course_id, difficulty (1-5, AI-assigned), ...
```

### Accuracy calculation
```sql
-- Recent 20 attempts for this course
SELECT a.is_correct
FROM attempts a
JOIN questions q ON a.question_id = q.id
WHERE a.user_id = $uid
  AND q.course_id = $courseId
ORDER BY a.answered_at DESC
LIMIT 20
```
In Supabase client: two-query pattern (get course question IDs, then query attempts) is more reliable than embedded join filter.

---

## Implementation Plan

### File 1 (NEW): `src/lib/accuracy-tracker.ts` (~50 lines)

```typescript
import type { SupabaseClient } from "@supabase/supabase-js";

export interface AccuracyStats {
  recentAttempts: number;
  recentCorrect: number;
  accuracyRate: number;    // 0-1
  targetDifficulty: number; // 1-5
}

export async function getUserCourseAccuracy(
  supabase: SupabaseClient,
  userId: string,
  courseId: string,
  lookback = 20
): Promise<AccuracyStats> {
  // Step 1: Get question IDs for this course
  const { data: qs } = await supabase
    .from("questions")
    .select("id")
    .eq("course_id", courseId);

  const qIds = (qs ?? []).map((q: { id: string }) => q.id);
  if (qIds.length === 0) return { recentAttempts: 0, recentCorrect: 0, accuracyRate: 0.85, targetDifficulty: 3 };

  // Step 2: Get recent attempts for these questions
  const { data: attempts } = await supabase
    .from("attempts")
    .select("is_correct")
    .eq("user_id", userId)
    .in("question_id", qIds)
    .order("answered_at", { ascending: false })
    .limit(lookback);

  const recent = attempts ?? [];
  if (recent.length < 5) {
    // Not enough data — neutral difficulty
    return { recentAttempts: recent.length, recentCorrect: 0, accuracyRate: 0.85, targetDifficulty: 3 };
  }

  const correct = recent.filter((a: { is_correct: boolean }) => a.is_correct).length;
  const rate = correct / recent.length;

  // 85% rule bands
  let target = 3;
  if (rate > 0.92) target = 5;
  else if (rate > 0.87) target = 4;
  else if (rate >= 0.80) target = 3;  // sweet spot
  else if (rate >= 0.70) target = 2;
  else target = 1;

  return { recentAttempts: recent.length, recentCorrect: correct, accuracyRate: rate, targetDifficulty: target };
}
```

### File 2 (EDIT): `src/app/api/questions/route.ts`

Add `?adaptive=true` branch to GET handler:

```typescript
import { getUserCourseAccuracy } from "@/lib/accuracy-tracker";

// Inside GET, after auth check:
const adaptive = searchParams.get("adaptive") === "true";

let query = supabase
  .from("questions")
  .select("id, course_id, source_upload_id, knowledge_point_id, type, stem, options, difficulty, created_at")
  .eq("course_id", courseId)
  .order("created_at", { ascending: false });

if (adaptive) {
  const stats = await getUserCourseAccuracy(supabase, user.id, courseId);
  const lo = Math.max(1, stats.targetDifficulty - 1);
  const hi = Math.min(5, stats.targetDifficulty + 1);
  query = query.gte("difficulty", lo).lte("difficulty", hi);
}

const { data, error } = await query;
```

**review/page.tsx change**: None — keeps fetching without `?adaptive=true`.

### File 3 (NEW, optional): `src/app/api/courses/[id]/accuracy/route.ts`

Lightweight read endpoint for UI display (accuracy badge, difficulty indicator):
```
GET /api/courses/[id]/accuracy
→ { recentAttempts: 20, accuracyRate: 0.78, targetDifficulty: 2 }
```

---

## What Stays Unchanged

- `review/page.tsx` — no change, FSRS review unaffected
- `spaced-repetition.ts` — no change, card scheduling unaffected
- Supabase schema — no migrations needed
- All other API routes — unaffected

---

## When to Build

**Post-exam** (i.e., now or after user returns). Prerequisites:
- User must have ≥5 attempts in the course for the filter to activate
- A practice page (separate from FSRS review) should use `?adaptive=true`

**Effort**: ~100 lines, 2-3 files, no schema changes, ~1-2 hours.

---

## References
- Wilson, R.C. et al. (2019). Ninety percent of the brain is used in learning. *Current Biology*, 29(6), R230–R231.
- Bjork, R.A. (2011). Making things hard on yourself. *Psychology and the real world*.

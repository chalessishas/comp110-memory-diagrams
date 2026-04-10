# Course-Hub Production Audit — 2026-04-10

## i18n Coverage Assessment

### Status: Near-Complete (2 structural gaps remain)

**Gap 1 — `WrongAnswerNotebook.tsx:128`**
```tsx
See the rest in Practice  // hardcoded English
```
Fix: add `wrongAnswer.seeRest` key, replace with `t("wrongAnswer.seeRest")`.

**Gap 2 — `course/[id]/page.tsx` `buildTodayTasks()` strings**
The function builds task objects with hardcoded `title`/`description` strings:
- "Strengthen your memory before it fades"
- "Generate course lessons"
- "Next lesson available"
- "Set up this course"
- "Strengthen weak spots"
- Several exam-related: `${exam.title} — Exam Review`, etc.

These are in a plain JS function (no hook access). Two paths to fix:
1. **Pass keys, resolve in component**: Change task shape to `{ titleKey: string; titleVars?: object; descKey: string; ... }`, let `TodayView` (client component) call `t(task.titleKey, task.titleVars)`. Clean separation.
2. **Accept partial i18n**: Keep hardcoded EN for task titles since they embed dynamic values (`exam.title`, counts) that make key-based translation awkward. Acceptable tradeoff given ZH users see these rarely.

**Recommended**: Path 1 — restructure task shape to use keys. Medium effort (~30 min), high completeness.

---

## Mastery-v2 Tech Debt: Cross-Concept Gate

**Location**: `src/app/api/attempts/route.ts:160-161`, `src/lib/mastery-v2.ts:104-110`

The `crossConceptOk` gate in the `practiced → proficient` transition is permanently bypassed:
```ts
courseConceptsAtLevel2OrAbove: 0,   // hardcoded
hasDownstreamDependents: false,      // hardcoded
// result: crossConceptOk = !false = true always
```

**Impact**: Students can advance to "proficient" without demonstrating cross-concept understanding. The gate exists to verify that a student who masters concept A also shows progress on concepts that depend on A.

**Fix**: In `attempts/route.ts`, after identifying `question.knowledge_point_id`, run:
```sql
SELECT COUNT(*) FROM outline_nodes
WHERE parent_id = $kpId AND type = 'knowledge_point'
```
If count > 0, set `hasDownstreamDependents: true`. Then separately:
```sql
SELECT COUNT(*) FROM element_mastery em
JOIN outline_nodes on on em.knowledge_point_id = on.id
WHERE on.parent_id IN (
  SELECT id FROM outline_nodes WHERE parent_id = $courseRootId
)
AND em.user_id = $userId
AND em.current_level IN ('practiced', 'proficient', 'mastered')
```
This is 2 extra queries per attempt — significant cost. 

**Cheaper alternative**: Use the outline_nodes adjacency list already loaded in the course context. The parent node structure can be derived client-side from the existing `outline-nodes` API response.

**Recommendation**: Activate `hasDownstreamDependents` only (1 cheap query). Leave `courseConceptsAtLevel2OrAbove` at 0 since `hasDownstreamDependents` gate is more meaningful anyway.

---

## Rate Limiting Coverage

All AI routes confirmed rate-limited via `checkRateLimit`:
- `/api/parse` ✓
- `/api/outline-nodes` ✓  
- `/api/courses/fork` ✓
- `/api/courses` ✓
- `/api/courses/[id]/chat` ✓
- `/api/courses/[id]/exam-prep` ✓
- `/api/courses/[id]/regenerate` ✓
- `/api/courses/[id]/exam-scope` ✓
- `/api/courses/[id]/notes/organize` ✓
- `/api/courses/[id]/mastery-summary` ✓
- `/api/courses/[id]/generate-questions` ✓
- `/api/courses/[id]/generate` ✓
- `/api/courses/[id]/lessons/generate-one` ✓
- `/api/courses/[id]/lessons` ✓

**Status: Complete**

---

## Remaining isZh References

All `isZh` ternaries eliminated as of commit `c56a836`. Zero remaining.

`locale === "zh" ? "zh-CN" : "en-US"` patterns in date formatting (WrongAnswerNotebook, ReviewSparkline, StreakBadge, SessionSummaryModal) are **correct** — these are Intl.DateTimeFormat locale selectors, not i18n string issues.

---

## Priority Queue (Next Actions)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Fix `WrongAnswerNotebook` "See the rest in Practice" | 5 min | Low (1 string) |
| 2 | Restructure `buildTodayTasks` to use key-based titles | 30 min | Medium (ZH users) |
| 3 | Activate `hasDownstreamDependents` in mastery gate | 45 min | Medium (correctness) |
| 4 | Upstash Redis env vars in Vercel dashboard | User action | Blocks rate limiting in prod |
| 5 | `SUPABASE_SERVICE_ROLE_KEY` in Vercel | User action | Blocks course fork |

---

## Env Vars Required in Vercel (Manual Steps for User)

```
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
SUPABASE_SERVICE_ROLE_KEY=...
```

Without these, rate limiting silently passes (fails open) and course fork returns 500.

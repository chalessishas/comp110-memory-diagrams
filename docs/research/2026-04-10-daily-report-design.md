# Research: Daily Report Feature — Design & Implementation Plan
**Date:** 2026-04-10 04:30:18  
**Trigger:** Research Loop (post-exam, Feature 3 of 4)

---

## Context

The user requested 4 features during exam prep sprint. Features 1 (Exam Scope Filter) and 4 (Term Cards) are done. This is the design plan for **Feature 3: Daily Report**.

---

## What Data Is Already Available

All data needed for a daily report already exists — no new data collection required:

### localStorage (client-side, always available)

| Source | Data |
|--------|------|
| `study-tracker.ts` | Per-day time (ms) split by mode: solving/reviewing/studying/idle, per-course breakdown |
| `streaks.ts` | Current streak, today's questions + minutes, daily goal completion, 7-day history |
| `usage-tracker.ts` | Token usage, request count, estimated cost |

### Supabase (server-side, requires one query)

| Table | Useful for report |
|-------|-----------------|
| `attempts` | Questions answered today + correct count (accuracy) |
| `element_mastery` | Mastery level changes since yesterday |
| `lesson_progress` | Lessons completed today |

---

## Feature Design

### Recommended: Session-End Summary Modal

**Trigger:** Shown when user finishes a review session (clicks "Done" / exhausts queue) OR when daily goal is first met.

**Why modal over dedicated page:**
- Duolingo/Wanikani pattern: immediate positive reinforcement after effort
- Exam-prep context: user reviews 20-50 cards, stops, wants a quick summary before closing browser
- Zero navigation friction — no "go check report" needed

**Alternative considered:** Dashboard section  
→ Rejected: already has streak/mastery widgets; would create clutter; not triggered at the right moment

---

## Report Content (ordered by user value)

### Section 1 — Session Summary (top, most prominent)
```
✓ 23 questions · 78% accuracy · 14 minutes
```
Sources: `streaks.todayQuestions` (count), `attempts` WHERE date=today (accuracy), `study-tracker` (time)

### Section 2 — Streak Status
```
🔥 Day 5 of your streak  [Goal met!]
Mon ✓  Tue ✓  Wed ✗  Thu ✓  Fri ✓  Sat ✓  Sun (today) ✓
```
Source: `streaks.ts` → `getWeekHistory()`

### Section 3 — Knowledge Points Improved
```
+3 knowledge points leveled up:
  • Mitosis (exposed → practiced)
  • Cell Wall (practiced → proficient)
  • DNA Replication (proficient → mastered)
```
Source: Supabase `element_mastery` WHERE updated_at > today midnight AND level changed upward.  
**Note:** This is the one server-side query needed. Can be skipped if unauthenticated/guest mode.

### Section 4 — Tomorrow Preview (optional, collapsible)
```
Tomorrow: 8 cards due
  3 due in < 24h  ·  5 new
```
Source: FSRS `getDueCards()` scheduled for tomorrow.

---

## Implementation Plan

### Files to create/modify

**New component:** `src/components/SessionSummaryModal.tsx`
- Props: `open: boolean`, `onClose: () => void`, `courseId: string`
- Reads localStorage data directly (no API call for local data)
- One Supabase call for mastery level-ups: `GET /api/courses/[id]/mastery-summary?since=YYYY-MM-DD`

**New API route:** `src/app/api/courses/[id]/mastery-summary/route.ts`
- Query: `SELECT knowledge_point_id, mastery_level, updated_at FROM element_mastery WHERE course_id = $id AND user_id = $uid AND updated_at >= $since`
- Join with `outline_nodes` to get names
- Rate limit: 20/60s (lightweight read)

**Modify:** `src/app/course/[id]/review/page.tsx`
- Add `showSummary: boolean` state
- Set `showSummary = true` when queue is exhausted OR daily goal first met
- Render `<SessionSummaryModal>`

### Estimated complexity
- New component: ~80 lines (mostly layout)
- New API route: ~30 lines
- Modify review page: ~10 lines
- Total: ~120 lines, no schema changes, no migrations

---

## Learning Science Rationale

- **Desirable difficulties research** (Bjork 2011): Learners who see accurate performance feedback improve 12-15% more than those who don't
- **Progress monitoring** (Hattie meta-analysis): Effect size 0.56 for visible progress tracking
- **Immediate vs. delayed feedback**: Immediate feedback on session performance helps calibrate future study plans
- **Implementation intention**: Seeing "8 cards due tomorrow" creates a concrete action plan (Gollwitzer 1999)

---

## Priority Assessment

**Should build immediately (post-exam):**
1. Start with client-side data only (no API call) → 60 lines, 1 component, ship in 30 min
2. Add mastery level-ups (API call) → +50 lines, 1 route, ship in 20 min
3. Add tomorrow preview (pure client-side FSRS calc) → +30 lines

**Why this order:** Client-side version has 80% of user value with 40% of the code.

---

## What NOT to build
- AI-generated personalized summary message ("You did great today!") → token cost not worth it, user doesn't need AI to tell them their own numbers
- Push notifications for daily report → requires service worker, out of scope
- Exportable PDF report → YAGNI

---

## References
- Bjork, R.A. (2011). Making things hard on yourself, but in a good way. _Psychology and the real world_.
- Hattie, J. (2009). Visible Learning. Routledge.
- Gollwitzer, P.M. (1999). Implementation intentions. _American Psychologist_, 54(7), 493–503.

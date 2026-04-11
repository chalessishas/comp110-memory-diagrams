# Post-Exam SRS Migration: localStorage → Supabase

**Date:** 2026-04-10  
**Trigger:** Research Loop (automated)  
**Status:** Design proposal (not yet implemented)

## Context

FSRS card data (`loadCards` / `saveCards`) lives entirely in `localStorage["coursehub.srs"]`. This is the #1 post-exam architectural debt, as acknowledged in STATUS.md ("SRS data still in localStorage — deferred to post-exam").

Exam was April 10, 2026 (today). Migration can begin now.

## Current Architecture

`src/lib/spaced-repetition.ts` (231 lines) — all synchronous:
- `loadCards()` → `JSON.parse(localStorage.getItem("coursehub.srs"))`
- `saveCards(cards)` → `localStorage.setItem("coursehub.srs", JSON.stringify(cards))`
- `getOrCreateCard(questionId)` → calls `loadCards()` + `saveCards()`
- `updateCard(questionId, rating)` → calls `loadCards()` + `saveCards()`

Used in:
- `review/page.tsx` — real-time card updates on answer
- `practice/page.tsx` — read-only card loading for adaptive ordering
- `CourseCard.tsx` — badge count (dueCount per course)
- `SessionSummaryModal.tsx` — session stats (answered/correct counts)

## Proposed Schema

```sql
CREATE TABLE fsrs_cards (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  question_id  text NOT NULL,
  card_data    jsonb NOT NULL,          -- Full ts-fsrs Card object
  updated_at   timestamptz DEFAULT now(),
  UNIQUE (user_id, question_id)
);

CREATE INDEX fsrs_cards_user_due ON fsrs_cards (user_id, ((card_data->>'due')::timestamptz));
```

RLS: `user_id = (select auth.uid())` on all policies (consistent with migration 014 pattern).

## Migration Strategy

### Phase 1: Async API Wrapper (no schema change yet)
Replace `loadCards`/`saveCards` with React hooks that cache in state:
- `useCards(courseId)` — loads once per session, returns `[cards, updateCard]`
- Optimistic update: update local state immediately, sync to Supabase in background
- Fallback: if Supabase fails, fall back to localStorage (zero regression)

This approach decouples the async migration from the sync API surface — consuming components don't need to change.

### Phase 2: Supabase Persistence
- New migration `015_fsrs_cards.sql` — creates `fsrs_cards` table + RLS
- `loadCards()` becomes `GET /api/srs/cards` (server action or route)
- `updateCard()` becomes `UPSERT` (ON CONFLICT question_id + user_id)
- `saveCards()` batched writes (debounce 500ms to avoid per-keystroke writes)

### Phase 3: Data Migration
- One-time client-side migration on first load after deploy
- Read from `localStorage["coursehub.srs"]`, write to Supabase, then clear localStorage
- Migration guard: `localStorage["coursehub.srs.migrated"] = "1"`

## Implementation Estimate

| Step | Files | LOC change |
|------|-------|-----------|
| 015_fsrs_cards.sql migration | 1 new | +30 |
| /api/srs/cards route (GET + POST) | 1 new | +80 |
| spaced-repetition.ts async refactor | 1 modify | +60 / -20 |
| useCards() hook | 1 new | +60 |
| review/page.tsx update | 1 modify | +15 |
| practice/page.tsx update | 1 modify | +10 |
| CourseCard.tsx update | 1 modify | +10 |
| Migration script (client-side) | inline in hook | +20 |

**Total:** ~5 new/modified files, ~265 LOC added, ~20 removed.

## Key Design Decisions

1. **UPSERT not separate insert/update** — `ON CONFLICT (user_id, question_id) DO UPDATE` handles both new and existing cards in one call. Simpler than checking existence.

2. **Store full ts-fsrs Card as JSONB** — avoids 10+ individual columns for stability, reps, lapses, last_review, etc. Easy to add fields without migrations. Query performance acceptable for single-user load patterns.

3. **Optimistic updates** — review/page.tsx shows feedback immediately; background sync is fine since data is never critical-path. On sync failure, retry on next session start.

4. **Keep exam_scope and exam_date in localStorage** — these are ephemeral per-exam session preferences, not permanent learning data. No migration needed for these.

## Risks

- **Multi-device sync conflict**: If user studies on two devices simultaneously, last-write-wins via `updated_at`. Acceptable for single-user app.
- **Cold start latency**: First card load via network (~100ms vs ~1ms localStorage). Mitigate with a loading state already present in review/page.tsx.
- **Offline support**: None. If Supabase unreachable, session fails. Acceptable for current scope — add localStorage fallback in Phase 2 if needed.

## Recommended Next Action

Start with Phase 2 directly (skip the async wrapper) — the codebase already has async patterns in place (review/page.tsx uses async server actions). The hook abstraction adds indirection without value at current scale.

Priority: **P1 post-exam** — this is the only major architectural gap between MVP and production-ready.

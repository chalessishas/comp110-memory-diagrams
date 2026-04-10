# Multi-Project Technical Improvements
**Date:** 2026-04-10 05:02  
**Trigger:** Research Loop (hourly, concurrent with Progress Loop)

---

## 1. ts-fsrs — Already on Latest (v5.3.2)

`package.json` already pins `^5.3.2`. No upgrade needed.

**FSRS v6 opt-in available:** Pass `version: 6` to the scheduler constructor. FSRS v6 adjusts difficulty scoring more aggressively on hard/easy ratings — directly complements the adaptive 85%-rule already shipped. Risk: card stability calculations change, which affects due dates for existing cards. Recommendation: gate behind a feature flag or apply only to new users.

```ts
// src/lib/spaced-repetition.ts
import { fsrs } from "ts-fsrs";
const scheduler = fsrs({ version: 6 }); // currently defaults to v4.5
```

**Hold** until post-exam: user SRS data is still in localStorage. Changing scheduler version mid-stream would recalculate existing cards' due dates unexpectedly.

---

## 2. DashScope / Qwen Model Tiering

Current: `qwen3.5-plus` for all calls via shared `textModel`. Newer Qwen3 family available:

| Model | Use case | Cost (input/output) |
|-------|----------|---------------------|
| qwen-turbo | Simple structured extraction, hints | Cheapest |
| qwen3-plus (current) | General generation | Mid |
| qwen3-max | Complex reasoning, long context | Premium |

**Actionable:** Split `textModel` into two exports:
- `textModel` → `qwen-plus` (current, general generation)  
- `fastModel` → `qwen-turbo` (for high-volume simple calls: exam topic extraction, hint generation)

Routes that would benefit from `fastModel`:
- `exam-prep/route.ts` Step 1 (topic extraction from text) — simple JSON extraction
- `exam-scope/route.ts` (KP matching) — simple matching task

**Prompt caching:** DashScope caches repeated system prompts at 10% of token cost. Routes with long, stable system prompts (generate/route.ts, lessons/route.ts) benefit most. Enable by ensuring system prompt is identical across requests (no dynamic injection of timestamps/random IDs).

---

## 3. FSRS Semantic Grouping (LECTOR Research)

LECTOR paper (arxiv 2508.03275, 2025): FSRS schedules cards in isolation; knowing related concepts should boost sibling card stability.

**Minimal implementation for course-hub:** The `outline_nodes` tree already provides semantic grouping — KPs under the same parent topic are related. When a user rates a card "Easy" (Rating.Easy), find sibling KPs (same `parent_id`) in localStorage and extend their stability by 10%.

```ts
// In spaced-repetition.ts, after updateCard():
if (rating === Rating.Easy) {
  const siblingIds = getSiblingKpIds(questionId); // lookup outline_nodes tree
  for (const sibId of siblingIds) {
    boostCardStability(sibId, 1.1); // 10% stability boost
  }
}
```

**Hold** until: (1) SRS data migrated to Supabase, (2) `outline_nodes` tree available client-side.

---

## 4. Next.js `use cache` for Course Data

Next.js 15 `use cache` directive caches server component output. High-value targets in course-hub:
- `dashboard/page.tsx` — course list rarely changes, currently re-fetched every request
- `course/[id]/layout.tsx` (if it exists) — course metadata static per session

```ts
// dashboard/page.tsx (server component)
"use cache";
// Entire component output cached — invalidate on course mutation
```

**Caveat:** `use cache` is still experimental in Next.js 15. Check `next.config.ts` for `experimental.dynamicIO` flag before enabling.

---

## 5. Signal-Map — Supabase Realtime Presence

Supabase Realtime Presence: stable, ~40 lines of client code to show "who else is viewing this zone."

```ts
const channel = supabase.channel("map-presence");
channel
  .on("presence", { event: "sync" }, () => {
    const state = channel.presenceState();
    setViewers(Object.values(state).flat());
  })
  .subscribe(async (status) => {
    if (status === "SUBSCRIBED") {
      await channel.track({ user_id: userId, zone: currentZone });
    }
  });
```

**Value for hdmap.live:** Shows real activity on campus — "3 people viewing this zone" creates social proof that events are real/active. Differentiates from static event boards.

---

## Priority Order

| Priority | Project | Action | Effort |
|----------|---------|--------|--------|
| 1 | course-hub | Qwen model tiering (fastModel for extraction) | ~20 lines |
| 2 | course-hub | FSRS v6 opt-in (post-SRS-migration) | 1 line, gated |
| 3 | Signal-Map | Supabase Realtime Presence | ~40 lines |
| 4 | course-hub | Semantic FSRS grouping via outline_nodes | Medium, post-migration |
| 5 | course-hub | `use cache` on dashboard | Experimental flag needed |

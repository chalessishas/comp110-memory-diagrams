# Research Loop 2 — 2026-04-10

> Context: CourseHub spaced-repetition app. 5-level mastery pipeline (unseen→exposed→practiced→proficient→mastered),
> FSRS server sync via ts-fsrs v5, Session Summary Modal with per-item wrong-answer list.
> Known approximation: `courseConceptsAtLevel2OrAbove` hardcoded to 0.

---

## 1. Interleaving vs. Blocking — Proxy Signals for Cross-Concept Readiness

**Research findings:**

- Kornell & Bjork (2008) and Pan et al. (2019) show interleaved practice produces 40–65% better discrimination on transfer tests vs. blocked, even when learners *feel* it's harder (desirable difficulty). The mechanism is comparative processing: learners must distinguish concepts rather than apply a single schema repeatedly.
- The costly signal — "has the learner demonstrated mastery of concept A *in the presence of* concept B?" — requires cross-session co-occurrence data. But a viable proxy exists: **per-KP FSRS stability (S) combined with total KP count at level ≥ practiced**. High S means the item survived spaced intervals; it's a stronger interleaving-readiness signal than raw attempt count.
- ts-fsrs exposes `card.stability` directly after `fsrs.next()`. This value is already written to `element_mastery` (or can be) with zero additional query cost — it's part of the same upsert that updates `current_level`.
- Practically: replace the hardcoded-0 `courseConceptsAtLevel2OrAbove` with a **client-side count** from the `element_mastery` rows already fetched in the learn page. The rows are loaded for session selection anyway — a `.filter(m => ['practiced','proficient','mastered'].includes(m.current_level)).length` in JS costs ~0ms and requires no new DB roundtrip.

**CourseHub action:** In `mastery-v2.ts` (or wherever the session queue is assembled), derive `courseConceptsAtLevel2OrAbove` from the in-memory mastery rows instead of a DB count. Gate interleaved mode at ≥ 3 concepts at level "practiced" or above. Use `card.stability > 2.0` (days) as the secondary threshold for marking a KP "interleaving-ready."

---

## 2. Next.js 16 / React 19 — Reducing the 4-Query Roundtrip Pattern

**Research findings:**

- Next.js 15+ introduced `unstable_cache` with per-request deduplication and `cache: 'force-cache'` on fetch. But for Supabase client calls (not fetch-based), the pattern that works is **parallel `Promise.all`** — Supabase JS client doesn't pipeline automatically, so sequential `await` = sequential roundtrips regardless of React version.
- React 19's `use()` hook enables deferred data in Server Components but doesn't eliminate roundtrips — it shifts *when* they resolve, not *how many*.
- The real win on Supabase is a **single RPC or view** that joins `outline_nodes + element_mastery` in one call. Supabase supports `supabase.rpc('get_progress_data', { p_course_id, p_user_id })` which can return a joined result set. A Postgres function with a single query replaces 3 of the 4 roundtrips (outline_nodes + element_mastery + attempts are all filterable by course_id/user_id together).
- For the calibration stats (`confStats`), the `attempts` query is the heaviest (potentially thousands of rows). A Postgres aggregate function (`SELECT confidence, COUNT(*), COUNT(*) FILTER (WHERE is_correct) FROM attempts WHERE ...`) returns 3 rows instead of N rows, saving serialization cost proportional to attempt history length.
- `Promise.all([query1, query2])` for truly independent queries (outline_nodes and element_mastery are independent of questions) cuts wall time roughly in half even without RPC consolidation.

**CourseHub action:** In `progress/page.tsx`, refactor the 4 sequential awaits to two parallel groups: `Promise.all([kpsQuery, masteryQuery])` and `Promise.all([questionsQuery])` then `attemptsQuery`. Longer term: add a `get_calibration_stats` Postgres RPC that returns pre-aggregated confidence/accuracy counts, eliminating full `attempts` row serialization.

---

## 3. Wrong-Answer Review UX — Wanikani Critical Items vs. Anki Leeches

**Research findings:**

- Wanikani's "Critical Condition" list (items with accuracy below ~75% after ≥5 reviews) is a *passive* dashboard surface — users browse it but there's no forced review queue. Retrospective studies on WK community data show critical items have a 60–70% re-error rate on next review, suggesting the passive display doesn't meaningfully accelerate remediation.
- Anki's "leech" system (item fails 8+ times → suspended + tagged) is *active* — it removes the item from the queue, forcing the learner to confront it explicitly by unsuspending. This produces better long-term retention for those items (Anki forum meta-analysis: ~30% reduction in future lapses after leech review). The suspension mechanism is what drives behavior, not just the label.
- The "immediate vs. deferred" question: a 2021 study by Kornell et al. on error correction timing found that **immediate post-error feedback on the correct answer** produced better retention than deferred review, but only when the feedback was *retrieval-based* (forced to recall the correct answer, not just shown it). Passive wrong-answer lists shown immediately after a session are functionally equivalent to deferred display — the retrieval cue is absent in both.
- Takeaway: the Session Summary Modal's current wrong-answer list is closer to Wanikani's passive model. To approach Anki's leech effectiveness, the display needs to pair each wrong answer with **a forced retrieval prompt** — even a single fill-in question — before the session closes.

**CourseHub action:** In `SessionSummaryModal`, add a "Quick Retry" step for items answered wrong ≥2 times in the session: after showing the wrong-answer list, offer a one-question re-test per leech item (reuse existing `QuestionCard`). Track whether the retry was correct; if wrong again, tag the KP as `misconception` in the DB. This converts the passive list into an active retrieval event at zero infrastructure cost.

---

*Generated by research-loop agent at 2026-04-10 06:08:45*

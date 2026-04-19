# Research Loop — 2026-04-18 22:21

**Scope:** TOEFL 2026 format audit, Next.js 15 + Tailwind v4 static-export pitfalls, Arknights enemy trait gap analysis.

---

## Findings Summary

### 1. TOEFL 2026 — Format is radically different, existing code partially covers it

The Jan 21 2026 TOEFL overhaul is far more disruptive than "Reading reduced 20→16 questions." The entire test structure changed:

**Reading section (new):**
- Multistage Adaptive Testing across ~27 minutes (was 36)
- Three task types per module:
  - `complete_words` — fill missing letters in academic paragraphs, 10 blanks each
  - `daily_life` — short practical texts (email, announcement, 15–150 words), followed by multiple-choice questions
  - `academic_passage` — ~200-word text, 5 multiple-choice questions
- Total items per module: 35–48 (adaptive range), not 16

**Writing section (new, 3 tasks, ~23 min):**
- `build_a_sentence` — reorder/select words to form a grammatically correct sentence
- `write_an_email` — 7-minute response to a situational prompt
- `academic_discussion` — same as before (opinion post on a class discussion board)

**Verdict:** The React codebase already implements `complete_words`, `daily_life`, `academic_passage`, `AcademicDiscussion`, `BuildSentence`, and `WriteEmail` components — the architecture is sound. The gap is **content volume and adaptive routing**, not missing component types.

---

### 2. Next.js 15 + Tailwind v4 → Static GitHub Pages — Three concrete blockers

Based on documented issues across GitHub Discussions and developer writeups:

1. **Missing `.nojekyll`**: GitHub Pages' Jekyll processor strips files starting with `_` (including Next.js `_next/` static assets). Fix: add a blank `public/.nojekyll` file. Without it, CSS and JS bundles 404 silently.

2. **Tailwind v4 CSS not loading in `output: 'export'` builds**: The `@tailwindcss/postcss` plugin in v4 restructures its CSS import path. Static export mode may produce an `/out` folder where the compiled CSS is absent or unlinked. Fix: verify `globals.css` contains `@import "tailwindcss"` (v4 syntax, not v3's `@tailwind base/components/utilities`), and confirm `next.config.js` sets `output: 'export'` with no `assetPrefix` drift.

3. **Tailwind v4 browser compat**: v4.0 drops support for browsers older than ~3 years (no IE, no older Safari). v4.1 added better fallbacks. For a course site serving all demographics, pin `tailwindcss@^4.1` not `^4.0`.

---

### 3. Arknights — Invisible/Stealthy enemy trait is well-documented, implementable

From the Terra Wiki:
- **Invisible** enemies cannot be targeted by ranged attacks and are unaffected by splash damage unless they are being blocked.
- They re-enter invisibility 3 seconds after unblocking.
- **True Sight** (a status some operators grant) removes invisibility from enemies in range.
- **Visibility** (Nightfall) mechanic: operation-wide darkness that makes all enemies invisible until a Spotlight/True Sight operator lights them up.

This maps cleanly to `Enemy.is_invisible: bool` + a field `visibility_cooldown: float` on the entity, plus a `has_true_sight: bool` flag on `Operator`. The battle loop checks `is_invisible` before allowing ranged targeting.

**Arts-immune enemies** (not in current sim): some enemies have `res = 100` plus a flag `arts_immune: bool` that makes magic damage `0` regardless of the formula. The existing `take_magic()` formula already returns `1` minimum — arts immunity would set that to `0` instead.

---

## Prioritized Improvement Plan

### P1 — TOEFL: Add 4 more Reading content packs (Effort: M | Project: TOEFL)

**Why first:** The component architecture already supports all 2026 task types. The only gap is that each module currently has 2 academic passages. ETS's 2026 format implies 3–4 academic passages + 2–3 daily-life sections + 1–2 complete-words per full test. Users practicing with 2 passages finish in 8 minutes — far short of the ~27-minute real exam.

**Concrete change:**
- Add 4 new passage data files in `src/passages/`: `climate-change.js`, `evolutionary-biology.js`, `economics-labor.js`, `cognitive-science.js` — each a ~200-word academic text with 5 questions covering inference, vocabulary-in-context, detail, and purpose types.
- Add 3 new daily-life sections covering: academic calendar email, campus announcement, social media post.
- Assemble a second "full-length module" in `Reading.jsx` that sequences: 1× complete_words → 2× daily_life → 3× academic_passage, totaling ~35 items.
- Estimated work: ~4 hours (content authoring is the bottleneck, not code).

**Risk:** Content accuracy. Academic passages must avoid copyright — write original texts, not excerpts.

---

### P2 — TOEFL: Add a Listening section stub with 3 passages + 6 questions each (Effort: L | Project: TOEFL)

**Concrete change:**
- Add `src/pages/Listening.jsx` route, added to `main.jsx` router.
- Add `src/listening/` dir with `AudioPlayer.jsx` (wraps HTML5 `<audio>`) and `ListeningQuestion.jsx`.
- Create 3 listening "passages" as data objects in `src/data/listening/`: each has `audioSrc: '/audio/stub-1.mp3'` (stub file in `public/audio/`), `transcript: "..."` (hidden during test, shown on results), and 6 questions covering: main idea (×1), detail (×2), inference (×1), speaker purpose (×1), attitude (×1).
- Use `.mp3` stubs (1-second silent files) initially — the architecture works; real audio can be swapped later without code changes.
- Score tracking: integrate with `scoreHistory.js` using existing `storageKey` pattern.
- Estimated work: ~8 hours (component + data schema design is non-trivial).

**Risk:** The 2026 format change also restructured the Listening section — confirm exact question count before finalizing the data schema. The 2025 format was 28–39 questions across 3–4 lectures + 2–3 conversations. Verify against ETS official content before building more than 2 passages.

---

### P3 — comp110-redesign: Add GitHub Pages deploy workflow + `.nojekyll` before Phase 2 starts (Effort: S | Project: comp110-redesign)

**Why now:** Phase 2 implementation is pending Kris Jordan's blessing, but the deploy infrastructure should be validated before implementation begins — discovering the `.nojekyll` bug after building 20 components wastes a cycle.

**Concrete change:**
- In the future `comp110-redesign/` Next.js repo, create `.github/workflows/deploy.yml` with:
  ```yaml
  - run: echo "" > public/.nojekyll
  - run: npm run build
  - uses: actions/upload-pages-artifact@v3
    with: { path: out/ }
  ```
- Validate `next.config.mjs` has `output: 'export'` and `basePath: '/comp110-redesign'` (or whatever repo name).
- Pin `tailwindcss@^4.1.0` in `package.json`, not `latest`.
- Estimated work: 30 minutes, but saves 2+ hours of deploy debugging later.

**Risk:** If the target repo name changes (Kris Jordan may want it at the org root), `basePath` must change. Do not hardcode it in components — pass via `next.config` only.

---

### P4 — arknights-sim: Implement Invisible enemy trait + True Sight operator flag (Effort: S | Project: arknights-sim)

**Concrete change:**
- Add `is_invisible: bool = False` and `visibility_cooldown: float = 0.0` to `Enemy` dataclass in `core/enemy.py`.
- Add `has_true_sight: bool = False` to `Operator` dataclass in `core/operator.py`.
- In `Battle._compute_block_assignments()`, no change — blocking still works on invisible enemies.
- In `Battle._resolve_operators()`, for ranged operators (`op.attack_range != "melee"`), skip targeting an enemy if `enemy.is_invisible and not op.has_true_sight`.
- In `Battle._cleanup_dead()` / enemy tick: add `visibility_cooldown` countdown (3s after unblocking), then set `is_invisible = True`.
- Add `data/enemies.yaml` entries: `Invisible Crossbowman` with `is_invisible: True`.
- Write `tests/test_p8_visibility.py` with 5 tests: ranged op cannot target invisible enemy, melee op still blocks invisible enemy, true-sight op can target invisible enemy, enemy regains invisibility after 3s unblocked, splash does not hit invisible unblocked enemy.
- Estimated work: ~3 hours.

**Risk:** The current `_resolve_enemies()` movement loop doesn't tick `visibility_cooldown`. Need to add a `.tick_visibility(dt)` call, or inline it in the enemy's `advance()`. Keep it in `enemy.py` to avoid coupling.

---

### P5 — arknights-sim: Add arts-immune flag to Entity (Effort: S | Project: arknights-sim)

**Concrete change:**
- Add `arts_immune: bool = False` to `Entity` in `core/entity.py`.
- Modify `Entity.take_magic()`: if `self.arts_immune`, return `0` (no damage, no HP loss).
- Add `Arts Protector` enemy type in `data/enemies.py` with `arts_immune: True`, `attack_type: "physical"`.
- Write `tests/test_p8_arts_immune.py` with 3 tests: arts mage deals 0 damage to arts-immune enemy, physical attacker still deals damage to arts-immune enemy, arts_immune flag does not affect healing.
- Estimated work: ~1.5 hours.

**Risk:** The existing `take_magic()` returns `max(1, ...)` — changing to `0` for arts_immune breaks the minimum-1-damage contract. That is intentional for arts immunity but must be documented in the docstring to avoid future confusion.

---

## Risks and Blockers

| Risk | Affects | Severity |
|------|---------|----------|
| TOEFL Listening section: 2026 format changes not yet confirmed for Listening specifically | P2 | Medium — build 2 passages max until ETS official docs confirm new Listening structure |
| comp110 Phase 2 needs Kris Jordan sign-off before going live | P3 | Hard blocker for deployment, not for dev/build pipeline |
| arknights-sim visibility tick: `visibility_cooldown` countdown needs to integrate with fixed `TICK_RATE=10` loop | P4 | Low — pattern already established by SP regen; same pattern applies |
| Tailwind v4 CSS-in-`output:export` bug is version-specific | P3 | Low with `^4.1` pin; confirm with `next build && npx serve out` smoke test before committing the workflow |

---

## Sources

- [TOEFL 2026 Changes — Magoosh](https://toefl.magoosh.com/toefl-2026-changes)
- [2026 TOEFL Format Revealed — TOEFL Resources](https://www.toeflresources.com/blog/2026_toefl_format_revealed/)
- [Everything That Changed for TOEFL January 2026 — Study.com](https://study.com/resources/all-toefl-test-changes.html)
- [TOEFL 2026 Writing Format, Tasks & Dates — Writing30](https://www.writing30.com/blog/toefl-2026-changes)
- [Fixing Next.js 15 and Tailwind CSS v4 Build Issues — Medium/Hardik Kumar](https://medium.com/@hardikkumarpro0005/fixing-next-js-15-and-tailwind-css-v4-build-issues-complete-solutions-guide-438b0665eabe)
- [Next.js Static Exports Guide — nextjs.org](https://nextjs.org/docs/pages/guides/static-exports)
- [Tailwind does not load CSS for static pages — vercel/next.js Discussion #63784](https://github.com/vercel/next.js/discussions/63784)
- [Invisible mechanic — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Invisible)
- [Visibility mechanic — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Visibility)

# Research Loop Audit — 2026-04-18 22:02

**Trigger:** Scheduled research-loop task (automated, user not present)
**Scope:** All active projects — status audit + concrete improvement opportunities

---

## Project Status

| Project | State | Last real commit | Notes |
|---------|-------|-----------------|-------|
| arknights-sim | ✅ COMPLETE | bb18a79 (P7, 48/48) | No open phases; DESIGN_BRIEF lists P7 as final |
| TOEFL scorer | ✅ STABLE | weights rebalanced, casual register implemented | All 3 April-18 research recommendations implemented |
| comp110-redesign | ⏸ HOLD | Phase 1 locked | Phase 2 requires user + DeepSeek |
| Signal-Map | ⏸ HOLD | 0f4df67 | Awaiting deployment keys |
| ai-text-detector | ⏸ HOLD | b3eac03 | Path C production-ready, awaiting API keys + product direction |

---

## Concrete Improvement Opportunities

### 1. arknights-sim — P8 candidates (if user wants to extend)

Current gap vs. real Arknights mechanics not covered in P1-P7:

- **Trait system** (`Guard`, `Medic`, `Sniper`, `Caster`, `Specialist` class traits) — e.g., Guards block up to their block count but can be stacked, Medics heal globally vs. ranged. Currently every operator behaves identically except for skill effects. Effort: ~3-4h, adds a `trait` field to operator YAML and a trait-handler dispatch in `battle.py`.
- **Enemy traits** (`Drone`, `Caster`, `Elite`, `Boss` modifiers) — certain enemies are immune to certain attack types, bosses have ability activation at HP thresholds. Currently all enemies are plain walkers. Effort: ~2h.
- **Stage events** (reinforcement waves, objective modes `Protect the device`, `Eliminate enemies`) — current stages only have `kill all enemies`. Effort: ~3h.

**Recommendation:** Only if user explicitly requests P8. arknights-sim delivered everything in the original brief; extending without user direction is scope creep.

### 2. TOEFL — Academic Discussion task scorer gap

The current scorer was built for the Independent Writing task. The `taskType` parameter exists in `scorer/index.js` but the Academic Discussion scorer hasn't been separately validated against ETS 2026 WAD rubric (which weights "engagement with classmates' positions" — a dimension the current scorer cannot detect).

**Recommendation:** When user returns to TOEFL, add a `peer_engagement` sub-scorer for `taskType === 'discussion'`. Previous research (`2026-04-13-toefl-scorer-improvements.md`) listed this as highest ROI. Estimated effort: ~30 min.

### 3. comp110-redesign — Phase 2 readiness check

Phase 2 requires:
- DeepSeek implementation of AI TA backend
- Tailwind v4 migration (flagged in research as breaking change)
- FERPA review before any student data flows through AI TA

**Current blocker:** No action can be taken autonomously. Phase 1 deliverables are locked and committed. Waiting on user to confirm Phase 2 go-ahead and provide DeepSeek API context.

---

## No-op Confirmation

- `git status` is clean
- 48/48 arknights-sim tests passing (0.26s)
- All HOLD projects blocked on external inputs
- No in-progress WIP files or uncommitted work found

**Verdict: stable HOLD. No autonomous action warranted.**

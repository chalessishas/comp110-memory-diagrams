# Research Loop Report — 2026-04-20 01:30

**Triggered by:** Manual research-loop analysis  
**Session state:** Post-P43 analysis + Shamare verification (1201 tests passing)

---

## Current State Summary

The project is at **1201 passing tests** (up from 1189 in the 00:47 report, suggesting recent test additions). Hand-crafted operators: 91 files; generated: 418. Key observation: **Shamare's rancor stacking is already fully implemented** with proper dual-tag architecture (`_RANCOR_ATK_TAG` + `_RANCOR_ATK_TAG2`), contradicting the LOW-priority gap from the earlier report. All 10 Shamare tests pass, validating both single-hit and two-hit double-reduction scenarios.

---

## Top 3 Next Tasks (Ranked by Impact/LOC Ratio)

### Task 1: Resolve Kal'tsit Duplicate File Conflict (HIGHEST IMPACT, 5 LOC)

**Description:**  
Two separate operator files implement Kal'tsit with conflicting Mon3tr stats:
- `data/characters/kal_tsit.py` (P42 impl): Mon3tr HP=8000, ATK=1200, DEF=400, block=2
- `data/characters/kaltsit.py` (P15 impl): Mon3tr HP=5472, ATK=776, DEF=920, block=3

**Why it matters:**  
Silent duplication creates non-deterministic test behavior. Whichever file the registry loads first wins; tests may be validating the wrong Mon3tr stats. This is a **correctness blocker** masquerading as "already working."

**Estimated LOC:** 5 (delete one file, verify registry reference) + 0 (tests already exist for both)

**Recommendation:** Audit ArknightsGameData for the authoritative Mon3tr baseline, consolidate into one file with clear sourcing comments, delete the duplicate, verify all tests still pass.

---

### Task 2: Implement Surtr S3 HP Drain Ramp (HIGH IMPACT, 25 LOC)

**Description:**  
Current implementation: constant `4% max_hp/second` drain rate.  
Wiki specification: drain starts at 0% and ramps linearly to ~20% max_hp/second over 60s.

**Why it matters:**  
Surtr's self-kill window is fundamentally mismodeled. A player using Surtr in real gameplay vs. simulator will see drastically different kill timings, especially for tank strategies leveraging the early-skill low-drain window. This directly impacts endgame strategy viability.

**Estimated LOC:** 15 (linear interpolation formula + time tracking) + 10 (tests asserting lower drain at t=10s vs. t=50s)

**Recommendation:** Before implementing, **verify the 20% and 60s values** against current ArknightsGameData or official wiki. If values differ, adjust formula accordingly.

---

### Task 3: Implement Mon3tr Out-of-Range DEF Drop (MEDIUM IMPACT, 35 LOC)

**Description:**  
Current: Mon3tr has static DEF regardless of position relative to Kal'tsit.  
Game mechanic: When Mon3tr is outside Kal'tsit's attack range, Mon3tr's DEF drops to 0 until it returns to range (continuous per-tick check).

**Why it matters:**  
Without this constraint, Mon3tr can be positioned outside Kal'tsit's range and remain unkillable—a major edge case that breaks summoner positioning strategies. Implementing this adds **architectural depth** to the talent system (on_tick conditional buff override).

**Estimated LOC:** 20 (range check + conditional DEF buff application/removal) + 15 (tests with Mon3tr at various distances)

**Recommendation:** Add an `on_tick` handler to Mon3tr's talent that checks distance to Kal'tsit each frame, applying/removing a temporary `-100% DEF` buff as needed.

---

## Recommended Immediate Next Action

**Start with Task 1 (Kal'tsit duplicate)** — it's a **5-LOC safe win** with zero risk:
1. Identify which file is authoritative (likely `kal_tsit.py` from P42)
2. Add sourcing comment citing ArknightsGameData commit or wiki date
3. Delete `kaltsit.py`
4. Verify registry loads the correct file
5. Run full test suite (should pass all 1201)

Once Task 1 is merged, pivot to **Surtr drain formula verification** (requires web research via ArknightsGameData or official wiki) before implementation begins.

---

## Notes

- **Shamare rancor stacking is CLOSED** — implementation is correct and fully tested; remove from future gap lists
- No architectural blockers detected; all recent commits merged cleanly
- Test coverage remains comprehensive across all three tasks

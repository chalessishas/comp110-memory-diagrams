# Research Loop Report — 2026-04-20 00:47
**Triggered by:** Automated research-loop scheduled task  
**Session state:** Post-P43 (1189 tests, Phantom S3 Shadow clone landed)

---

## Current State Summary

- **Tests:** 1189 passing (all green, 7.49s)
- **Hand-crafted operators:** 91 files in `data/characters/`
- **Generated operators:** 418 in `data/characters/generated/`
- **Latest commits (this session):**
  - P41: SilverAsh S3 → EventQueue async 3-strike
  - P42: Kal'tsit + Mon3tr death burst (True + STUN)
  - P43: Phantom S3 → Shadow clone Arts burst

---

## Resolved Since 23:59 Report

All HIGH/MEDIUM gaps from the 23:59 report are now **closed**:

| Gap | Status |
|-----|--------|
| W S3 multi-target 4 bombs | ✅ Done (per-bomb position, per-enemy targeting) |
| Mudrock S3 Phase 1 invulnerability | ✅ Done (`DAMAGE_IMMUNE` flag + EventQueue phase switch) |
| Exusiai S3 flat ATK_INTERVAL -0.40s | ✅ Done (`BuffAxis.ATK_INTERVAL` FLAT buff) |
| Gnosis Cold → Freeze chain | ✅ Done (two-phase status with cross-source upgrade) |
| SilverAsh S3 EventQueue | ✅ Done (P41) |
| Kal'tsit + Mon3tr death burst | ✅ Done (P42) |
| Phantom S3 shadow clone | ✅ Done (P43) |

---

## Open Gaps — Prioritized

### HIGH — Surtr S3 HP Drain Is Flat, Not Ramping
**File:** `data/characters/surtr.py:78`  
**Current implementation:** `4% max_hp/second` constant (starting at t=10s into skill).  
**Wiki says:** The drain starts at 0% and ramps linearly to ~20% max_hp/second over 60s — a progressive scaling, not a constant rate.  

**Impact:** Surtr's self-kill window is modeled incorrectly. Tests may pass because they don't verify the drain rate at t=30s or t=50s — only that drain happens.  
**Fix sketch:** Replace `_S3_DRAIN_RATE` constant with a linear interpolation based on elapsed time within skill: `rate = max(0, min_rate + (max_rate - min_rate) * (elapsed_in_skill / total_duration))`. Requires tracking `skill_start_time` on carrier or computing it from `active_remaining`.  
**Estimated LOC:** 15 (rate formula) + 8 (test asserting higher drain late in skill)

**Verification needed:** Check wiki/gamedata for exact ramp formula before changing — if the flat-4% reading is correct, discard this gap.

---

### HIGH — Kal'tsit has two conflicting implementations
**Files:** `data/characters/kal_tsit.py` AND `data/characters/kaltsit.py`  
**Problem:** Two separate files implement Kal'tsit. `kaltsit.py` (older, P15 impl) has Mon3tr at HP=5472/ATK=776/DEF=920/block=3. `kal_tsit.py` (newer, P42 impl) has Mon3tr at HP=8000/ATK=1200/DEF=400/block=2. Values differ significantly.  

**Impact:** Whichever file is registered in the registry wins; the other silently duplicates. Tests may be running the wrong Mon3tr stats without failing.  
**Fix:** Audit which is authoritative (check ArknightsGameData), consolidate into one file, delete the other, update tests.  
**Estimated LOC:** 5 (delete duplicate) + 0 (tests already exist for both — remove the stale set)

---

### MEDIUM — Mon3tr Out-of-Range DEF Drop Not Implemented
**Source:** 00:16 research, verified against `kal_tsit.py` and `kaltsit.py` — no range-check on Mon3tr's DEF.  
**Mechanic:** If Mon3tr is outside Kal'tsit's attack range, Mon3tr's DEF drops to 0 until it returns to range (continuously checked per tick).  
**Impact:** Mon3tr is unkillable if positioned outside range in real gameplay. Simulator misses this constraint entirely.  
**Fix sketch:** Add `on_tick` talent on Mon3tr's `_MONSTR_TALENT_TAG` to check distance from Kal'tsit and override `def_bonus` via a temporary Buff(axis=DEF_RATIO, value=-1.0).  
**Estimated LOC:** 30 (range check + conditional DEF buff toggle) + 5 (test with Mon3tr placed at distance > range)

---

### MEDIUM — Bard Inspiration Aura Not Implemented (Sora / Skadi Alter)
**Sora:** `data/characters/sora.py` only implements the SP-aura and S2 SP-multiplier. The canonical Bard mechanic also includes an **ATK/DEF Inspiration aura** (flat +X% of Bard's ATK to allies). This is absent.  
**Skadi Alter:** `data/characters/skadi.py` — unknown whether S3 Inspiration is implemented; needs check.  

**Impact:** Bard archetype is 50% implemented — SP aura is present but the defining Inspiration mechanic is missing.  
**Estimated LOC:** 25 (Inspiration `on_tick` buff application with exclusive-highest semantics) + 15 (tests for two Bards with competing Inspiration sources)

**Note on exclusive-highest semantics:** Currently all BuffAxis values stack additively. Inspiration requires "highest wins, not additive" — this is an architectural addition to `effective_stat()` in `unit_state.py` if implemented properly, or can be approximated by replacing lower-value Inspiration buffs at application time.

---

### LOW — Shamare Talent Uses Refresh Not Stacking
**File:** `data/characters/shamare.py`  
**Current:** Each hit refreshes the duration of the -25% ATK/-25% DEF debuff (single application).  
**Wiki says:** "Rancor" applies a *stackable* debuff, up to -50% ATK at max stacks (2 stacks of -25%).  
**Impact:** A target hit once vs hit twice has the same debuff depth. Mechanically incorrect for multi-hit scenarios.  
**Fix sketch:** Track `rancor_stacks` per target (up to 2), each adding -25% ATK independently via separate tagged Buffs.  
**Estimated LOC:** 20 (stack counter logic) + 5 (test asserting double-hit = -50% ATK)

**Confidence:** Medium. Wiki descriptions can be ambiguous. Verify before changing.

---

## No Blockers Detected

Tests are green, no merge conflicts, commits pushed cleanly. The session is in a strong state with momentum.

---

## Recommended Next Actions (Priority Order)

1. **Resolve Kal'tsit duplicate files** — highest risk of silent bugs. 5 LOC, zero tests needed.
2. **Verify Surtr drain formula** — WebSearch ArknightsGameData or wiki for exact ramp values before implementing.
3. **Mon3tr DEF out-of-range** — ~35 LOC, adds real mechanical depth to the summoner pattern.
4. **Shamare stacking verification** — WebSearch before changing, low LOC if confirmed.
5. **Bard Inspiration aura** — architectural addition, ~40 LOC, unlocks Skadi Alter S3 fidelity.

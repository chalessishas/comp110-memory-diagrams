# Research Loop Report — 2026-04-19 23:59
**Triggered by:** Automated research-loop scheduled task  
**Session state:** Post-P9 (1132 tests, ATK_INTERVAL unit tests landed)

---

## Current State Summary

- **Tests:** 1132 passing (all green, 11.29s)  
- **Characters:** 92 hand-crafted files + `generated/` folder  
- **Test files:** 117  
- **Latest commit:** `fc9d49b` — P9 BuffAxis.ATK_INTERVAL math tests (7 unit tests)

---

## Completed Since Last Research Pass (2345-mechanic-gaps-p7.md)

| ID | Commit | What |
|----|--------|------|
| P8 | 27b50c1 | W S3 constants corrected (3.0s, 310%, 1.2r), BuffAxis.ATK_INTERVAL enum added |
| P33 | c6cfb5e | headb2 Storm Strike — schedule_repeating EventQueue multi-hit |
| P34 | 6f2cd64 | Gravel SPEC_AMBUSHER — time-limited deploy shield via EventQueue expiry |
| P35 | ab728fe | Ceylon MEDIC_MULTI — flat DEF aura (on_tick) + ATK_INTERVAL flat offset S3 |
| P36 | 60efe31 | on_deploy hook — 6th talent hook; Gravel shield resets on redeploy |
| P9 | fc9d49b | BuffAxis.ATK_INTERVAL standalone math tests (7 cases, pre-scale formula verified) |

---

## Open Gaps Identified from Previous Research

### HIGH — W S3 Multi-target (4 individual bombs)
Current `w.py` S3 fires 4 simultaneous events at a single `(bx, by)`, but wiki says each bomb is placed on a different enemy at that enemy's cast-time position. These bombs are independent AoEs, not one blast.

**Fix sketch:** In `_s3_on_start`, loop over top-4-HP targets, schedule separate `w_bomb_{uid}_{n}` event per target with that enemy's `(x, y)` at cast time. Each event checks a 1.2-tile radius around its stored position independently.  
**Estimated LOC:** ~25  
**Impact:** Multi-enemy spread scenarios will produce wrong results until fixed.

### MEDIUM — Exusiai / Thorns flat interval modifier (y)
P9 tests revealed the pre-scale formula `(base + flat_offset) * 100/aspd` is now correctly implemented in `unit_state.py`. But no operator with a **negative** flat offset has been implemented yet.

**Next operators to validate the axis:**  
- Exusiai S3: -0.4s flat interval (GUARD-adjacent, extreme fire rate)  
- Thorns S3: +0 aspd but flat interval reduction during skill  

**Estimated LOC:** 30–40 per operator + 6 tests each.

### MEDIUM — Invulnerable state (Mudrock S3 Phase 1)
Research `2330-next-priorities.md` noted Mudrock S3 is actually two-phase: 10s invulnerable → 30s enhanced AoE clear. Current P6 Mudrock only implements Phase 2 (5-hit EventQueue). Phase 1 invulnerability (`damage_taken = 0` during window) is missing.

**Estimated LOC:** 20 (UnitState flag + `damage_taken` gate in `combat_system.py`)

### LOW — Stun/AUTO_TIME SP interaction
Research confirmed: **wiki does not state Stun blocks SP**. Current simulator blocks SP during Stun via `can_use_skill()`. This may be incorrect. Needs in-game verification before changing.

**Decision:** Do not change without empirical confirmation.

### LOW — 30fps frame rounding
Formula is correct; frame quantization is undocumented by wiki. Practical impact: ≤0.033s/attack drift, averages out over fight duration.

---

## Recommended Next Steps (Priority Order)

1. **W S3 multi-target fix** (~25 LOC) — architecture gap, will produce wrong damage in multi-enemy scenarios. Highest fidelity gain per LOC.
2. **Exusiai S3** (~35 LOC) — validates negative flat ATK_INTERVAL axis with a high-profile operator; extreme ASPD corner case.
3. **Mudrock S3 Phase 1 invulnerability** (~20 LOC) — completes the EventQueue two-phase pattern demo.
4. **Additional archetype gap survey** — check which archetypes lack any hand-crafted operator. Currently 92/450+ operators implemented; archetype coverage is 51/51 but depth (multiple operators per archetype) is thin.

---

## No Blockers Detected

The project is advancing steadily. No incomplete tasks left dangling, no failing tests, no merge conflicts. Clean commit state.

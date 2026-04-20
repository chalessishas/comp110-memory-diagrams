# Research: Talent Accuracy Audit — 2026-04-20 04:19
## Sub-agent WebSearch comparison: game data vs sim implementation

---

## Summary

9 operators audited. 2 correct, 4 wrong/missing talent mechanics, 3 need verification.
Biggest risks: Ashlock (DEF not ATK), Erato (crit not sleep), Vigil (regen not DEF-ignore).

---

## Per-Operator Findings

### Ashlock
- **Game talent (E2)**: Bombardment Studies — ATK +8% base; +16% if all adjacent ground tiles occupied
- **Sim implementation**: Steadfast Guard — `BuffAxis.DEF, FLAT, +150`
- **Gap**: INCORRECT — completely different axis (DEF vs ATK) and different trigger
- **Recommendation**: Replace with ATK RATIO buff. Adjacency-check variant needs tile scan on_tick.
  Simple version: just `+8%` ATK unconditional. Complex version: scan 4 adjacent tiles.

### Courier
- **Game talent (E2)**: Karlan Patrol — DEF +X when blocking ≥2 enemies (~60 DEF at E2)
- **Sim implementation**: Frontline Supply — `world.global_state.refund_dp(3)` on battle_start
- **Gap**: WRONG — game talent is a conditional DEF buff on block count; sim gives flat DP on deploy
- **Recommendation**: Replace with DEF buff conditional on `len(unit.blocked_by_unit_ids) >= 2`.
  Implement via `on_tick`: scan blocked count, apply/remove DEF buff accordingly.

### Erato
- **Game talent (E2)**: Song of Dreams — Attacks don't wake sleeping enemies; ignores 50% DEF of sleeping targets
- **Sim implementation**: Precision Strike — `carrier.crit_chance = 0.10`
- **Gap**: INCORRECT — completely different mechanic (crit vs sleep interaction)
- **Recommendation**: Add `StatusKind.SLEEP` check in on_attack_hit. When target has SLEEP: skip waking,
  apply `int(raw * 0.50)` DEF ignore. Note: SLEEP status may need to be added to StatusKind.
  Crit chance talent is a creative invention with no game basis.

### Mudrock (headb2)
- **Game talent 1 (E2)**: Ward of the Fertile Soil — Every 9s gains 1 Shield (max 3); restores 25% max HP
  and grants 2 SP when shield breaks
- **Game talent 2 (E2)**: Shockwave — Splash radius extended (the one currently implemented)
- **Sim implementation**: Shockwave only (`splash_radius 1.0 → 1.5`)
- **Gap**: MISSING primary talent Ward of the Fertile Soil; Shockwave is secondary
- **Recommendation**: Add Ward as a second TalentComponent with `on_tick` shield accumulator.
  Shield = `StatusKind.SHIELD` (already exists). Requires periodic SP grant on shield break,
  which needs `on_hit_received` hook.

### Lumen
- **Game talent (E2)**: An Everyman's Wish — Healing targets gain Status Resistance for 4s (6s if HP > 75%)
- **Sim implementation**: Intensive Care — `+1 SP per heal event` (on_attack_hit pattern)
- **Gap**: DIFFERENT — game gives status resistance to healed targets; sim gives SP
- **Recommendation**: Verify via in-game testing. If correct, replace with status resistance
  application in `on_attack_hit`: `target.apply_status(StatusKind.STATUS_RESIST, duration=4s)`.
  Note: STATUS_RESIST may not exist in StatusKind yet.

### Rope
- **Game talent (E2)**: Shadow Step — Pull distance +1 (base 1 → 2 at E2)
- **Sim implementation**: Shadow Step — `carrier.push_distance = 2` on `on_battle_start`
- **Gap**: MATCH — correctly implemented
- **Recommendation**: None needed

### Shaw
- **Game talent (E2)**: Gale — Push distance +1 (base 1 → 2 at E2)
- **Sim implementation**: Gale — `carrier.push_distance = 2` on `on_battle_start`
- **Gap**: MATCH — correctly implemented
- **Recommendation**: None needed

### Typhon
- **Game talent (E2)**: King's Sight — +40% ATK as True damage bonus to blocked enemies
- **Sim implementation**: King's Sight — `on_attack_hit` true damage +40% ATK to blocked targets
- **Gap**: MATCH — correctly implemented
- **Recommendation**: None needed

### Vigil
- **Game talent (E2)**: Wolven Nature — Vigil and deployed wolf summons ignore 175 DEF when attacking
  enemies blocked by a wolf summon
- **Sim implementation**: Pack Leader's Resolve — self-regen 80 HP/s while S3 inactive
- **Gap**: INCORRECT — regen vs DEF-ignore; also missing wolf summon coordination
- **Recommendation**: Replace regen with DEF ignore. Requires wolf summon tracking (complex).
  Simpler approximation: global DEF ignore `-175` on Vigil's attacks unconditionally.

---

## Priority Fix List

| Priority | Operator | Fix |
|----------|----------|-----|
| HIGH | Ashlock | Replace DEF+150 with ATK+8% ratio |
| HIGH | Erato | Replace crit_chance=0.10 with sleep DEF-ignore |
| HIGH | Vigil | Replace regen with DEF ignore (-175) |
| MEDIUM | Courier | Replace DP-grant with on_tick conditional DEF buff |
| MEDIUM | Mudrock (headb2) | Add Ward of Fertile Soil as second talent |
| LOW | Lumen | Verify Intensive Care vs An Everyman's Wish |

---

## Notes on Reliability

WebSearch results for Arknights wiki vary by module level and patch. These findings should be
cross-checked against ArknightsGameData repo before implementing changes. Particularly uncertain:
- Ashlock tile adjacency bonus (may be different trigger condition)
- Lumen SP grant (could be a module bonus, not base talent)
- Erato Song of Dreams (SLEEP status not currently in sim StatusKind)

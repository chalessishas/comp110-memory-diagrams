# Arknights Sim: S2 Test Coverage Research
_Generated: 2026-04-20 23:10:28 | Research Loop auto-trigger_

## Current State

- **Total tests**: 2343 (as of P125 commit `c2d3f5b`)
- **All tests green**: yes, clean working tree
- **S2 dedicated test files**: 84 operators covered
- **Operators without dedicated `_s2.py`**: 12

## Remaining S2 Test Gap

| Operator | S2 Skill | Key Mechanics |
|----------|----------|---------------|
| akkord | Harmonic Blast | AUTO_ATTACK trigger, CASTER_BLAST pierce |
| beanstalk | Everyone Together! | 12 DP/15s drip, block=0 |
| courier | Support Order | AUTO 15s skill, vanguard utility |
| deepcolor | Jellyfish S2 | 1 Jellyfish summoner (vs S3's 2) |
| durnar | (S2 name TBD) | DEF+50%, block=4 |
| glaucus | (S2 name TBD) | AoE arts + BIND on enemies in range |
| kroos2 | (S2 name TBD) | ATK+100% + direct FREEZE |
| meteo | (S2 name TBD) | ATK+50% + wider splash |
| mulberry | (S2 name TBD) | MEDIC_WANDERING heal + talent clears elemental bars |
| rope | Binding Arts | instant, 200% ATK + 1.5s BIND + 3-tile pull |
| shining | Faith | 300% ATK shield, 30s duration |
| specter | (S2 name TBD) | ATK+160% + lifesteal |

## Priority Recommendation

**High-complexity (implement first)**:
1. `rope` — multi-mechanic: BIND + pull distance, instant skill timing
2. `glaucus` — AoE arts + BIND, interaction with Tidal Current SLOW talent
3. `kroos2` — FREEZE mechanic, interaction with Arctic Fox COLD talent
4. `specter` — lifesteal, interaction with Undying Will talent

**Medium complexity**:
5. `shining` — shield = 300% ATK, Illuminate talent interaction
6. `durnar` — DEF+50% + block=4 (straightforward buff test)
7. `meteo` — ATK+50% + splash radius increase

**Simpler (batch together)**:
8-12. akkord, beanstalk, courier, deepcolor, mulberry

## Approach Suggestion

Batch the simpler 5 (akkord/beanstalk/courier/deepcolor/mulberry) in one progress loop pass (~85 tests), then handle the 4 complex ones individually or in pairs. This mirrors the P122-P125 cadence that has been highly effective.

## S1 Coverage Status

Not yet audited. After S2 is complete (~12 more operators), the next phase should be:
1. S1 coverage audit
2. Cross-operator interaction tests (talent stacking, multi-operator combos)
3. Stage-level integration tests using stages/loader.py

## Notes

- `glacus` (alternate spelling) already has `glacus_s2.py` added in P125 — different from `glaucus`
- `glaucus` still missing (Decel Binder archetype, SLOW aura talent)
- `registry.py` is infrastructure, not an operator — correctly excluded

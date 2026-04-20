# Research Loop — 2026-04-20 04:04:27
## arknights-sim ECS v2: S2 Pipeline Analysis

### Status
- P58 Gravel S2 just shipped (1432 tests green)
- Liskarm S2 already implemented (Voltaic Shield, AoE pulse)
- 5 operators remain S1-only: elysium, manticore, ptilopsis, erato, spuria

### Priority Ranking

| Operator | Proposed S2 | Pattern | ECS Gaps |
|----------|------------|---------|----------|
| **Elysium** | "Tactical Gear" — 24 DP/12s + ATK+60%, block=0 | DP drip + ATK buff + block save/restore | None |
| **Ptilopsis** | "Resonance Echo" — heal×1.8 + ATK+30% buff to 2 nearest allies | Heal mult + INSPIRATION-like aura | Buff expiration refresh |
| **Manticore** | "Venom Surge" — ATK+70% + ASPD buff (reduced atk_interval) | Dual ATK+ASPD buff | Verify ASPD_UP buff axis |
| **Erato** | "Suppressive Barrage" — ATK+120% + periodic RES_DOWN to range | ATK buff + range-scan debuff | Verify RES_DOWN StatusKind |
| **Spuria** | Pure ATK+100% S2 (summon decoy variant deferred) | Simple ATK buff | Summon API absent |

### Elysium S2 Spec (P59 — implement next)

```
Name: "Tactical Gear"
sp_cost: 28, initial_sp: 12, duration: 12.0s
trigger: AUTO, requires_target: False (DP generator, doesn't need enemies)
behavior_tag: "elysium_s2_tactical_gear"

on_start:
  - Save block, set block=0
  - Append Buff(ATK, RATIO, 0.60, source_tag="elysium_s2_tg")
  - setattr(_DP_FRAC_ATTR, 0.0)

on_tick(dt):
  - frac += 2.0 * dt; gained = int(frac)
  - if gained > 0: world.global_state.refund_dp(gained)
  - setattr(_DP_FRAC_ATTR, frac - gained)

on_end:
  - Restore block from _saved_block
  - Remove buffs by source_tag
  - Clear DP frac

Tests:
  1. S2 configured (name, slot, duration, requires_target=False)
  2. block=0 on skill start
  3. ATK buff applied (~1.6× base ATK)
  4. ~24 DP generated over 12s (±1 tolerance)
  5. block restored after skill ends
  6. S1 regression (DP drip still works)
```

### ECS Gaps Identified

| Gap | Severity | Recommendation |
|-----|----------|---------------|
| Temporary summon spawn on skill (for Spuria S2) | HIGH | Use Mayer pattern for now; generalize later |
| ASPD buff axis (for Manticore S2) | MEDIUM | Verify BuffAxis.ASPD_UP reduces atk_interval in effective stats |
| RES_DOWN status refresh (for Erato S2) | LOW | StatusEffect.expires_at works; just refresh each tick |

### Test Coverage Note
All proposals follow the standard 5-test pattern:
configured → on_start effect → on_tick behavior → on_end cleanup → S1 regression

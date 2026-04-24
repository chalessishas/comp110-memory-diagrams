# Arknights Skill Data Research — rdoc batch
Date: 2026-04-24
Session: sonnet-0424ac

Source: Kengxxiao/ArknightsGameData (zh_CN) + Kengxxiao/ArknightsGameData_YoStar (en_US)
All values at Skill Level 7 (index 6 in levels array).

SP type mapping:
- `INCREASE_WITH_TIME` → AUTO_TIME
- `INCREASE_WHEN_ATTACK` → AUTO_ATTACK

---

## Operator Index

| Filename | EN Name | ZH Name | Stars | Class/Archetype |
|----------|---------|---------|-------|-----------------|
| rdoc.py | Doc (R.Doc) | 医生 (空弦) | 5★ | Guard/Fighter |
| savage.py | Savage | 暴行 (野鬃) | 5★ | Guard/Centurion |
| serum.py | Corroserum | 蚀清 (血清) | 5★ | Caster/Core |
| sensi.py | Senshi | 森西 (先师) | 5★ | Defender/Guardian |
| necras.py | Necrass | 死芒 (死亡) | 5★ | Caster/Core |
| nightm.py | Nightmare | 夜魔 (恶梦) | 4★ | Caster/Core |

---

## Skill Data Tables

### rdoc — Doc (R.Doc / 医生)

#### S1: skchr_rdoc_1 — "Violent Response" / "以暴制暴"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 30 |
| Initial SP | 11 |
| Duration | -1.0s (instant/bullet-based) |
| Blackboard | `skill_max_trigger_time`=3, `attack@trigger_time`=31, `heal_scale`=3.0, `base_attack_time`=-0.7 |

**Classification: COMPLEX**
Reasons: duration=-1 (bullet mechanic, fires 31 shots then ends), self-heal on activation, massive attack speed buff via `base_attack_time`, 3-use-per-deploy limit. Not a simple stat buff during a timed window.

#### S2: skchr_rdoc_2 — "Stim Pistol" / "激素手枪"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 20 |
| Initial SP | 9 |
| Duration | -1.0s (instant) |
| Blackboard | `heal_scale`=6.0, `skill_max_trigger_time`=3 |

**Classification: COMPLEX**
Reasons: instant projectile that heals the first allied operator hit, directional targeting, 3-use-per-deploy limit. No timed duration stat buff — pure active ability.

**Stub discrepancies vs current rdoc.py:**
- S1 stub says sp_cost=5, initial_sp=0, duration=0 → actual: sp_cost=30, initial_sp=11, duration=-1
- S2 stub says sp_cost=40, initial_sp=20, duration=20s → actual: sp_cost=20, initial_sp=9, duration=-1

---

### savage — Savage (暴行)

#### S1: skchr_savage_1 — "Power Strike β" / "强力击·β型"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_ATTACK (INCREASE_WHEN_ATTACK) |
| Trigger | AUTO |
| SP Cost | 4 |
| Initial SP | 0 |
| Duration | 0.0s (instant, next-attack buff) |
| Blackboard | `atk_scale`=2.0 |

**Classification: COMPLEX**
Reasons: `atk_scale` (not `atk`) — this is a multiplier on the next single attack, not a sustained ATK% stat buff. Duration=0 means it's instant/next-attack. Would require a "charged attack" mechanic, not a simple stat buff window.

#### S2: skchr_savage_2 — "Precise Blast" / "微差爆破"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_ATTACK (INCREASE_WHEN_ATTACK) |
| Trigger | MANUAL |
| SP Cost | 19 |
| Initial SP | 0 |
| Duration | 0.0s (instant) |
| Blackboard | `max_target`=4, `atk_scale`=3.6 |

**Classification: COMPLEX**
Reasons: instant AoE strike hitting up to 4 enemies in 3-tile range ahead, `atk_scale` not `atk`. No timed buff window.

**Stub discrepancies vs current savage.py:**
- S1 stub says sp_cost=5, AUTO_ATTACK — actual: sp_cost=4. Close but not exact.
- S2 stub says sp_cost=40, initial_sp=20, AUTO_TIME, MANUAL, duration=20s → actual: sp_cost=19, initial_sp=0, AUTO_ATTACK, MANUAL, duration=0

---

### serum — Corroserum (蚀清)

#### S1: skchr_serum_1 — "Focus Overload" / "专注力超载"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 30 |
| Initial SP | 0 |
| Duration | 30.0s |
| Blackboard | `atk`=1.0, `stun`=10.0 |

**Classification: COMPLEX**
Reasons: ATK+100% for 30s is a pure stat buff BUT has a side effect: operator is Stunned for 10 seconds after the skill ends (`stun`=10.0 key, applied post-skill). The stun mechanic is not implementable as a simple stat buff — it requires a post-skill state change. Also initial_sp=0 vs stub's 0 (matches).

**If stun post-effect can be ignored for simulation purposes**, S1 could be treated as SIMPLE (atk only during duration). However the stun is a meaningful mechanic and should be tracked.

**Verdict: COMPLEX** (post-skill stun side effect)

#### S2: skchr_serum_2 — "Conductive Corrosive Blast" / "传导蚀滞弹"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 40 |
| Initial SP | 25 |
| Duration | 25.0s |
| Blackboard | `atk`=0.7, `attack@silence`=3.5 |

**Classification: COMPLEX**
Reasons: ATK+70% combined with on-hit silence for 3.5s per attack. `attack@silence` is not a simple stat key — requires per-hit debuff application mechanic.

**Stub discrepancies vs current serum.py:**
- S1 stub says sp_cost=10, initial_sp=0, duration=0, AUTO_TIME, AUTO → actual: sp_cost=30, initial_sp=0, duration=30, AUTO_TIME, MANUAL
- S2 stub says sp_cost=35, initial_sp=18, duration=15 → actual: sp_cost=40, initial_sp=25, duration=25

---

### sensi — Senshi (森西)

#### S1: skchr_sensi_1 — "A Meal For One" / "单人份料理"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | AUTO |
| SP Cost | 8 |
| Initial SP | 0 |
| Duration | 3.0s |
| Blackboard | `heal_scale`=2.5, `atk`=0.17, `attack_speed`=17.0, `max_hp`=0.22, `up_duration`=8.0 |

**Classification: COMPLEX**
Reasons: 3-second cooking channel (stops attacking), then heals an ally for 250% ATK, then randomly grants one of three buffs (ATK+17%, ASPD+17, or MaxHP+22%) for 8 seconds. The random selection from three possible buffs and the heal-on-completion make this non-trivial. Not a deterministic stat buff.

#### S2: skchr_sensi_2 — "Monster Meals For Many" / "团体魔物大餐"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 25 |
| Initial SP | 8 |
| Duration | 10.0s |
| Blackboard | `tick_heal_scale`=0.38, `heal_scale`=1.5, `magic_sp`=10 |

**Classification: COMPLEX**
Reasons: 10-second cooking channel, stops attacking, heals all nearby allies for 38% ATK/sec during channel, then AoE heal for 150% ATK. No stat buff at all — pure healing mechanic.

**Stub discrepancies vs current sensi.py:**
- S1 stub says sp_cost=5, initial_sp=0, AUTO_ATTACK → actual: sp_cost=8, initial_sp=0, AUTO_TIME
- S2 stub says sp_cost=40, initial_sp=20, AUTO_TIME, duration=25s → actual: sp_cost=25, initial_sp=8, duration=10

---

### necras — Necrass (死芒)

#### S1: skchr_necras_1 — "Dread Desire" / "噩愿"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 17 |
| Initial SP | 6 |
| Duration | -1.0s (toggle) |
| Blackboard | `atk_scale`=3.7, `range_radius`=1.5 |

**Classification: COMPLEX**
Reasons: summon mechanic — passive AoE damage when Servant of Lamentation is created/upgraded; active use re-summons all servants. Core identity is the summon system. Duration=-1 (toggle). Not a stat buff.

#### S2: skchr_necras_2 — "Snap the Withered" / "折朽"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 22 |
| Initial SP | 11 |
| Duration | 12.0s |
| Blackboard | `atk_scale`=1.3, `additional_token_cnt`=2.0, `hit_duration`=12.0, `interval`=0.5, `max_target`=2 |

**Classification: COMPLEX**
Reasons: Puts up to 2 enemies to Sleep, deals `atk_scale` arts damage every 0.5s for 12s. AoE sleep/DOT mechanic, not a stat buff.

**Stub discrepancies vs current necras.py:**
- S1 stub says sp_cost=10, initial_sp=0, AUTO_TIME → actual: sp_cost=17, initial_sp=6, duration=-1
- S2 stub says sp_cost=35, initial_sp=18, duration=15s → actual: sp_cost=22, initial_sp=11, duration=12

---

### nightm — Nightmare (夜魔)

#### S1: skchr_nightm_1 — "Drain Soul" / "灵魂汲取"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | MANUAL |
| SP Cost | 80 |
| Initial SP | 40 |
| Duration | 60.0s |
| Blackboard | `attack@heal_scale`=0.7, `attack@max_target`=1.0 |

**Classification: COMPLEX**
Reasons: Each attack during skill heals up to 1 nearby ally for 70% of damage dealt. HP drain/lifesteal mechanic applied on each hit. No pure stat buff keys — `attack@heal_scale` is not in {atk, def, max_hp, aspd, attack_speed, magic_resistance}.

#### S2: skchr_nightm_2 — "Night Phantom" / "夜魇魔影"

| Field | Value |
|-------|-------|
| SP Recovery | AUTO_TIME (INCREASE_WITH_TIME) |
| Trigger | AUTO |
| SP Cost | 24 |
| Initial SP | 0 |
| Duration | -1.0s (toggle/instant effect) |
| Blackboard | `move_speed`=-0.6, `max_target`=3, `interval`=0.066, `value`=1200.0, `duration`=7.0 |

**Classification: COMPLEX**
Reasons: Applies "Nightmare" debuff to 3 enemies — slows movement speed by 60% and deals true damage proportional to distance traveled, lasting 7s per target. AoE debuff with DOT, not a stat buff.

**Stub discrepancies vs current nightm.py:**
- S1 stub says sp_cost=10, initial_sp=0, AUTO_TIME, AUTO → actual: sp_cost=80, initial_sp=40, AUTO_TIME, MANUAL, duration=60s (massive discrepancy)
- S2 stub says sp_cost=30, initial_sp=15, AUTO_TIME, MANUAL, duration=15s → actual: sp_cost=24, initial_sp=0, AUTO_TIME, AUTO, duration=-1

---

## Summary Table

| Operator | Skill | EN Name | ZH Name | SP Cost | Init SP | Duration | SP Type | Trigger | SIMPLE keys present | Verdict |
|----------|-------|---------|---------|---------|---------|----------|---------|---------|---------------------|---------|
| rdoc | S1 | Violent Response | 以暴制暴 | 30 | 11 | -1s | AUTO_TIME | MANUAL | heal_scale, base_attack_time | **COMPLEX** |
| rdoc | S2 | Stim Pistol | 激素手枪 | 20 | 9 | -1s | AUTO_TIME | MANUAL | heal_scale only | **COMPLEX** |
| savage | S1 | Power Strike β | 强力击·β型 | 4 | 0 | 0s | AUTO_ATTACK | AUTO | atk_scale (next-hit only) | **COMPLEX** |
| savage | S2 | Precise Blast | 微差爆破 | 19 | 0 | 0s | AUTO_ATTACK | MANUAL | atk_scale (instant AoE) | **COMPLEX** |
| serum | S1 | Focus Overload | 专注力超载 | 30 | 0 | 30s | AUTO_TIME | MANUAL | atk=1.0 + post-stun | **COMPLEX** |
| serum | S2 | Conductive Corrosive Blast | 传导蚀滞弹 | 40 | 25 | 25s | AUTO_TIME | MANUAL | atk=0.7 + on-hit silence | **COMPLEX** |
| sensi | S1 | A Meal For One | 单人份料理 | 8 | 0 | 3s | AUTO_TIME | AUTO | atk/aspd/max_hp (random pick) | **COMPLEX** |
| sensi | S2 | Monster Meals For Many | 团体魔物大餐 | 25 | 8 | 10s | AUTO_TIME | MANUAL | none (heal only) | **COMPLEX** |
| necras | S1 | Dread Desire | 噩愿 | 17 | 6 | -1s | AUTO_TIME | MANUAL | none (summon mechanic) | **COMPLEX** |
| necras | S2 | Snap the Withered | 折朽 | 22 | 11 | 12s | AUTO_TIME | MANUAL | none (sleep + DOT) | **COMPLEX** |
| nightm | S1 | Drain Soul | 灵魂汲取 | 80 | 40 | 60s | AUTO_TIME | MANUAL | none (lifesteal on-hit) | **COMPLEX** |
| nightm | S2 | Night Phantom | 夜魇魔影 | 24 | 0 | -1s | AUTO_TIME | AUTO | none (AoE slow + true DMG) | **COMPLEX** |

**Result: 0 of 12 skills are SIMPLE/IMPLEMENTABLE as pure stat buffs.**

---

## Stub Correction Table

The current `.py` files have placeholder (stub) values that need to be corrected. Actual verified values:

| Operator | Skill | Stub sp_cost | Actual sp_cost | Stub init_sp | Actual init_sp | Stub duration | Actual duration | Stub sp_type | Actual sp_type | Stub trigger | Actual trigger |
|----------|-------|-------------|---------------|-------------|---------------|--------------|----------------|-------------|---------------|-------------|---------------|
| rdoc | S1 | 5 | 30 | 0 | 11 | 0s | -1s | AUTO_ATTACK | AUTO_TIME | AUTO | MANUAL |
| rdoc | S2 | 40 | 20 | 20 | 9 | 20s | -1s | AUTO_TIME | AUTO_TIME | MANUAL | MANUAL |
| savage | S1 | 5 | 4 | 0 | 0 | 0s | 0s | AUTO_ATTACK | AUTO_ATTACK | AUTO | AUTO |
| savage | S2 | 40 | 19 | 20 | 0 | 20s | 0s | AUTO_TIME | AUTO_ATTACK | MANUAL | MANUAL |
| serum | S1 | 10 | 30 | 0 | 0 | 0s | 30s | AUTO_TIME | AUTO_TIME | AUTO | MANUAL |
| serum | S2 | 35 | 40 | 18 | 25 | 15s | 25s | AUTO_TIME | AUTO_TIME | MANUAL | MANUAL |
| sensi | S1 | 5 | 8 | 0 | 0 | 0s | 3s | AUTO_ATTACK | AUTO_TIME | AUTO | AUTO |
| sensi | S2 | 40 | 25 | 20 | 8 | 25s | 10s | AUTO_TIME | AUTO_TIME | MANUAL | MANUAL |
| necras | S1 | 10 | 17 | 0 | 6 | 0s | -1s | AUTO_TIME | AUTO_TIME | AUTO | MANUAL |
| necras | S2 | 35 | 22 | 18 | 11 | 15s | 12s | AUTO_TIME | AUTO_TIME | MANUAL | MANUAL |
| nightm | S1 | 10 | 80 | 0 | 40 | 0s | 60s | AUTO_TIME | AUTO_TIME | AUTO | MANUAL |
| nightm | S2 | 30 | 24 | 15 | 0 | 15s | -1s | AUTO_TIME | AUTO_TIME | MANUAL | AUTO |

---

## Notes for Implementation

### Serum S1 — "borderline SIMPLE" case
If the simulator can model the post-skill stun as a passive flag (operator locks for 10s after skill), serum S1 (`atk`=1.0 for 30s) is the closest to implementable. The atk buff portion is pure. Recommend tagging as COMPLEX-WITH-ATK-BUFF.

### Savage S1 — "next-hit multiplier"
`atk_scale` on a duration=0 AUTO_ATTACK skill means "next attack deals 2× ATK". This requires a "charged attack" modifier, not a sustained buff. Different from `atk` (which is an additive % to base ATK stat).

### Necras — summon-dependent
Both Necras skills are inseparable from her token mechanic (悲叹的仆役). Implementing without the summon system is not meaningful.

### Nightm S1 — largest stub discrepancy
sp_cost=80, init_sp=40 — the current stub (10/0) is wildly off. The skill is a 60-second toggle with lifesteal, completely different from the placeholder.

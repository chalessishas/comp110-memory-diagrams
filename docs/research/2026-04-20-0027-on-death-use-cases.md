# on_death Hook Use Cases — arknights-sim v2 ECS
**Date:** 2026-04-20  
**Context:** P13 landed (Mayer token cascade despawn). Infrastructure: `core/systems/talent_registry.py` exposes `on_death(world, unit)`. `cleanup_system.py` dispatches via `_just_died` flag, one tick after HP → 0.

---

## 1. Ling — Thunderer / Summon Death Cascade

### Mechanic
Ling (龄) is a Summoner Supporter who deploys dragon summons whose form depends on active skill:
- **S1** → Tranquilities (melee, physical)
- **S2** → Peripateticisms (ranged AoE Arts + bind burst on skill activation)
- **S3 "To Remain Oneself"** → **Thunderers** (melee multi-hit Arts, stronger stats)

S3 Thunderers can **absorb each other** (second Thunderer deployed within range of the first → merges into a single "higher" unit using 2 unit slots). No confirmed wiki source found for a **death-stun AoE** specific to Thunderers dying — search returns were inconclusive. The "Long Xian" name appears in lore/Chinese fan terminology, not in the EN wiki skill table.

### What IS confirmed on_death
- All Ling summons despawn if Ling retreats or dies (standard Summoner rule).
- S2 skill-activation releases a burst AoE + bind — this is a **skill activation event**, not on_death.
- S3 merged Thunderer "emanates an aura" doing periodic Arts damage to adjacent tiles — this is an **on_tick** aura, not on_death.

### Conclusion for ECS
No verified on_death stun explosion for Ling's dragons in EN wiki sources. The commonly discussed use case (dragon dies → AoE stun) may be CN-community folklore or confusion with **Mon3tr** (see §2). Recommend deferring Ling's S3 until the summon-merge mechanic (unit absorption, 2→1 unit limit slot cost) is the next design challenge. That's an **on_deploy** event, not on_death.

**Implementation cost:** Medium (summon absorption needs a merge event in deploy_system; AoE aura needs on_tick registered per-summon). Not blocked by on_death.

---

## 2. Kal'tsit + Mon3tr — Death Burst (Non-Damaging Restructuring)

### Mechanic
Mon3tr's talent **"Non-Damaging Restructuring"** triggers on Mon3tr's death:
- Burst: **True damage** to all enemies in surrounding 8 tiles + **Stun** for 3 seconds.
- At higher talent stages: also triggers when Mon3tr HP drops below 50% for the first time per deployment. Damage and stun duration increase at Stage 3.
- If Kal'tsit is stunned, silenced, or dies → Mon3tr vanishes (Kal'tsit → Mon3tr cascade).
- If Mon3tr dies → Mon3tr redeployment timer starts (25s at E2); Kal'tsit's skills require Mon3tr to be fielded to charge SP.

### on_death use cases here
1. **Mon3tr dies** → fire AoE True damage + Stun to 8-tile radius. This is a canonical on_death talent.
2. **Kal'tsit dies** → despawn Mon3tr (same pattern as Mayer → token, already implemented).
3. The 50%-HP trigger is a separate **on_hit_received** check, not on_death.

### ECS implementation plan
```python
# talent: "mon3tr_non_damaging_restructuring"
def _on_death(world, unit):  # unit = Mon3tr summon
    # AoE 8-tile radius True damage + stun
    now = world.global_state.elapsed
    for enemy in world.enemies():
        if _within_8_tiles(unit.position, enemy.position):
            enemy.take_damage(MON3TR_DEATH_TRUE_DAMAGE, damage_type=DamageType.TRUE)
            enemy.statuses.append(StatusComponent(kind=StatusKind.STUN, expires_at=now + 3.0))
```

Requires: `DamageType.TRUE` bypass (already in `unit_state.take_damage` if FRAGILE logic is present), 8-tile grid distance helper, stun status (already in `StatusKind.STUN`).

**Implementation cost:** Low-Medium. ~40 lines including tests. Blocked only by needing a `True` damage bypass path (check `take_damage` — currently SHIELD is the only bypass). On_death hook exists. Stun StatusKind exists.

**Why it matters:** Mon3tr is extremely high-use in actual gameplay. Correct simulation of his burst-on-death affects rotation timing, AoE stacking combos, and Kal'tsit's SP gate dependency.

---

## 3. Inspiration — Bard Stacking Rule (NOT on_death)

### Mechanic (corrected framing)
"Exclusive Inspiration" is not a named mechanic in the EN wiki — it's a **community shorthand**. The actual rule from the wiki:

> "Multiple instances of Inspiration are mutually exclusive on a given attribute; the highest effect takes precedence."

- Bard Supporters (e.g., Heidi, Bard sub-archetype) provide aura-based stat buffs via the Inspiration effect.
- When two Bards are deployed, their Inspiration effects **do not stack additively** per attribute — the higher value wins.
- Bard operators themselves **cannot receive** Inspiration buffs (self-excluded).

### Why this is hard to implement in ECS
The standard `BuffStack.RATIO` in the current system is **additive** (multiple ratio buffs summed). Inspiration requires a **"highest wins"** evaluation mode — a new `BuffStack.INSPIRATION` value, or a filtering pass in `effective_atk` that groups by source attribute and takes max.

This is **not an on_death problem** — it's a buff evaluation problem. The ECS needs a third buff stacking mode or a pre-resolve filter step.

**Implementation cost:** Medium. Requires adding `BuffStack.INSPIRATION` (or equivalent), modifying `effective_atk/def/hp` resolvers in `unit_state.py`, and an aura on_tick emitter. Entirely independent of on_death.

---

## 4. Additional on_death Use Cases (Beyond Summon Despawn)

### 4a. Retreat Cascade (on_retreat ≠ on_death)
Current gap: `on_death` fires when HP → 0 (`_just_died` flag). But **manual retreat** (operator recalled by player) currently has no hook. Mayer's cascade test only covers the death path. 

For operators like Kal'tsit, all Summoner operators, and Ling: summons must also despawn **on retreat**. This needs a separate `on_retreat` hook in the registry + `World.retreat(unit)` method that fires it.

**Implementation cost:** Low. Add `on_retreat` slot to registry tuple (index 7), add `fire_on_retreat`, add `World.retreat()` method. 2–3 hours + tests.

### 4b. Surtr — Passive Regen → Death Surge (S2/S3)
Surtr's S3: at end of skill, Surtr's HP begins draining (effectively a DOT on self). When she reaches 0 HP, she releases a massive single-hit AoE Arts burst then **cannot die** for a brief window (death immunity). This is on_death + DAMAGE_IMMUNE + post-death burst. Requires ordering guarantees: on_death fires the burst, then damage immunity is applied *before* cleanup removes her.

**Implementation cost:** High. Requires: (1) DOT self-application on skill end (exists via StatusKind.DOT), (2) ordered on_death that fires a burst AND suppresses unit removal for N ticks, (3) "invincible for N seconds after on_death" — a new state. Suggests on_death should return a bool (`should_remove: True/False`) so the cleanup system can delay removal.

### 4c. Deepcolor — Summon Dies → Spawn New Summon
Deepcolor's mechanic: when her jellyfish summon dies in combat, it splits/re-spawns (not manual, triggered by combat kill). This is on_death on the **summon** that spawns a new child unit. Already structurally identical to Mon3tr's burst — just spawns instead of deals damage.

**Implementation cost:** Low, given Mon3tr pattern. ~30 lines + tests. Interesting test: ensure the newly-spawned unit doesn't cascade-trigger another on_death loop.

### 4d. Phantom (Headhunter S3) — Clone Explodes on Death
Phantom's S3 deploys a clone. When the clone dies, it deals Arts damage to nearby enemies in a radius (confirmed game mechanic). This is purely on_death → AoE Arts, identical structure to Mon3tr but with Arts damage type instead of True damage.

**Implementation cost:** Very Low once Mon3tr is done. Share AoE helper, parameterize damage type.

### 4e. Operator-Dies → Ally Buff Expires (Linked Buffs)
Example: some skill/talent buffs are "while this operator is alive" — they attach as timed buffs, but if the operator dies mid-buff, buffs should expire immediately rather than running their remaining duration. The current system uses time-based buff expiry (`expires_at`). On operator death, a cleanup pass could remove all `source_tag` buffs originating from that operator on all allies.

**Implementation cost:** Low. Add `source_unit_id` field to `Buff` dataclass, add on_death cleanup that iterates `world.allies()` and removes buffs with matching source_unit_id.

---

## 5. Priority Matrix

| Mechanic | on_death? | Implementation Cost | ECS Correctness Impact |
|---|---|---|---|
| Mon3tr death burst + stun | YES | Low-Medium | High — flagship operator |
| Retreat cascade (on_retreat hook) | New hook | Low | High — correctness gap for all summoners |
| Deepcolor summon re-spawn | YES | Low | Medium |
| Phantom clone death burst | YES | Very Low | Medium |
| Surtr invincible death surge | YES (complex) | High | High — unique death semantics |
| Linked buff expiry on death | YES | Low | Medium — affects multi-operator comps |
| Ling summon merge | NO (on_deploy) | Medium | Medium |
| Inspiration stacking | NO (buff eval) | Medium | Medium — affects all Bard operators |

---

## 6. Recommended P14 Scope

1. **Mon3tr "Non-Damaging Restructuring"** — highest value, confirms on_death can emit AoE+status, sets pattern for Deepcolor/Phantom. Implement as `kal_tsit_mon3tr` character file with on_death + on_death cascade Kal'tsit → Mon3tr despawn.
2. **on_retreat hook** — prerequisite correctness gap; 2-3 hours, unblocks all summoner retreat tests.
3. **Deepcolor or Phantom** — follow-on, reuses Mon3tr AoE helper, good regression coverage.

Surtr and Inspiration can be separate phases (P15+).

---

## Sources
- [Ling's Summons — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Ling's_Summons)
- [Ling — Arknights Wiki Fandom](https://arknights.fandom.com/wiki/Ling)
- [Mon3tr (summon) — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Mon3tr_(summon))
- [Kal'tsit — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Kal'tsit)
- [Inspiration — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Inspiration)
- [Supporter: Bard — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Supporter/Bard)
- [Summon — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Summon)
- [Bard Supporter — Arknights Wiki Fandom](https://arknights.fandom.com/wiki/Supporter/Bard)

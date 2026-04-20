# Arknights-Sim: Next Mechanic Priorities — Archetype & Operator Research
**Date:** 2026-04-20 00:16  
**Researcher:** sonnet-0420c (Claude Sonnet 4.6)  
**Project state at research time:** 1147 tests, 88 hand-crafted operators, 419 generated operators, 51/51 archetypes covered

---

## Context Correction

The task brief described the project as "P11 complete, 72 tests, 6 operators." The actual state is significantly further: all 51 archetypes have at least one operator implementation, 1147 tests pass, and 88 operators are hand-crafted. This research therefore pivots from "which archetypes are missing?" to "which mechanics have shallow implementation depth or are entirely absent at the operator-skill level?"

---

## 1. Archetypes That Are Implemented But Mechanically Shallow

All 51 archetypes are covered, but many have only one operator implemented with minimal skills. The highest-value targets for depth expansion:

### 1a. Summoner (Supporter/Summoner)
**Representative operators:** Mayer (Supporter/Summoner — sentry summons), Ling (Supporter/Summoner — dragon units), W (Specialist — delayed bomb summons)

**Core mechanic:** Summons are independent entities with their own HP, ATK, DEF, block count, and attack targets. They share the operator's range-based origin but act autonomously each tick. A summon persists until:
- Its HP reaches 0
- The parent operator retreats (summon auto-destructs)
- The skill duration ends (skill-gated summons only)

**What's missing in ECS:**
- `SummonComponent` on entities (unit_id, parent_operator_id, summon stats, lifetime)
- Parent death → cascade despawn of all children with same `parent_operator_id`
- Summons counting against the global unit cap
- Mayer S3 specifically: deploys Sentry units that have their own DEF and last until destroyed (not duration-gated)

**ECS test value:** Tests for cross-entity lifecycle dependencies — a pattern absent from all current operator implementations. Parent/child entity relationships are the hardest ECS edge case.

**Estimated LOC:** 120 (SummonComponent + spawn + despawn cascade) + 80 (Mayer S3) + 50 (tests) = ~250

---

### 1b. Bard (Supporter/Bard)
**Representative operators:** Sora (5★), Skadi the Corrupting Heart (6★ Alter), Ling (also Bard-adjacent via passive)

**Core mechanic:**
- Bards cannot attack at all
- Passive aura: heals all allies in surrounding 8 tiles / radius-2 at `10% of self.ATK per second` (continuous, not per-tick-event)
- **Inspiration** buff: increases ally ATK/DEF by a flat amount equal to `X% of Bard's ATK/DEF` — multiple Inspiration sources are **mutually exclusive** (highest value wins, they do not stack additively)
- Bards do NOT benefit from Inspiration themselves

**Skadi the Corrupting Heart (S3):** Trait converts from heal to `5% HP/second self-drain + 25–70% ATK true damage/second to enemies + Inspiration 50–110% ATK to allies` for 20 seconds. This is a damage + self-sacrifice pattern.

**What's missing in ECS:**
- Inspiration buff conflict resolution: `BuffAxis.INSPIRATION` with `exclusive=True` flag — when a second Inspiration is applied, it replaces only if higher, not additive
- Bard passive heal implemented as `on_tick` (may exist via Sora's implementation — needs verification)
- Skadi S3's HP drain as a `schedule_repeating` EventQueue event (already proven by Surtr remnant_ash pattern)

**ECS test value:** Tests for exclusive-highest-wins buff resolution. Currently all BuffAxis values stack additively. Inspiration is the first mechanic requiring non-additive buff competition. This is an architectural addition to `BuffStore` or `UnitState.effective_stat`.

**Estimated LOC:** 40 (BuffAxis.INSPIRATION + exclusivity logic) + 60 (Skadi S3) + 40 (tests) = ~140

---

### 1c. Hexer (Supporter/Hexer)
**Representative operators:** Shamare (6★), Gnosis (6★)

**Core mechanic (Shamare):** Talent "Curse" — when Shamare attacks, there's a chance to apply a stacking ATK debuff to the target (up to -50% ATK at max stacks). This is a probabilistic debuff that accumulates over multiple hits on the same target.

**Gnosis mechanic:** Attacks apply Cold status; enough Cold applications become Freeze. This is a two-phase elemental status (same as the Fire → Burn → Burst chain but for Cold → Freeze).

**What's missing in ECS:**
- Per-target stack tracking: `entity.buffs` currently stores global buffs, but Shamare's curse stacks per-enemy-unit, not globally. Requires `target.buffs.add(Buff(axis=DEF_RATIO, value=-0.1, source_tag="shamare_curse", stacks_to=5))`
- Stack cap with `source_tag` counting
- Cold accumulation counter per enemy (similar to Elemental Injury but for status buildup)

**ECS test value:** Tests for stacking debuffs with caps and probabilistic application. The existing `on_hit_received` hooks (Liskarm) are on the defender side; Shamare's curse is on the attacker side (`on_hit_dealt` hook pattern).

---

### 1d. Juggernaut (Defender/Juggernaut)
**Representative operators:** Mudrock (6★), Nian (6★)

**Current implementation:** Mudrock is implemented but S3's Phase 1 invulnerability is documented as missing in `2026-04-19-2359-research-loop-report.md`.

**Core mechanic gap:** `invulnerable: bool` flag on `UnitState` with `damage_taken = 0` gate in `combat_system.py`. One additional flag, ~5 LOC change to `take_physical` / `take_arts`.

**ECS test value:** Completes the two-phase EventQueue state machine pattern already architected in the existing research.

---

## 2. Most Mechanically Interesting Operators for ECS Edge Cases

These operators are specifically valuable because they stress-test the ECS architecture rather than just adding more instances of existing patterns:

### 2a. Kal'tsit — Summoner with Skill-Gated Summon Dependency
**Archetype:** Medic/Medic (with Mon3tr as Summoner mechanic)  
**Key mechanics:**
- Mon3tr is a permanent summon with its own `redeployment_cd` (25s at E2) — independent of Kal'tsit's deployment
- If Mon3tr leaves Kal'tsit's attack range, **Mon3tr's DEF drops to 0** — requires continuous range-check on per-tick
- Kal'tsit's skills can only be cast if Mon3tr is currently deployed in the field
- Talent: when Mon3tr is killed (not retreated), all enemies in 8-tile radius are Stunned for 3s and take 1200 True damage

**ECS test value:**
- Range-dependent stat modification (`on_tick` check: `if not is_in_range(mon3tr, kalt_range): mon3tr.def_override = 0`)
- Summon-death triggering a one-shot AoE event (requires a `on_death` hook for summon entities)
- Skill availability gating on a separate entity's deployment state — currently no skill has a precondition other than `sp >= sp_cost`

**Why it matters:** Introduces `on_death` hooks (currently absent — only `on_kill` for killers, not `on_being_killed`), and cross-entity preconditions for skill activation.

**Estimated LOC:** ~200 (Mon3tr entity + range check + death hook + skill precondition system)

---

### 2b. Eyjafjalla — RES Debuff + Multi-Target Caster with Faction-Wide ATK Aura
**Archetype:** Caster/Splash  
**Implementation status:** `eyjafjalla.py` exists, `test_v2_eyjafjalla.py` exists

**What to verify is implemented:**
- S3 Volcano: `RES -25` applied to primary target for 6 seconds (not just the burst-effect RES reduction)
- Pyrobreath talent: `All Caster operators' ATK +7/14%` — this is a **faction-wide aura** (all deployed units with class=CASTER get a BuffAxis.ATK bonus while Eyjafjalla is deployed)
- Wild Fire talent: random SP gain of 7–15 on deploy

**ECS test value:** Faction/class-based aura buffs applied to other entities. Currently all talent effects are per-operator-self or per-adjacent-target. A class-filtered aura requires `world.all_units_where(lambda u: u.class == CASTER)` and applying buffs dynamically as operators are deployed/retreated. This is a new ECS query pattern.

---

### 2c. Surtr — HP Drain Schedule + Fatal Damage Prevention
**Implementation status:** `surtr.py` exists, `test_v2_surtr.py` exists

**What to verify is implemented:**
- S3 Twilight: HP drain is not flat — it scales from 0% to **20% max HP/second over 60 seconds** (increasing ramp, not constant)
- Remnant Ash talent: after taking fatal damage, prevents HP from reaching 0 for 8-9 seconds then forces retreat — this requires a "damage interception" hook that changes `damage_applied` before it reduces HP
- S3 cannot be used again for the rest of the deployment after Remnant Ash triggers (one-use mechanic)

**ECS test value:** Non-linear HP drain schedules and fatal-damage interception. The current `take_physical` / `take_arts` methods return damage dealt and reduce HP directly. Remnant Ash requires a layer that intercepts the final HP reduction and clamps it.

---

### 2d. Skadi the Corrupting Heart — Self-Damaging Bard with True Damage Aura
**Archetype:** Supporter/Bard  
**Key mechanics (S3 "The Tide Surges, The Tide Recedes"):**
- Self HP drain: 5% max HP/second for 20 seconds (= 100% HP total — she will reach 0 HP if not healed during skill)
- Enemy damage: 25–70% ATK as **true damage per second** to all enemies in range (continuous AoE true damage, not attack-based)
- Inspiration aura: +50–110% ATK to allies

**ECS test value:**
- True damage dealt through a non-attack path (currently all true damage is via `take_true(dmg)` called from attack handlers; here it should fire from a per-tick passive, separate from the attack system)
- Self-destruction through self-damage during skill (do Remnant Ash / other HP floor mechanics interact?)
- Inspiration exclusivity (see section 1b above)

---

### 2e. Warfarin — SP-on-Kill with Probabilistic Ally Targeting
**Implementation status:** `warfarin.py` exists, `test_v2_warfarin_s2.py` exists

**What to verify is implemented:**
- Blood Sample Recycle talent: `Warfarin + random 1 ally in range` each gain `+1 SP` when any enemy dies within range — this is an `on_kill` talent that targets a random ally (similar to Liskarm SP battery, but triggered by kills not by taking damage)
- S2: `+ATK% to Warfarin + random 1 ally in range` with `both lose 3% max HP/second` — the HP drain must apply to BOTH units, not just Warfarin; the ally target is locked at skill activation time

**ECS test value:** Validates that `on_kill` SP share and dual-entity HP drain from a single skill are correctly handled, especially when the buffed ally retreats mid-skill.

---

## 3. High-Value Synergy Combos for Integration Tests

These combos produce emergent behavior that unit tests cannot catch:

### Combo A: Liskarm + Hoshiguma (SP Battery + DEF Shield)
**Already partially tested** (mentioned in research). Specific edge case NOT yet tested:
- Liskarm takes damage → grants SP to Hoshiguma → Hoshiguma S3 activates during the same tick that Liskarm's SP grant fires → does the skill activation happen in the same tick or next tick?
- **Test:** Verify that `skill_system.py` processes SP grants and then checks for auto-trigger in the same tick (no one-tick delay gap).

### Combo B: Eyjafjalla + Any Caster (Faction ATK Aura)
**Not yet tested:**
- Deploy Eyjafjalla → all Casters in field gain ATK +14%
- Retreat Eyjafjalla → buff must be removed from all Casters immediately
- **Test:** Two-Caster squad; deploy Eyjafjalla; verify both Casters' `effective_atk` increases; retreat Eyjafjalla; verify both revert.
- **ECS stress:** Requires `on_deploy` and `on_retreat` hooks that scan all allied units and modify their buff store — currently no operator does this.

### Combo C: Warfarin + Surtr (SP Battery + HP Drain Cancel)
- Warfarin S2: Surtr gains ATK + both lose 3% HP/second
- Surtr S3: Surtr loses 20% HP/second (at 60s into skill)
- Surtr Remnant Ash activates when HP approaches fatal — but this is triggered by damage, not by HP drain (HP drain bypasses damage interception)
- **Question:** Does Remnant Ash trigger from the Warfarin S2 HP drain or only from enemy attack damage?
- **Test value:** Validates interaction between non-damage HP loss and damage-interception talents — a critical ambiguity in the combat system.

### Combo D: Kal'tsit + Abyssal Hunters (Faction Faction-Wide ATK Buff)
- Skadi the Corrupting Heart deployed → all Abyssal Hunter operators gain ATK +22% and max HP +20%
- Kal'tsit is an Abyssal Hunter → her ATK +22% changes Mon3tr's combat performance (Mon3tr's stats are derived from Kal'tsit at spawn time or continuously?)
- **Test value:** Faction buff applying to a summon whose stats reference its parent — whether the buff is snapshotted at spawn or is live-computed changes the outcome.

### Combo E: Saria + Any Defender (SP Battery via Healing)
- Saria Refreshment talent: heals trigger +1 SP to healed ally
- Saria healing Hoshiguma → Hoshiguma SP charges faster during combat
- **Test:** Verify SP accumulation rate is exactly 1 SP per heal event (not per tick), and that auto-trigger activates when Hoshiguma's SP threshold is met mid-combat.
- **Already has pattern** from Liskarm SP battery; this validates the `on_heal_received` hook (if it exists) vs. the `on_hit_received` hook.

---

## 4. Mechanic Gaps Identified as Highest Priority

Ranked by ECS architecture impact (operators that require new system primitives, not just new operator files):

| Priority | Mechanic | Operators | New ECS Primitive | Est. LOC |
|----------|----------|-----------|-------------------|----------|
| 1 | Summon entity lifecycle (parent/child) | Mayer, Ling, Kal'tsit | `SummonComponent` + cascade despawn | 250 |
| 2 | Exclusive Inspiration buff conflict | Sora, Skadi alter, all Bards | `BuffAxis.INSPIRATION` with `exclusive=True` | 80 |
| 3 | Mudrock S3 Phase 1 invulnerability | Mudrock | `invulnerable` flag + damage gate | 50 |
| 4 | Faction-wide aura (class filter) | Eyjafjalla, Warfarin, Zima | `on_deploy`/`on_retreat` world scan | 100 |
| 5 | `on_death` hook for summons | Kal'tsit Mon3tr | New hook type in skill registry | 60 |
| 6 | HP drain non-linear ramp | Surtr S3 | `schedule_repeating` with scaling payload | 40 |
| 7 | Stacking debuffs with cap | Shamare | Stack counter per source_tag in BuffStore | 70 |

---

## 5. Archetype Coverage Assessment vs. Fandom Wiki Complete List

For completeness, archetypes confirmed as having no hand-crafted test file:

| Archetype | Covered by | Test file | Depth |
|-----------|-----------|-----------|-------|
| Guard/Mercenary | (unknown — new archetype) | Unknown | Check |
| Guard/Primal Guard | (new — elemental) | Unknown | Check |
| Caster/Shaper Caster | (summon on kill) | Unknown | Check |
| Caster/Primal Caster | (elemental) | Unknown | Check |
| Sniper/Loopshooter | (boomerang) | Unknown | Check |
| Sniper/Skybreaker | (aerial → land AoE) | Unknown | Check |
| Supporter/Ritualist | (elemental injury) | Unknown | Check |
| Supporter/Alchemist | (throw alchemy units) | Unknown | Check |
| Specialist/Skyranger | (take off, block aerial) | Unknown | Check |
| Vanguard/Strategist | (DP gen + support unbench) | Unknown | Check |
| Defender/Primal Protector | (elemental) | Unknown | Check |

Run `grep -r "ARCH_" tests/` to map these against actual test coverage. These newer archetypes (Primal*, Shaper, Strategist, Alchemist) were added in more recent game updates and may genuinely be missing.

---

## Sources

- [Class — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Class)
- [Kal'tsit — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Kal%27tsit)
- [Skadi the Corrupting Heart — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Skadi_the_Corrupting_Heart)
- [Warfarin/Overview — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Warfarin/Overview)
- [Surtr — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Surtr)
- [Eyjafjalla — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Eyjafjalla)
- [Supporter/Summoner — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Supporter/Summoner)
- [Supporter/Bard — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Supporter/Bard)
- [Inspiration — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Inspiration)
- [Damage — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Damage)
- [Abyssal Hunters — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Abyssal_Hunters)
- [Sanity;Gone — Kal'tsit Guide](https://old.sanitygone.help/operators/kaltsit)

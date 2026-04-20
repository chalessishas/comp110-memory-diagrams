# Arknights S3 Gaps Research
**Generated:** 2026-04-20 10:37:44  
**Scope:** 6★ operator S3 mechanics not yet in arknights-sim; ECS pattern gaps

---

## 1. Specter S3 — Status: ALREADY IMPLEMENTED (as custom mechanic)

**Real game mechanic (Specter is actually 5★, not 6★):**  
Specter's iconic skill is S2 "Bone Fracture" — during the duration, her HP cannot drop below 1 (pseudo-immortality), ATK +160%. After the skill ends she is Stunned for 10 seconds. She only has 2 skills in total (no S3 in game).

Her "undying on death" behavior is actually her **Talent** on the upgraded version "Specter the Unchained" (6★ Dollkeeper): when HP hits 0, a substitute doll takes her place for 20 seconds, then she returns with full HP.

**Simulator state:** The simulator has `specter.py` with a custom `S3 "Deathless Aegis"` that does not match real game data. The real Specter only has S2 for the immortality mechanic. However the implemented behavior (undying via talent + S3 giving sustained immortality) is a **reasonable creative extension** for simulator purposes, not a bug per se — just not game-accurate.

**Real Specter S2 mechanics for potential faithful reimplementation:**
- HP floor: cannot drop below 1 during skill
- ATK +160% at max level  
- 15s duration (at SL7), 10s Stun after skill ends
- AUTO_TIME SP gain, manual or auto trigger

**Key ECS pattern from real S2:** "HP floor clamp" + "post-skill debuff (Stun)" — the post-skill Stun on Specter S2 is not yet modeled in the simulator's current Specter implementation.

---

## 2. Lumen S3 — NOT YET IMPLEMENTED (only S2 exists in simulator)

**Real game mechanic:**  
S3 "This Lantern Undying" — ammo-based skill (8 charges at M3).
- While skill is active: ATK +55%, ASPD +30
- When Lumen heals an ally **with a Negative Status**: consumes 1 charge, healing amount ×2 (effectively 200% ATK), and **cleanses all Negative Statuses** from that ally
- Ammo is NOT consumed for healthy targets — the skill lasts indefinitely if no status-afflicted allies exist
- Skill ends when all 8 ammo are consumed or player manually deactivates
- SP cost: ~25-30 (auto-time), no fixed duration

**New ECS patterns required:**
1. **Ammo-based skill with conditional charge consumption** — skill stays active but each qualifying heal costs 1 charge. Distinct from current duration-based skills.
2. **Status-conditional heal amplification** — check if target has a Negative Status before dealing full heal power. Doubles heal+cleanse in one interaction.
3. **Cleanse mechanic** — remove all negative statuses from target on a healing hit. The sim has status effects but no "cleanse all negatives" system call yet.

**Simulator file:** `/Users/shaoq/Desktop/VScode Workspace/arknights-sim/data/characters/lumen.py` — only S2 "Group Recovery" exists, no S3 at all.

---

## 3. Shining S3 — NOT YET IMPLEMENTED (only S2 exists in simulator)

**Real game mechanic:**  
S3 "Creed Field" — duration-based aura skill.
- Buffs Shining's own ATK (moderate boost)
- While active: DEF +X to all allies within Shining's healing range (area buff)
- Duration: ~20-25s
- Effective against physical damage; does nothing against Arts damage
- Quick cooldown post-activation, good for reactive/emergency use

**New ECS patterns required:**
1. **Ranged DEF aura on skill activation** — periodic check of all allies in range_shape and apply a DEF buff component. Differs from Myrtle S3 team SP aura (which affects SP) and Pallas S3 (which affects arts/block). This would be the first **physical mitigation aura** in the sim.
2. **Aura buff expiry tracking on range exit** — allies leaving range mid-skill should lose the buff. Current buff system uses expires_at timers, not position-based removal. May need a position-check hook.

**Simulator file:** `/Users/shaoq/Desktop/VScode Workspace/arknights-sim/data/characters/shining.py` — only S2 "Faith" (instant DEF shield) is implemented. Talent "Illuminate" (heal → per-hit shield) is also done. S3 not present.

---

## 4. New ECS Patterns Worth Adding

### 4a. Ammo/Charge-Based Skills (Lumen S3, Exusiai S2)
Currently skills are duration-based or instant. An ammo model needs:
- `charges_remaining` field on SkillComponent
- Skill activates when `sp >= sp_cost`, consumes charges conditionally per-event
- Skill ends when `charges_remaining == 0` or manual deactivation
- Prevents needing a fixed `duration` field

**Operators that use this:** Lumen S3, Exusiai S2 (already in sim via different approach), Nearl S3

### 4b. Post-Skill Debuff (Specter S2 Stun, Surtr S3 HP drain end)
Current `on_end` hooks exist but no "apply debuff to self at skill end" pattern. Need:
- `on_end` applying a `STUN` status with duration to the casting operator
- Stun during stun window: operator cannot attack or block
- Example: Specter S2 Stun (10s), or Surtr's escalating HP drain

### 4c. DEF/RES Aura to Allies in Range (Shining S3, Saria S2)
Currently only SP aura (Myrtle S3, Ptilopsis) and Arts/block aura (Pallas S3) exist. A physical mitigation aura would need:
- `on_tick` scan of allies within `range_shape`
- Apply or refresh a buff with `expires_at = now + tick_interval + epsilon`
- On skill end: sweep and remove all aura-sourced buffs

### 4d. Cleanse System (Lumen S3, Silence S2)
Currently negative statuses (Freeze, Slow, Stun) persist until expires_at. A cleanse:
- Removes all statuses with `kind in NEGATIVE_STATUS_KINDS` from a unit
- Could be triggered on a specific heal hit or manually
- `NEGATIVE_STATUS_KINDS = {FREEZE, SLOW, STUN, POISON, BURN, ...}`

### 4e. Conditional Heal Multiplier (Lumen S3)
Heal damage (AttackType.HEAL) already goes through the standard attack pipeline. Adding a multiplier hook on "heal target has a Negative Status" would enable Lumen S3 and similar operators (e.g., future support medics).

### 4f. On-Death Token Spawn (Surtr S3 — self-retreat, Ling dragons, Mayer drones)
Surtr's escalating HP drain means she will eventually die on-field during S3. Some operators (Ling, Mayer) spawn tokens when retreating or dying. The pattern: `on_unit_death` event fires a "deploy token at position X" action. The sim has basic death handling but no on-death-spawn hook.

### 4g. Global Damage Aura (Warfarin S3, "all enemies take X damage")
Warfarin S3 applies a flat Arts damage aura to all enemies in range each second. This is distinct from an attack — it's a passive per-tick damage event not attributed to an attack roll. Pattern: `on_tick` → deal `arts_damage(value)` to all enemies in range ignoring atk_interval.

---

## Priority Ranking for Implementation

| Priority | Operator / Pattern | Why |
|----------|-------------------|-----|
| 1 | Lumen S3 (ammo + cleanse) | High mechanical novelty; enables a new skill archetype (ammo-based) |
| 2 | Shining S3 (DEF aura) | Completes the existing Shining file; 1st physical mitigation aura |
| 3 | Post-skill Stun (Specter S2 faithful) | Correctness for already-implemented operator |
| 4 | Cleanse system (shared by Lumen + future ops) | Infrastructure enabling multiple future operators |
| 5 | Global damage aura (Warfarin S3) | New damage event class distinct from normal attacks |

---

## Sources
- [Specter | Arknights Wiki - GamePress](https://ak.gamepress.gg/operator/specter)
- [Specter the Unchained | Arknights Wiki - GamePress](https://ak.gamepress.gg/operator/specter-unchained)
- [Specter Guide — Sanity;Gone](https://old.sanitygone.help/operators/specter)
- [Specter the Unchained — Sanity;Gone](https://old.sanitygone.help/operators/specter-the-unchained)
- [Lumen's overview | Arknights Wiki | Fandom](https://arknights.fandom.com/wiki/Lumen/Overview)
- [This Lantern Undying | Arknights Wiki - GamePress](https://ak.gamepress.gg/skill/lantern-undying)
- [Lumen Guide — Sanity;Gone](https://old.sanitygone.help/operators/lumen)
- [Shining's overview | Arknights Wiki | Fandom](https://arknights.fandom.com/wiki/Shining/Overview)
- [Shining | Arknights Wiki - GamePress](https://ak.gamepress.gg/operator/shining)
- [Surtr — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Surtr)

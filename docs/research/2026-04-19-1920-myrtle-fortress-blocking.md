# P8 Research: Myrtle DP Drip, Fortress Defender, Blocking Priority

**Date:** 2026-04-19  
**Context:** arknights-sim P8 planning — three open mechanics questions  
**Sources:** arknights.wiki.gg (Terra Wiki), arknights.fandom.com, GamePress

---

## 1. Standard Bearer DP Drip — Myrtle & Elysium

### Key Correction to Original Assumption

The original research prompt stated DP drip "STOPS when operator is attacking or blocking." This is **wrong**.

According to the in-game skill text (confirmed via wiki):  
> "Stops attacking and recovers X DP over the skill duration"

During skill activation, Myrtle/Elysium:
- **Cannot attack** (explicit in skill text)
- **Cannot block** (confirmed by module trait text: "Cannot block enemies during the skill duration, but grants +1 Block to an Operator in front of this unit")

DP drip is not paused by anything during the skill window — the operator is simply incapable of blocking or attacking for the entire duration. There is no conditional "stops dripping when action occurs" mechanic.

### Confirmed Numbers at Max Rank (M3/SL10)

| Operator | Skill | DP | Duration | DP/s | SP Cost | Initial SP |
|----------|-------|----|----------|------|---------|------------|
| Myrtle   | S1 Support β | 14 | 8s | 1.75 | 22 | 13 |
| Myrtle   | S2 Healing Wings | 16 | 16s | 1.00 | 24 | 10 |
| Elysium  | S1 Support γ | 18 | 8s | 2.25 | higher | — |

**S2 additional effect:** Heals a nearby friendly for 50% of Myrtle's ATK per tick.

### ECS Modeling Implications

- DP drip is a **fixed-rate linear accumulation** over the skill duration: `dp_per_tick = total_dp / (duration * ticks_per_second)`
- No conditional pause logic needed — skill activation simply sets a `cannot_block = True` flag and `cannot_attack = True` flag
- SP regeneration: Myrtle is a Vanguard — she regenerates SP by blocking enemies normally (1 SP per blocked enemy hit). During skill, she cannot block, so SP regen from blocking halts naturally (no special case needed)
- The "Standard Bearer" subclass trait gives +1 DP when deployed (separate from skill)

---

## 2. Fortress Defender — Correct Operator List & Trait

### Official Subclass

**Archetype:** Fortress Defender  
**Exact trait text (from wiki.gg):**  
> "When not blocking enemies, prioritizes dealing ranged AoE Physical damage"

Additional characteristics confirmed:
- Ranged attack has AoE splash (physical)
- Cannot target air units with ranged attack
- Has a blind spot in the two rows directly in front (cannot hit those tiles with ranged attack)
- When blocking an enemy, switches to normal melee single-target attack

### Complete Operator Roster (confirmed: 3 operators total)

| Operator | Rarity | Notes |
|----------|--------|-------|
| Ashlock  | 5★ | First Fortress Defender released |
| Firewhistle | — | |
| Horn     | 6★ | Victorian faction |

### Corrections to Original Assumptions

- **Nian** is NOT a Fortress Defender — she is a **Protector Defender** (blocks 3, high DEF, ally DEF buff talent)
- **Eunectes** is NOT a Fortress Defender — she is a **Duelist Defender** (block 1, extremely high ATK)
- **Mudrock** is a Guard (Brawler), not a Defender
- **Saria** is a Guardian Defender (heals allies via skill)

The original prompt's "Fortress Defender" list (Nian, Eunectes, Tandem-ψ) was incorrect. Tandem-ψ does not appear in the Fortress Defender category.

### ECS Implementation Notes for Fortress Trait

```
if operator.blocking_count == 0:
    # ranged AoE physical attack, cannot target air
    attack_mode = RANGED_AOE_PHYSICAL
    target_priority = GROUND_ONLY
else:
    # standard melee single-target
    attack_mode = MELEE_SINGLE
```

The tile-exclusion blindspot (2 rows in front) needs to be modeled in the attack range definition, not in the targeting logic.

---

## 3. Blocking Priority Mechanics

### Confirmed Mechanic

**Primary:** Enemies are blocked in order they arrived on the tile (first-on-tile = first blocked).  
**Tie-breaker when comparing blocked enemies for *targeting*:** **Path distance remaining** (not physical/Euclidean distance to goal).

Exact quote from community documentation:
> "if the enemy's pathing is convoluted, friendly units' targeting will be based on the length of the enemy's path remaining. For example, an enemy may be near a Protection Objective, but if they make several laps or take longer to get there, they will not be prioritized."

### What This Means for Targeting vs. Blocking

These are two separate questions:

| Question | Answer |
|----------|--------|
| Which enemies get blocked? | First to enter the operator's tile, up to block count |
| Which blocked enemy does the operator attack? | The blocked enemy with shortest **path distance remaining** |
| What happens to excess enemies? | They pass through the tile unblocked |

### ECS Implementation Notes

Current implementation assigns enemies to blockers via targeting — needs to be split into two phases:

1. **Block assignment** (on enemy movement tick): When enemy steps onto operator's tile, add to `blocked_by` set if operator has capacity. This is purely spatial/arrival-order.

2. **Attack target selection** (on operator attack tick): Among all currently blocked enemies, select the one with minimum `path_distance_remaining`. This requires enemies to track their remaining path length (tile hops or weighted path cost to exit).

**Key insight:** Physical proximity to exit tile is NOT the right metric. A enemy 2 tiles from the goal via a shortcut is prioritized over one 1 tile away physically if that tile is 5 hops from exit via the actual path.

---

## Action Items for P8 Implementation

### Priority 1 — Myrtle (Standard Bearer DP drip)
- [ ] Add `StandardBearerSkillComponent` with `dp_total`, `duration`, `elapsed` fields
- [ ] Each sim tick: `dp_gain += dp_total / (duration * ticks_per_second)` — no conditional logic
- [ ] Skill activation sets `operator.can_block = False`, `operator.can_attack = False`
- [ ] Skill deactivation restores both flags
- [ ] Test: deploy Myrtle, activate S1, verify exactly 14 DP over 8s, verify 0 blocking during skill

### Priority 2 — Blocking Priority Fix
- [ ] Verify current blocking uses arrival-order assignment, not targeting-based
- [ ] Add `path_distance_remaining` field to enemy entities (updated each movement tick)
- [ ] Change operator attack target selection: `min(blocked_enemies, key=lambda e: e.path_distance_remaining)`
- [ ] Test: two enemies on same blocker tile at different path distances, confirm correct target priority

### Priority 3 — Fortress Defender (Ashlock/Horn)
- [ ] Correct operator list: Ashlock (5★), Firewhistle, Horn (6★) — NOT Nian/Eunectes
- [ ] Implement `FortressDefenderComponent` with range toggle:
  - `blocking_count == 0` → ranged AoE physical, ground-only, blind spot in front 2 rows
  - `blocking_count > 0` → melee single-target
- [ ] Test: Fortress Defender with 0 blocked enemies attacks ranged AoE; when enemy enters tile and is blocked, switches to melee

---

## Unresolved / Needs Further Research

1. **Firewhistle** — no data on her exact skills or release date. Check if she's global-released.
2. **Blocking engagement distance** — confirmed enemies are blocked when they step onto the same tile. Need to verify: can a melee operator "reach out" to grab an enemy in an adjacent tile, or strictly same-tile only?
3. **S1 SP rank values** — the 22 SP cost / 13 initial SP above are at M3. The rank 7 (max non-mastery) values differ. Confirm which rank the sim should target for testing.
4. **Elysium's blocking behavior during skill** — assume same as Myrtle (cannot block), but not explicitly verified from wiki text.

---

*Sources: [Terra Wiki - Myrtle](https://arknights.wiki.gg/wiki/Myrtle) | [Terra Wiki - Defender](https://arknights.wiki.gg/wiki/Defender) | [Terra Wiki - Fortress Defender Category](https://arknights.wiki.gg/wiki/Category:Fortress_Defender) | [Terra Wiki - Block](https://arknights.wiki.gg/wiki/Attribute/Block) | [Fandom - Block](https://arknights.fandom.com/wiki/Attribute/Block)*

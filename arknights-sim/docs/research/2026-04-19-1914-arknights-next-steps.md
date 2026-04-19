# Arknights Sim — Research & Action Plan
**Date:** 2026-04-19 19:14  
**State at time of research:** P1–P5 complete, 108 tests green  
**Researcher:** sonnet-0419a (Claude Sonnet 4.6)

---

## 1. Vanguard Subclass Mechanics

### 1.1 Charger Vanguard (Fang, Vigna, Plume, Grani, Bagpipe, Reed, Wild Mane)

**Exact class trait:**  
> "Obtain 1 DP after this unit defeats an enemy; Refunds the original DP Cost when retreated."

- DP is gained on **kill**, not on block.
- With CHG-X Module: improves to **2 DP per defeated enemy** and refunds current (not original) DP cost.
- **Plume** specifically has a passive talent that also generates 1 DP per kill (stacks with trait for 2 DP on kill pre-module).

**Simulation gap:** The project already has `texas_dp_on_kill` hook in the talent registry. This confirms the hook architecture is correct. What is missing is wiring every Charger operator to fire this talent automatically via the class trait — it should not require a per-operator talent tag. The trait is class-level behavior.

### 1.2 Pioneer Vanguard (Texas, Fang (alt), Vigna, Plume)

**Class trait:** "Blocks 2 enemies." (No inherent DP mechanic in the trait.)

DP generation for Pioneers comes exclusively from **skills**:
- `Charge γ / β` family: instantly gains 12 DP on activation. SP cost ~35, SP initial ~20.
- `Sword Rain` (Texas S2): gains 12 DP + deals 170% ATK Arts damage x2 to nearby enemies + 3s Stun.

**Texas talent "Tactical Delivery":**
- E1: Gains 1 extra DP when Texas is in the squad (passive at battle start, not per kill).
- E2: Gains 2 extra DP when Texas is in the squad.

The existing `texas_dp_on_kill` in the simulator is **incorrect** — it should be `texas_dp_at_deploy` (a one-time flat bonus at battle start). This is a correctness bug.

### 1.3 Tactician Vanguard (Beanstalk, Blacknight, Mitm, Muelsyse, Vigil)

**Class trait:** "Can designate a Tactical Point within range; ATK increased to 150% when attacking enemies blocked by Reinforcements." (No inherent passive DP accumulation.)

DP generation is skill-based only:
- **Beanstalk S1 "Sentinel Command":** activates to gain 8 DP instantly (SP ~30–40).
- **Beanstalk S2 "Everyone Together!":** generates 12 DP over 15 seconds.
- **Vigil S1 "Packleader's Call":** auto-charges to generate 7 DP + summon wolf shadow each cycle.
- **Vigil S2 "Packleader's Gift":** auto-charges to generate 2 DP per charge; 1 additional DP if Wolfpack kills target.
- **Vigil S3 "Packleader's Dignity":** generates 12 DP over 15 seconds.
- **Muelsyse:** DP via skills; talent spawns a free Reinforcement (no DP cost, no unit limit).

**No passive DP accumulation exists for Tacticians** — their DP advantage comes from the Reinforcement (free blocker), freeing DP that would be spent on blockers.

### 1.4 Standard Bearer Vanguard (Myrtle, Elysium, Saileach, Wanqing)

**Class trait:** "Cannot block enemies during the skill duration."

DP generation is highest among Vanguards, entirely through skills:

| Operator | Skill | DP Gained | Duration | SP Cost (max) | Notes |
|----------|-------|-----------|----------|----------------|-------|
| Myrtle | Support β (S1) | 14 DP | 8s | 22 | Stops attacking; ~1.75 DP/s |
| Myrtle | Healing Wings (S2) | 16 DP | 16s | 24 | Stops attacking + heals ally; ~1.0 DP/s |
| Elysium | Support γ (S1) | 18 DP | 8s | ~20 | ~2.25 DP/s |
| Elysium | Monitor (S2) | 20 DP | 15s | ~24 | ~1.33 DP/s |

**Myrtle talent "Glistening" (E2):** All Vanguard operators recover **25 HP/second** while Myrtle is deployed (28 HP/s at Potential 5; up to 30 HP/s with module).

**Implementation note for Standard Bearer:** During skill activation, operators of this class must: (a) stop attacking, (b) stop blocking, and (c) accumulate DP at a linear rate over the skill duration. The DP is distributed evenly over the duration — it is NOT a lump sum at the end. This requires a `dp_per_tick` field on the skill while active.

---

## 2. Known Correctness Issues in Arknights ECS Simulators

Research found no directly comparable Python ECS-style Arknights battle simulator on GitHub (the closest, Wirowo/ArknightsBattleSimulator, uses mitmproxy to replay actual game traffic — not an independent ECS implementation). The christwsy-zz/Arknights-Simulation project is agent-routing only, not a combat sim.

**Based on game formula research and common sim patterns, identified correctness risks:**

### 2.1 ASPD Formula
The correct formula (confirmed via arknights.wiki.gg) is:

```
effective_interval = (100 / (100 + aspd_sum)) × (base_interval + flat_modifier)
```

Where:
- `aspd_sum` = sum of all ASPD percentage modifiers (additive, capped to [20, 600] total ASPD)
- `flat_modifier` = flat interval modifier (max one active per unit at a time)
- Base ASPD is 100; effective ASPD = 100 + aspd_sum

**Correctness check for this simulator:** Verify that ASPD caps are enforced on the *total ASPD value* (20–600), not on the modifier sum. The cap applies before the formula.

### 2.2 ATK Buff Pipeline
Confirmed correct formula from wiki:

```
atk_final = FLOOR(FLOOR(atk_base × atk_stage) × (1 + sum_of_atk_plus_pct)) + atk_ex
# then multiplicative debuffs:
atk_after_debuffs = FLOOR(atk_final × product_of(1 - debuff_i))
```

**Risk:** The `FLOOR` operations must occur in the right order. If the simulator uses a single float and floors only at damage application, small rounding differences will accumulate.

### 2.3 Physical Damage Minimum Floor
Confirmed: **minimum 5% of attacker's ATK** before independent percentage-based modifiers (FRAGILE, etc.) apply. This is pre-DEF, not post-DEF — i.e., the floor is `ATK × 0.05`, then FRAGILE multiplies on top.

Phrased precisely: `damage = max(ATK × multiplier - DEF, ATK × 0.05)`, then apply FRAGILE.

### 2.4 Texas DP Talent (Bug Confirmed)
As noted above: Texas's talent gives **flat DP at battle start** (1 or 2 DP on deploy to squad), NOT a DP on kill. The existing `texas_dp_on_kill` tag is mechanically wrong. It should be `texas_dp_at_deploy` and fire once when the battle initializes with Texas in the squad.

### 2.5 Charger Trait Missing Class-Level Dispatch
The DP-on-kill for Chargers (Fang, Vigna, Plume, etc.) is a **class trait**, not an operator-specific talent. Generated operators from akgd data won't automatically have a talent tag for this. The `spawn_system.py` or character factory should check `subclass == "Charger"` and auto-attach a `charger_dp_on_kill` talent when creating those operators.

---

## 3. Stage JSON Format — Path Fix Verification

### 3.1 Confirmed: `Obt/Main` → `obt/main` fix is correct

From live query of `yuanyan3060/ArknightsGameResource/main/gamedata/excel/stage_table.json`:

```
stageId: 'main_00-01', levelId: 'Obt/Main/level_main_00-01'
stageId: 'main_00-02', levelId: 'Obt/Main/level_main_00-02'
stageId: 'main_00-03', levelId: 'Obt/Main/level_main_00-03'
```

The `levelId` field in `stage_table.json` uses **mixed case** (`Obt/Main`), but the actual file path in the Kengxxiao/ArknightsGameData repository is **all lowercase**: `zh_CN/gamedata/levels/obt/main/level_main_00-01.json`.

**Correct path construction in `gen_stages.py`:**
```python
level_id = stage["levelId"].lower()  # "obt/main/level_main_00-01"
file_path = f"zh_CN/gamedata/levels/{level_id}.json"
```

### 3.2 Other Path Quirks

**`#f#` suffix stages:** Many stages have a `#f#` variant (e.g., `main_00-01#f#`) with the same `levelId`. These are the "challenge mode" (hard mode) versions of stages using the same map layout. `gen_stages.py` should deduplicate by `levelId`, not by `stageId`, to avoid generating duplicate YAML files for the same map.

**obt subfolders confirmed (all lowercase):**
```
obt/campaign, obt/crisis/v2, obt/guide, obt/hard, obt/legion,
obt/main, obt/memory, obt/promote, obt/recalrune, obt/roguelike,
obt/rune, obt/sandbox/sandbox_1, obt/training, obt/weekly
```

For main story stages (main_00 through main_13+), the path is always `obt/main/`.

### 3.3 Level JSON Internal Structure (confirmed from `level_main_00-01.json`)

Key fields for `gen_stages.py`:

```json
{
  "levelId": "Obt/Main/level_main_00-01",
  "mapData": {
    "map": [[tile_index, ...], ...],      // 2D grid, row-major, row 0 = top
    "tiles": [                             // tile definitions
      {
        "tileKey": "tile_road",            // "tile_road", "tile_start", "tile_end", "tile_forbidden", "tile_wall"
        "heightType": "LOWLAND",           // "LOWLAND" or "HIGHLAND"
        "buildableType": "MELEE",          // "NONE", "MELEE", "RANGED"
        "passableMask": "ALL"              // "ALL" or "FLY_ONLY"
      }
    ]
  },
  "routes": [
    {
      "motionMode": "WALK",
      "startPosition": {"row": 5, "col": 0},
      "endPosition": {"row": 5, "col": 8},
      "checkpoints": [
        {"type": "MOVE", "time": 0, "position": {"row": 5, "col": 3}},
        {"type": "WAIT_FOR_SECONDS", "time": 2.0, "position": {"row": 5, "col": 3}},
        ...
      ]
    }
  ],
  "waves": [
    {
      "preDelay": 5.0,
      "fragments": [
        {
          "preDelay": 0.0,
          "actions": [
            {
              "actionType": "SPAWN",
              "key": "enemy_1001_duckmi",
              "count": 1,
              "preDelay": 0.0,
              "interval": 2.0,
              "routeIndex": 0
            }
          ]
        }
      ]
    }
  ]
}
```

**Tile key → sim type mapping:**
| `tileKey` | Sim tile type |
|-----------|---------------|
| `tile_road` | `ground` |
| `tile_start` | `spawn` |
| `tile_end` | `goal` |
| `tile_forbidden` | `wall` (impassable) |
| `tile_wall` | `wall` |
| `buildableType: MELEE` | `deployment_melee` |
| `buildableType: RANGED` | `deployment_ranged` |

Note: A tile can be both `tile_road` AND `buildableType: MELEE` — the deployment flag takes precedence for the YAML type.

---

## 4. Concrete Action Plan — Priority Order for Highest 1:1 Fidelity

### P6.1 — Fix Texas DP Talent (bug, 30 min)
**File:** `data/characters/texas.py` (or wherever Texas is defined — likely in `generated/` with a curated override)

Change `behavior_tag="texas_dp_on_kill"` to `behavior_tag="texas_dp_at_deploy"` and add a `fire_on_deploy` hook to `talent_registry.py`. Fire it from battle initialization for every operator in the squad.

### P6.2 — Add Charger Class Trait Auto-Wire (correctness, 1h)
**File:** `data/characters/registry.py` or a new `data/characters/charger_trait.py`

When a Charger-subclass operator is instantiated, auto-attach a `charger_dp_on_kill` talent. Add this to the `on_kill` hook: if operator is Charger subclass → gain 1 DP (2 with CHG-X module if tracking modules). Since akgd-generated data includes `subclass` field, this can be done at registry load time.

### P6.3 — Standard Bearer Skill DP Drip (correctness, 2h)
**File:** `core/systems/skill_system.py`, `core/state/unit_state.py`

Add `dp_per_second` field to skill definition. During skill active ticks, accumulate DP at this rate. Also enforce: operator stops attacking and loses blocking capacity during skill duration.

**Myrtle numbers to verify:**
- S1: 14 DP over 8s = 1.75 DP/s
- S2: 16 DP over 16s = 1.0 DP/s

### P6.4 — gen_stages.py for 251 Main Story Stages (highest value, 4h)
**File:** new `tools/gen_stages.py`

Steps:
1. Load `stage_table.json` from ArknightsGameData.
2. Filter for `stageId` matching `main_\d\d-\d\d` (exclude `#f#` challenge variants — deduplicate by `levelId`).
3. For each stage, compute `level_path = f"zh_CN/gamedata/levels/{stage['levelId'].lower()}.json"`.
4. Parse level JSON: extract `mapData` (tiles+grid), `routes`, `waves`.
5. Convert tile grid to YAML format: determine `type` from `buildableType` + `tileKey`, `height` from `heightType`.
6. Convert routes to path arrays (extract `checkpoints` of type `MOVE`, ordered by position).
7. Convert waves to `enemies` array with `id`, `count`, `interval`, `routeIndex`.
8. Write to `data/stages/main_XX-YY.yaml`.

Output: ~251 YAML stage files replacing the current 3 hand-authored ones.

### P6.5 — Fortress Defender Subclass Trait (correctness, 2h)
**Class:** Ashlock, Firewhistle, Horn  
**Trait:** "When not blocking enemies, prioritizes dealing ranged AoE Physical damage."

Implementation: When a Fortress Defender's `block_count` is 0 (no enemies in melee range being blocked), switch attack mode to long-range AoE with physical damage. When they resume blocking, revert to standard melee attacks. The FOR-X Module adds +10% ATK when attacking blocked enemies, but this is optional.

### P6.6 — Besieger Sniper (note: NOT a Caster subclass)
The task description mentions "Besieger caster" — this is a **Sniper** subclass, not Caster. Clarified:

**Besieger Sniper trait:** "Attacks the heaviest enemy first." (highest weight priority)

Current targeting system uses `path_progress`. Besieger needs a weight-priority targeting mode. Implementation: add `target_priority: "heaviest"` field to operator definition; `targeting_system.py` checks this flag.

**Operators:** Erato, Ju, Rosa, Toddifons, Totter, Typhon.

### P6.7 — Liskarm + Exusiai Wired to Generated Base Stats (cleanup, 1h)
**Files:** `data/characters/liskarm.py`, `data/characters/exusiai.py`

Currently these use hand-coded stats. Wire them to pull base stats from `generated/liskarm.py` and `generated/exusiai.py` while keeping the skill/talent overrides. Pattern: call the generated `make_liskarm()` as a base, then patch skills/talents on top.

---

## 5. ASPD Formula Verification Checklist

Current implementation should match exactly:

```python
ASPD_MIN = 20
ASPD_MAX = 600

def compute_interval(base_interval: float, aspd_mods: list[int], flat_mod: float = 0.0) -> float:
    total_aspd = max(ASPD_MIN, min(ASPD_MAX, 100 + sum(aspd_mods)))
    return (100 / total_aspd) * (base_interval + flat_mod)
```

Key: cap on `total_aspd` value (100 + sum), NOT on the sum of mods. Only one flat modifier may be active at a time.

---

## 6. Damage Formula Checklist

```python
# Physical damage
raw = atk * multiplier
dmg = max(raw - def_, atk * 0.05)   # 5% floor of ATK, not of raw
dmg = dmg * fragile_multiplier       # FRAGILE applied after floor

# Arts damage  
dmg = atk * multiplier * (1 - res / 100)
# Note: no DEF reduction, no minimum floor for Arts (floor is 0)

# ATK calculation (with stacking)
atk = floor(floor(atk_base * atk_stage_mult) * (1 + sum_atk_pct_buffs)) + atk_additive
atk_final = floor(atk * product_of(1 - debuff_pct_i))
```

---

## Summary Table

| Item | Type | Priority | Estimated Effort |
|------|------|----------|-----------------|
| Fix Texas DP talent (on-kill → on-deploy) | Bug | CRITICAL | 30 min |
| Charger class trait auto-wire | Correctness | HIGH | 1h |
| Standard Bearer DP drip + stop-attack/block | Correctness | HIGH | 2h |
| gen_stages.py — 251 main story stages | Feature | HIGH | 4h |
| Fortress Defender ranged-AoE-when-not-blocking | Feature | MEDIUM | 2h |
| Besieger Sniper weight-priority targeting | Feature | MEDIUM | 1.5h |
| Liskarm + Exusiai wired to generated stats | Cleanup | LOW | 1h |
| ASPD cap enforcement audit | Audit | LOW | 30 min |

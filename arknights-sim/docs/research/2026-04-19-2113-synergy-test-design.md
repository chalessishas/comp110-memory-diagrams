# Multi-Operator Synergy Test Design
**Date:** 2026-04-19  
**Author:** Code Analysis  
**Status:** Proposal for Implementation  

---

## Executive Summary

Current test coverage (51/51 archetypes, 941 tests) validates **single-operator behavior** in isolation. While this ensures archetype mechanics are correct, it does **not detect**:

- **Buff propagation chains** — when operator A buffs B, does B's damage graph correctly reflect it?
- **Healer priority conflicts** — do multiple healers resolve correctly when multiple injured allies exist?
- **Skill interaction timing** — when two AUTO_TIME skills fire in the same tick, does order matter?
- **DP generation with multi-unit economies** — do vanguard DP drip skills interact correctly with spawning?

The ECS architecture (targeting → combat → skill → talent) processes 1 tick = 1 world state transition. **Multi-operator tests exercise the full tick loop**, catching bugs that unit tests cannot because they:
- Invoke the complete targeting → combat → buff application pipeline
- Validate state mutations across 3+ operators in parallel
- Test interaction ordering (which operator attacks first? which healer is chosen?)

---

## Architecture Analysis

### Targeting System (lines 1-80 of `targeting_system.py`)

**Priority Stack:**
1. Blocked units (defender + melee guard priority)
2. Highest aggression (deployment time + path progress)
3. Closest to destination

**Key Detail:** Healer targeting is special — targets the **most-injured alive ally** with `min(hp/max_hp)`:
```python
if op.attack_type == AttackType.HEAL:
    candidates = [u for u in world.allies() if u.alive and u.hp < u.max_hp]
    return min(candidates, key=lambda u: u.hp / u.max_hp)
```

**Insight:** When 2+ healers are deployed, both compute the same target. No conflict logic = both may heal the same target in one tick. **Multi-healer test must validate this behavior is correct.**

### Combat System (lines 1-60 of `combat_system.py`)

**Attack Loop:**
1. For each unit: decrement `atk_cd`
2. When `atk_cd <= 0`: get target (via targeting system)
3. Apply damage/heal
4. Fire `on_attack_hit` talent callbacks
5. Reset `atk_cd` to `atk_interval`

**Multi-Target Support:**
- Multi-target heal: `_apply_multi_heal(world, u, multi_targets)`
- Ranged AoE: `_apply_fortress_ranged(world, u, multi_targets)`

**Insight:** Buff effects (via talents' `on_attack_hit`) modify subsequent operators' effective stats **in the same tick if processing order aligns**. This is where **buff propagation timing bugs** hide.

### Test Pattern (from `test_v2_stage_main00.py`)

```python
def test_main_00_01_clears_with_silverash_liskarm():
    _, world = load_and_build(_stage_path("main_00-01"))
    sa = make_silverash()
    lk = make_liskarm()
    _place(world, sa, (3.0, 3.0))
    _place(world, lk, (1.0, 2.0))
    result = world.run(max_seconds=180.0)
    assert result == "win"
```

**Boilerplate:** Load stage YAML → place operators → run → assert.  
**Opportunity:** Stage tests run full ECS; unit tests do not. This is our test seam.

---

## Key Operator Behaviors Identified

### Buff/Aura Operators

**Pallas (GUARD_INSTRUCTOR):**
- **Talent "Battle Inspiration":** After each attack that deals damage, grant **all deployed allies in attack range** +80 flat ATK for 5s. Refreshes (not stacks) if already present.
- **Range:** 3×3 forward cone (0–2 tiles ahead, ±1 row)
- **Attack Type:** Physical (melee)
- **Chain Interaction:** If Pallas attacks → buffs nearby ally → that ally immediately attacks in same tick, does the ally use the +80 ATK?

**Bagpipe (VANGUARD_PIONEER):**
- **Talent "Glorious March":** While deployed, all other Vanguards gain **+25% ATK** (short-lived buff, refreshed every tick via `on_tick`).
- **S3 "Last Wish":** +200% ATK for 40s; attacks apply 50% SLOW to target.
- **Chain Interaction:** If Bagpipe S3 is active and another Vanguard is deployed, does that vanguard's attacks benefit from both the talent (+25%) and being within range of any other buff?

**Angelina (SUPPORTER_DECEL):**
- **Talent "Thoughtful":** Attacks inflict 30% SLOW for 0.8s.
- **S3 "All for One":** Grants **all deployed allies** +50% ATK and +25 ASPD for 40s (global aura, not range-gated).
- **Chain Interaction:** When S3 fires at t=10s, do allies who just deployed benefit immediately? What if an ally dies and redeploys while S3 is active?

### Healer/Shield Operators

**Shining (MEDIC_ST):**
- **Talent "Illuminate":** When healing an ally, grant that ally a **shield worth 15% of Shining's ATK** for 10s. Shields refresh (amount + duration reset), not stack.
- **S2 "Faith":** **Instant** shield worth 300% ATK on the most-injured ally. 30s duration. `sp_cost=3`, triggered by `AUTO_ATTACK`.
- **Critical Detail:** S2 is instant (duration=0), fired on SP full. Must correctly identify "most-injured ally" in a multi-operator world.
- **Chain Interaction:** If Shining S2 fires and shields ally A, then 1s later ally A takes damage, does the shield absorb it correctly? If two injured allies exist, which one is chosen?

### Vanguard/DP Generation

**Courier (VANGUARD_TACTICIAN):**
- **No passive DP generation.** DP via skills only.
- **S1 "Tactical Formation I":** **Instant** +8 DP. `sp_cost=25`, `initial_sp=10`, AUTO_TIME, instant.
- **S2 "Support Order":** Drips 12 DP over 15s (0.8 DP/s). `sp_cost=35`. Block reduced to 0 during skill.
- **Chain Interaction:** If Courier deploys with `initial_sp=10`, S1 fires immediately (at ~t=0.4s?). Does this DP come in before the first enemy spawns? Multi-vanguard test must validate DP timing in spawn wave.

### Defender/Control

**Blemishine (DEFENDER_PROTECTOR):**
- **Trait:** When blocking enemies at capacity (`blocking >= block`), gain **+50% DEF** (conditional buff, checked every tick).
- **Talent "Aegis" (E2):** When blocking at capacity **AND HP > 50%**, gain additional **+30% DEF**. Both stack.
- **S2 "Iron Aegis":** **MANUAL.** +40% ATK, +60% DEF for 25s. `sp_cost=45`, `initial_sp=25`.
- **Block:** 3 (can hold 3 enemies)
- **Chain Interaction:** When Blemishine blocks 3 enemies AND S2 is active, does DEF stack correctly (+50% trait + +30% talent + +60% skill)? If an enemy dies (count drops to 2), does the trait buff correctly expire?

---

## Multi-Operator Synergy Test Scenarios

### **Test 1: Pallas + Shining — Buff Propagation & Healer Priority**

**Operator Placement:**
- **Pallas** at (3, 1) — front-line Guard with melee range (3×3 cone)
- **Shining** at (5, 1) — back-line Medic (ranged heal, range=[1-3 dx])

**World Setup:**
- Use **stage main_00-01** (simple enemy path, low enemy count)
- Spawn **3-4 weak enemies** in a staggered wave
- Set Pallas S2 skill to **OFF** (use base physical attacks)
- Set Shining skill to **S2** (auto-cast shield on most-injured)

**Expected Flow:**
1. **t≈0.5-1.0s:** First enemy reaches Pallas, Pallas attacks (+737 ATK base)
2. **t≈1.05s (Pallas atk_interval):** Pallas hits again → talent fires → Shining in range gains +80 ATK buff (stacks with base ~950 ATK)
3. **Shining auto-heals** when Pallas HP drops below max (or other ally is injured)
4. **S2 "Faith" trigger:** When Shining SP fills, S2 fires instantly, shields **most-injured ally at that moment**

**Assertions to Validate:**
```python
# Assertion 1: Pallas damage before vs after first hit
assert world.units[enemy_idx].hp > 0, "Enemy survives at least one hit"

# Assertion 2: Shining's effective ATK in second attack includes +80 flat from Pallas
# Check via logs or by verifying damage output
# If Shining heals an enemy: expected_heal = int(effective_atk * heal_multiplier)
# where effective_atk = 950 + 80 (from buff) = 1030

# Assertion 3: Shield is applied to correct target (most injured, not Pallas)
shining_shields = [s for s in world.units if s.name == "Shining"][0].statuses
assert any(s.source_tag == "shining_s2_shield" for s in shining_shields), \
    "S2 shield was applied to target"

# Assertion 4: No operator dies (sufficient healing + tanking)
assert all(u.alive for u in world.allies()), "All operators survive"
```

**Why This Catches Bugs:**
- **Buff timing:** If Pallas buff is not correctly applied to Shining before Shining's next attack in the same tick, Shining's damage will be lower.
- **Healer logic:** If Shining's S2 targeting logic fails (picks wrong ally), the wrong unit gets the shield.
- **State propagation:** Full tick loop exercises buff application → damage → heal in sequence.

---

### **Test 2: Angelina S3 + Bagpipe + Courier — Global Buff Aura & DP Generation Chain**

**Operator Placement:**
- **Courier** at (1, 1) — early vanguard, front-left
- **Bagpipe** at (2, 1) — late vanguard, front-center
- **Angelina** at (5, 2) — back-right caster (global aura range)

**World Setup:**
- Use **stage main_00-01** (simple, predictable spawns)
- Stage starts with **20 DP**
- Pre-arm Angelina S3 to **fire at t≈2-3s** (set sp close to sp_cost)
- Courier uses **S1** (+8 DP instant)

**Expected Flow:**
1. **t≈0s:** Courier deploys (cost=12, remaining DP=8), Bagpipe deploys (cost=12, remaining DP=-4 = wait for DP)
2. **t≈1-2s:** Courier S1 fires → +8 DP (total=8), Bagpipe can now deploy (cost=12, remaining DP=-4)
3. **t≈3s:** Angelina S3 fires → all deployed allies (+50% ATK, +25 ASPD for 40s)
4. **t≈3.5s+:** Both vanguards benefit from Angelina's aura; subsequent attacks have +50% ATK
5. **t≈5s onward:** Bagpipe S3 auto-fires (initially sp_cost=35, but gains SP from AUTO_TIME) → Bagpipe ATK = base + Angelina aura (+50%) + S3 (+200%)

**Assertions to Validate:**
```python
# Assertion 1: DP generation via Courier S1
assert world.global_state.dp >= 8, "Courier S1 generated +8 DP"

# Assertion 2: Bagpipe deployed after DP recovered
bagpipe_units = [u for u in world.units if u.name == "Bagpipe"]
assert len(bagpipe_units) > 0, "Bagpipe is deployed"
assert bagpipe_units[0].deployed, "Bagpipe deployed flag is True"

# Assertion 3: Angelina S3 aura applied to both vanguards
bagpipe = [u for u in world.units if u.name == "Bagpipe"][0]
courier = [u for u in world.units if u.name == "Courier"][0]
assert any(b.source_tag == "angelina_s3_aura" for b in bagpipe.buffs), \
    "Bagpipe has Angelina S3 aura buff"
assert any(b.source_tag == "angelina_s3_aura" for b in courier.buffs), \
    "Courier has Angelina S3 aura buff"

# Assertion 4: Vanguard attack output includes aura bonus
# Simulated: after S3 fires, measure next attack damage
# expected_damage_with_aura = int(base_atk * (1 + 0.50)) * ... [other modifiers]

# Assertion 5: Stage clears with 2+ lives remaining
assert world.global_state.lives > 1, f"Lives remaining: {world.global_state.lives}, no narrow wins"
```

**Why This Catches Bugs:**
- **Global aura buffing:** If Angelina's S3 doesn't correctly apply to all deployed allies, vanguard damage will tank.
- **DP race condition:** If Courier S1 DP is spent before Bagpipe can deploy, the test will catch under-timing.
- **Skill interaction timing:** Angelina S3 duration (40s) + Bagpipe S3 auto-trigger must not conflict. If S3 buffs expire mid-battle, surviving should get harder.
- **Full economy loop:** Tests the DP → deployment → skill → buff chain.

---

### **Test 3: Blemishine + Shining — Defender Block Scaling & Multi-Healer Conflict**

**Operator Placement:**
- **Blemishine** at (2, 1) — heavy defender, melee (block=3)
- **Shining** at (4, 1) — medic healer, ranged

**World Setup:**
- Use **stage main_00-01**
- **Spawn 4-5 weak enemies in quick succession** → Blemishine blocks at capacity
- No other allies (force Shining to choose between Blemishine and... only Blemishine)

**Expected Flow:**
1. **t≈1s:** First 2 enemies reach Blemishine, she blocks them. No buff yet (only 2 < 3 capacity).
2. **t≈1.5s:** Third enemy blocked → **blocking count = 3 = capacity** → trait activates (+50% DEF)
3. **Blemishine HP drops** (multiple enemies hitting her) → Shining auto-heals
4. **t≈2s:** Blemishine HP > 50% + blocking=3 → talent "Aegis" activates (+30% more DEF)
5. **S2 activation (manual, but we'll auto-set sp to near cost):** Once triggered, +60% DEF stacks with trait+talent

**Assertions to Validate:**
```python
# Assertion 1: Block logic — when exactly does trait DEF buff activate?
blemishine = [u for u in world.units if u.name == "Blemishine"][0]
enemies_blocked_by = [e for e in world.enemies() if blemishine.unit_id in e.blocked_by_unit_ids]
blocking_count = len(enemies_blocked_by)
assert blocking_count <= blemishine.block, f"Blocked count {blocking_count} within capacity {blemishine.block}"

# Assertion 2: Trait DEF buff is active when at capacity
if blocking_count >= blemishine.block:
    assert any(b.source_tag == "blemsh_trait_def" for b in blemishine.buffs), \
        "Trait +50% DEF is active when blocking at capacity"

# Assertion 3: Talent DEF buff is active when at capacity AND HP > 50%
hp_above_half = blemishine.hp > blemishine.max_hp * 0.5
if blocking_count >= blemishine.block and hp_above_half:
    assert any(b.source_tag == "blemsh_talent_def" for b in blemishine.buffs), \
        "Talent +30% DEF is active when at capacity and HP > 50%"

# Assertion 4: Effective DEF is the sum of all buffs
effective_def = blemishine.effective_def
expected_def = blemishine.def_base
for b in blemishine.buffs:
    if b.axis == BuffAxis.DEF and b.stack == BuffStack.RATIO:
        expected_def = int(expected_def * (1.0 + b.value))
assert effective_def >= expected_def - 5, \
    f"Effective DEF {effective_def} >= expected {expected_def} (within rounding)"

# Assertion 5: Shining healing is working (not wasting heals when Blemishine is healthy)
shining = [u for u in world.units if u.name == "Shining"][0]
healing_done = world.global_state.total_healing_done
assert healing_done > 0, f"Shining did healing {healing_done} > 0"

# Assertion 6: Stage clears without defender death
assert blemishine.alive, "Blemishine survived the encounter"
```

**Why This Catches Bugs:**
- **Conditional buff logic:** Trait + talent are state-dependent (block count, HP ratio). Multi-enemy spawn tests this every tick.
- **Multi-buff stacking:** If DEF buffs don't compose correctly (ratio vs flat), effective DEF calculation breaks.
- **Healer under load:** Shining must keep Blemishine alive while she tanks 3+ enemies. If healing is delayed or targeted wrong, Blemishine dies.
- **Buff expiration:** When an enemy dies (block count drops to 2), the trait buff should expire immediately. Test validates on_tick logic.

---

### **Test 4: Pallas + Bagpipe + Angelina (Triple Buff Aura) — Chaining Multiplier Effects**

**Operator Placement:**
- **Pallas** at (2, 1) — attack range (3×3 cone), within Angelina aura
- **Bagpipe** at (3, 1) — adjacent to Pallas, vanguard
- **Angelina** at (5, 2) — global aura range

**World Setup:**
- Use **stage main_00-02 or higher** (more enemies, longer battle)
- Spawn **6-8 enemies in 2-3 waves**
- Pre-fill all operator SP to near max (simulate early-battle)

**Expected Flow:**
1. **t≈0-1s:** Pallas attacks first (fast melee), triggers Battle Inspiration → Bagpipe in range gets +80 ATK
2. **Bagpipe attacks** (now with +80 ATK from Pallas + base vanguard stats)
3. **t≈2-3s:** Angelina S3 fires → all allies (+50% ATK, +25 ASPD)
4. **Now Pallas's attacks to Bagpipe happen faster** (ASPD +25) and hit harder
5. **Pallas inspiration refreshes every hit** → Bagpipe sustains the +80 ATK buff
6. **Effective ATK of Bagpipe** = base + Angelina (+50%) + Pallas talent (+80 flat per hit within range)

**Key Insight:** This isn't just additive. With Angelina's +50% ATK and ASPD+25:
- Base ATK=300, Angelina aura → 300 * 1.5 = 450
- + Pallas inspiration (flat, applied after ratio) → 450 + 80 = 530
- Damage output scales 2-3x due to ASPD increase

**Assertions to Validate:**
```python
# Assertion 1: All three operators deployed
assert len([u for u in world.units if u.faction == Faction.ALLY and u.alive]) >= 3, \
    "All 3 operators deployed"

# Assertion 2: Pallas inspiration buff is on Bagpipe
bagpipe = [u for u in world.units if u.name == "Bagpipe"][0]
has_inspiration = any(b.source_tag == "pallas_inspire_atk" for b in bagpipe.buffs)
assert has_inspiration, "Bagpipe has Pallas inspiration buff"

# Assertion 3: Angelina aura is on both Pallas and Bagpipe
for op_name in ["Pallas", "Bagpipe"]:
    op = [u for u in world.units if u.name == op_name][0]
    has_aura = any(b.source_tag == "angelina_s3_aura" for b in op.buffs)
    assert has_aura, f"{op_name} has Angelina S3 aura"

# Assertion 4: Damage from Bagpipe is significantly higher post-aura
# Baseline: first 10s before Angelina S3 → measure cumulative damage
# After S3: next 10s → measure cumulative damage
# assert damage_after_s3 > 1.5 * damage_before_s3, "Damage output increased significantly with aura"

# Assertion 5: Stage clear with 2+ lives
assert world.global_state.lives >= 2, f"Lives: {world.global_state.lives}"
assert world.global_state.enemies_defeated >= 6, f"Enemies defeated: {world.global_state.enemies_defeated}"
```

**Why This Catches Bugs:**
- **Buff composition:** Ratios (Angelina +50%) + flat (Pallas +80) must both apply. If one is dropped, damage tanks.
- **ASPD interaction:** Angelina's ASPD buff changes attack interval. This must re-trigger Pallas inspiration more frequently. If ASPD doesn't affect inspiration refresh rate, the test will show lower damage than expected.
- **Range checking:** Pallas inspiration only applies to in-range allies. If range checks fail, Bagpipe (adjacent) might not receive it.
- **Multi-buff lifetime:** Angelina S3 duration 40s, Pallas inspiration 5s per hit. Do they correctly compose over a long battle?

---

### **Test 5: Shining Dual-Heal + Blemishine Dual-Block — Healer & Tank Scaling**

**Operator Placement:**
- **Blemishine #1** at (2, 1) — left defender (block=3)
- **Blemishine #2** at (2, 3) — right defender (block=3)
- **Shining** at (4, 2) — centered medic (can reach both defenders if range allows)

**World Setup:**
- Use **stage main_00-02 or higher** (multi-lane or branching paths)
- Route enemies such that **some hit Blemishine #1, others hit Blemishine #2**
- Disable Shining skills → base attacks only (test fundamental heal loop)

**Expected Flow:**
1. **t≈1s:** Enemies hit both defenders; both take damage
2. **Shining targeting logic:** Selects "most injured" = lower hp/max_hp ratio
3. **Shining heals that defender** (say, Blemishine #1 at 60% HP)
4. **t≈1.5s:** Blemishine #1 is now higher HP; Blemishine #2 drops to 50% HP
5. **Next Shining heal cycle:** Targets Blemishine #2 (now most injured)
6. **Shining talent "Illuminate":** Each heal applies shield 15% ATK to target for 10s

**Assertions to Validate:**
```python
# Assertion 1: Both defenders are deployed
blemshines = [u for u in world.units if u.name == "Blemishine" and u.deployed]
assert len(blemshines) == 2, f"Both Blemishine deployed, got {len(blemshines)}"

# Assertion 2: Shining correctly identifies and heals the most-injured
# Track HP before and after heal
# shining_target_before = [u for u in world.allies() if u.hp / u.max_hp < others][0]
# After heal: shining_target_after should have higher HP

# Assertion 3: Shields are applied to correct targets (not both, just the one healed)
shield_count = sum(1 for u in blemshines for s in u.statuses if s.source_tag == "shining_illuminate_shield")
assert shield_count > 0, f"Shields applied, count={shield_count}"

# Assertion 4: Shield absorbs damage correctly
# Track total damage taken before shield vs after shield application
# After shield: effective HP should be higher

# Assertion 5: Neither defender dies (sufficient healing to sustain both)
for blem in blemshines:
    assert blem.alive, f"Blemishine at {blem.position} survived"

# Assertion 6: Stage clears
assert world.global_state.lives > 0, f"Lives: {world.global_state.lives}"
```

**Why This Catches Bugs:**
- **Multi-target healer logic:** Shining must prioritize correctly when multiple injured allies exist. If the targeting logic is broken, one defender may starve of healing.
- **Shield mechanics:** Shields must absorb damage before HP. If shield is applied but damage bypasses it, the test fails.
- **Talent proc per heal:** If Illuminate talent doesn't fire on every heal, shields won't accumulate. Test validates talent registry integration.
- **Dual-tank economy:** Two defenders require more healing resources. This test stresses healer output frequency and target selection.

---

## Implementation Checklist

### Files to Create/Modify

1. **Create `tests/test_v2_synergy_multi_operator.py`**
   - Import: `pytest`, `load_and_build`, `Faction`, operators
   - Define `_place()` helper (same as in `test_v2_stage_main00.py`)
   - Implement 5 test functions (one per scenario above)
   - Each test: load stage → place operators → run → assert

2. **Reference Stages**
   - Use **stage main_00-01** (simplest: 1 lane, ~15 enemies total)
   - Use **stage main_00-02** or **main_00-03** (if available: multi-lane or higher difficulty)

3. **Operator Imports** (add to `__init__.py` if missing)
   ```python
   from .pallas import make_pallas
   from .angelina import make_angelina
   from .bagpipe import make_bagpipe
   from .courier import make_courier
   from .blemishine import make_blemishine
   from .shining import make_shining
   ```

### Test Code Template

```python
"""Multi-operator synergy tests — exercises ECS tick loop with 2-3 operators."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from stages.loader import load_and_build
from data.characters import make_pallas, make_shining, make_angelina, \
                            make_bagpipe, make_courier, make_blemishine
from core.types import Faction

STAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "stages")

def _stage_path(name: str) -> str:
    return os.path.join(STAGE_DIR, f"{name}.yaml")

def _place(world, unit, pos):
    """Add an operator directly (bypass DP cost for test simplicity)."""
    unit.deployed = True
    unit.position = pos
    world.add_unit(unit)

# Test 1: Pallas + Shining
def test_synergy_pallas_shining_buff_propagation():
    """Pallas inspiration buff to Shining; Shining S2 shield."""
    _, world = load_and_build(_stage_path("main_00-01"))
    pallas = make_pallas(slot="S2")
    shining = make_shining(slot="S2")
    _place(world, pallas, (3.0, 1.0))
    _place(world, shining, (5.0, 1.0))
    
    result = world.run(max_seconds=180.0)
    assert result == "win", f"Stage should clear with Pallas+Shining, got {result}"
    assert world.global_state.lives > 0, f"Lives remaining: {world.global_state.lives}"
    
    # Verify buffs were applied (check logs or state)
    pallas_unit = [u for u in world.units if u.name == "Pallas"][0]
    assert pallas_unit.alive, "Pallas survived"

# ... (Tests 2-5 follow similar structure)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Risk & Validation Strategy

### What Could Go Wrong?

| Bug Type | Example | Caught By |
|----------|---------|-----------|
| **Buff not applied** | Angelina S3 fires but Bagpipe doesn't get aura | Test 2, 4 |
| **Wrong healer target** | Shining heals full-HP ally instead of injured one | Test 3, 5 |
| **Shield doesn't absorb** | Illuminate shield applied but damage ignores it | Test 3, 5 |
| **DP race** | Bagpipe tries to deploy before Courier S1 generates DP | Test 2 |
| **Buff expiration** | Trait DEF remains after unblocking enemy | Test 3 |
| **ASPD doesn't affect attack frequency** | Angelina ASPD buff applied but attack interval unchanged | Test 4 |
| **Range check broken** | Pallas inspiration goes to out-of-range ally | Test 1, 4 |
| **Talent not firing** | on_attack_hit hook doesn't execute | Test 1, 2, 4, 5 |

### Validation Steps

1. **Run tests locally** → all should pass
2. **Inject known bugs** (e.g., comment out buff application) → tests should fail
3. **Check coverage** → add assertions for critical code paths (buff calc, healer targeting)
4. **Run against main_00-02/03** → confirm tests scale to harder content

---

## Timeline

- **Design Phase (completed):** Identified 5 synergy scenarios, mapped to operator mechanics
- **Implementation Phase:** Write `test_v2_synergy_multi_operator.py` (~200-300 LOC)
- **Integration Phase:** Add to CI/CD pipeline; run alongside 941 existing tests
- **Expansion Phase:** Once validated, extend to 10+ scenarios (3+ operators, elemental interactions, etc.)

---

## Success Criteria

1. ✅ All 5 tests pass with current codebase
2. ✅ Tests fail if buff application logic is removed
3. ✅ Tests fail if healer targeting is broken
4. ✅ Tests fail if shield mechanics are disabled
5. ✅ Coverage: tests exercise targeting → combat → skill → talent in full loop
6. ✅ Documentation: each test has clear assertion comments explaining what's being validated

---

## Conclusion

The ECS architecture's strength is **composability**—buffs, skills, and talents combine predictably. Multi-operator tests validate this at scale. These 5 scenarios are **minimal** but **targeted**—they cover the highest-risk interaction patterns (buff propagation, healer priority, DP economy, conditional tanking, global auras) that single-operator unit tests cannot catch.

**Next Step:** Implement `test_v2_synergy_multi_operator.py` and run against the full test suite to confirm all scenarios pass.

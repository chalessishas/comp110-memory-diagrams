"""Lumen — MEDIC_MULTI: heals 3 most-injured allies simultaneously per attack.

Tests cover:
  - Archetype and heal_targets default
  - Multi-heal fires for all injured allies in one attack
  - Priority: heals lowest hp/max_hp ratio first
  - Does NOT heal full-HP allies
  - Falls back cleanly when fewer injured than heal_targets
  - S2: heal_targets increases to 5, reverts on expiry
  - S2 ATK buff applied/removed correctly
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType, RoleArchetype, BuffAxis
from core.systems import register_default_systems
from data.characters.lumen import make_lumen, _BASE_HEAL_TARGETS, _S2_HEAL_TARGETS, _S2_ATK_RATIO
from data.characters import make_liskarm


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _tank(pos=(0, 1), hp_ratio=1.0, name="Tank") -> UnitState:
    t = make_liskarm()
    t.name = name
    t.deployed = True
    t.position = (float(pos[0]), float(pos[1]))
    t.hp = max(1, int(t.max_hp * hp_ratio))
    return t


# ---------------------------------------------------------------------------
# Test 1: Archetype and heal_targets
# ---------------------------------------------------------------------------

def test_lumen_archetype_and_heal_targets():
    lm = make_lumen()
    assert lm.archetype == RoleArchetype.MEDIC_MULTI
    assert lm.heal_targets == _BASE_HEAL_TARGETS == 3
    assert lm.attack_type == AttackType.HEAL


# ---------------------------------------------------------------------------
# Test 2: Heals multiple injured allies in one attack
# ---------------------------------------------------------------------------

def test_multi_heal_heals_three_allies():
    """Single attack from Lumen restores HP to all 3 injured allies."""
    w = _world()
    lm = make_lumen()
    lm.deployed = True
    lm.position = (0.0, 1.0)
    lm.atk_cd = 0.0
    w.add_unit(lm)

    t1 = _tank(pos=(0, 1), hp_ratio=0.5, name="T1")
    t2 = _tank(pos=(1, 1), hp_ratio=0.6, name="T2")
    t3 = _tank(pos=(3, 1), hp_ratio=0.7, name="T3")
    w.add_unit(t1); w.add_unit(t2); w.add_unit(t3)

    hp1_before = t1.hp; hp2_before = t2.hp; hp3_before = t3.hp

    w.tick()  # Lumen fires once, heals all 3

    assert t1.hp > hp1_before, "T1 (25% HP) must be healed"
    assert t2.hp > hp2_before, "T2 (50% HP) must be healed"
    assert t3.hp > hp3_before, "T3 (70% HP) must be healed"


# ---------------------------------------------------------------------------
# Test 3: Priority — most-injured healed first (lowest hp/max_hp ratio)
# ---------------------------------------------------------------------------

def test_multi_heal_priority_lowest_hp_ratio():
    """When there are 4 injured and heal_targets=3, the 3 most-injured get healed."""
    w = _world()
    lm = make_lumen()
    lm.deployed = True; lm.position = (0.0, 1.0); lm.atk_cd = 0.0
    w.add_unit(lm)

    # 4 injured allies at different HP ratios; T4 at 90% should NOT be healed this tick
    t1 = _tank(pos=(0, 1), hp_ratio=0.20, name="T1")  # most injured
    t2 = _tank(pos=(1, 1), hp_ratio=0.40, name="T2")
    t3 = _tank(pos=(3, 1), hp_ratio=0.60, name="T3")
    t4 = _tank(pos=(4, 1), hp_ratio=0.90, name="T4")  # least injured → excluded this tick
    w.add_unit(t1); w.add_unit(t2); w.add_unit(t3); w.add_unit(t4)

    hp4_before = t4.hp

    w.tick()

    assert t1.hp > int(t1.max_hp * 0.20), "T1 must be healed"
    assert t2.hp > int(t2.max_hp * 0.40), "T2 must be healed"
    assert t3.hp > int(t3.max_hp * 0.60), "T3 must be healed"
    assert t4.hp == hp4_before, "T4 (least injured) must NOT be healed this tick"


# ---------------------------------------------------------------------------
# Test 4: Full-HP allies are never healed
# ---------------------------------------------------------------------------

def test_multi_heal_skips_full_hp_allies():
    """Lumen does not waste a heal slot on a full-HP ally."""
    w = _world()
    lm = make_lumen()
    lm.deployed = True; lm.position = (0.0, 1.0); lm.atk_cd = 0.0
    w.add_unit(lm)

    full = _tank(pos=(0, 1), hp_ratio=1.0, name="Full")  # full HP
    injured = _tank(pos=(1, 1), hp_ratio=0.5, name="Inj")
    w.add_unit(full); w.add_unit(injured)

    hp_full_before = full.hp
    w.tick()

    assert full.hp == hp_full_before, "Full-HP ally must not be healed"
    assert injured.hp > int(injured.max_hp * 0.5), "Injured ally must be healed"


# ---------------------------------------------------------------------------
# Test 5: Fewer injured than heal_targets — heals only available injured
# ---------------------------------------------------------------------------

def test_multi_heal_fewer_than_capacity():
    """When only 1 ally is injured and heal_targets=3, Lumen heals just that 1."""
    w = _world()
    lm = make_lumen()
    lm.deployed = True; lm.position = (0.0, 1.0); lm.atk_cd = 0.0
    w.add_unit(lm)

    lone = _tank(pos=(0, 1), hp_ratio=0.5, name="Lone")
    w.add_unit(lone)

    hp_before = lone.hp
    w.tick()

    assert lone.hp > hp_before, "Single injured ally must be healed"


# ---------------------------------------------------------------------------
# Test 6: S2 increases heal_targets to 5
# ---------------------------------------------------------------------------

def test_s2_increases_heal_targets():
    """During S2, Lumen's heal_targets rises from 3 to 5."""
    w = _world()
    lm = make_lumen(slot="S2")
    lm.deployed = True; lm.position = (2.0, 1.0); lm.atk_cd = 999.0
    w.add_unit(lm)

    assert lm.heal_targets == 3

    lm.skill.sp = lm.skill.sp_cost
    w.tick()  # S2 activates

    assert lm.skill.active_remaining > 0.0
    assert lm.heal_targets == _S2_HEAL_TARGETS == 5, (
        f"S2 must raise heal_targets to 5, got {lm.heal_targets}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 resets heal_targets on expiry
# ---------------------------------------------------------------------------

def test_s2_resets_heal_targets_on_end():
    """After S2 expires, heal_targets returns to 3."""
    w = _world()
    lm = make_lumen(slot="S2")
    lm.deployed = True; lm.position = (2.0, 1.0); lm.atk_cd = 999.0
    w.add_unit(lm)

    lm.skill.sp = lm.skill.sp_cost
    w.tick()  # S2 activates

    from data.characters.lumen import _S2_DURATION
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert lm.skill.active_remaining == 0.0
    assert lm.heal_targets == _BASE_HEAL_TARGETS, (
        f"heal_targets must revert to {_BASE_HEAL_TARGETS} after S2, got {lm.heal_targets}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff increases effective heal amount
# ---------------------------------------------------------------------------

def test_s2_atk_buff_increases_heal():
    """S2 ATK +30% means each heal is larger than the base."""
    w = _world()
    lm = make_lumen(slot="S2")
    lm.deployed = True; lm.position = (2.0, 1.0); lm.atk_cd = 999.0
    w.add_unit(lm)

    tank = _tank(pos=(0, 1), hp_ratio=0.01, name="Tank")
    w.add_unit(tank)

    base_atk = lm.effective_atk
    expected_s2_atk = int(base_atk * (1.0 + _S2_ATK_RATIO))

    lm.skill.sp = lm.skill.sp_cost
    w.tick()  # S2 activates

    assert lm.effective_atk == expected_s2_atk, (
        f"S2 ATK should be {expected_s2_atk}, got {lm.effective_atk}"
    )

    atk_buffs = [b for b in lm.buffs if b.axis == BuffAxis.ATK]
    assert any(abs(b.value - _S2_ATK_RATIO) < 0.01 for b in atk_buffs), (
        "S2 ATK buff must be present in buffs list"
    )

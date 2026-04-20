"""Lumen — MEDIC_MULTI: heals top-3 most-injured allies + S2 Group Recovery (top-5, ATK+30%)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.lumen import (
    make_lumen, _BASE_HEAL_TARGETS, _S2_HEAL_TARGETS, _S2_ATK_RATIO, _S2_DURATION,
)
from data.characters.mountain import make_mountain


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ally(pos=(1, 1), hp=1000, hp_ratio=0.8) -> UnitState:
    """Create a Mountain operator as a stand-in injured ally."""
    op = make_mountain()
    op.deployed = True
    op.position = (float(pos[0]), float(pos[1]))
    op.atk_cd = 999.0
    op.max_hp = hp
    op.hp = int(hp * hp_ratio)
    return op


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_lumen_config():
    lumen = make_lumen()
    assert lumen.archetype == RoleArchetype.MEDIC_MULTI
    assert lumen.heal_targets == _BASE_HEAL_TARGETS
    sk = lumen.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 20


# ---------------------------------------------------------------------------
# Test 2: Heals top-3 most-injured allies (base)
# ---------------------------------------------------------------------------

def test_lumen_heals_top_3():
    """Lumen heals the 3 most-injured allies, leaving the 4th untouched."""
    w = _world()
    lumen = make_lumen()
    lumen.deployed = True; lumen.position = (0.0, 1.0); lumen.atk_cd = 0.0
    lumen.skill = None  # remove skill so auto-trigger doesn't fire
    w.add_unit(lumen)

    # 4 injured allies; ally_d is least injured (highest hp ratio)
    ally_a = _ally(pos=(1, 1), hp=1000, hp_ratio=0.20)  # most injured
    ally_b = _ally(pos=(2, 1), hp=1000, hp_ratio=0.40)
    ally_c = _ally(pos=(3, 1), hp=1000, hp_ratio=0.60)
    ally_d = _ally(pos=(4, 1), hp=1000, hp_ratio=0.80)  # least injured
    for a in [ally_a, ally_b, ally_c, ally_d]:
        w.add_unit(a)

    hp_d_before = ally_d.hp
    w.tick()  # Lumen fires, heals top 3

    assert ally_a.hp > int(ally_a.max_hp * 0.20), "Most-injured ally_a must be healed"
    assert ally_b.hp > int(ally_b.max_hp * 0.40), "2nd-injured ally_b must be healed"
    assert ally_c.hp > int(ally_c.max_hp * 0.60), "3rd-injured ally_c must be healed"
    assert ally_d.hp == hp_d_before, "4th ally (least injured) must NOT be healed"


# ---------------------------------------------------------------------------
# Test 3: Heal amount equals effective_atk
# ---------------------------------------------------------------------------

def test_lumen_heal_amount():
    """Each heal target receives effective_atk HP (no DEF/RES on heals)."""
    w = _world()
    lumen = make_lumen()
    lumen.deployed = True; lumen.position = (0.0, 1.0); lumen.atk_cd = 0.0
    lumen.skill = None
    w.add_unit(lumen)

    ally = _ally(pos=(1, 1), hp=9999, hp_ratio=0.01)
    w.add_unit(ally)

    hp_before = ally.hp
    w.tick()

    healed = ally.hp - hp_before
    assert healed == lumen.effective_atk, (
        f"Heal must equal effective_atk {lumen.effective_atk}; got {healed}"
    )


# ---------------------------------------------------------------------------
# Test 4: S2 increases heal targets to 5
# ---------------------------------------------------------------------------

def test_s2_expands_heal_targets():
    """After S2 fires, Lumen heals 5 allies instead of 3."""
    w = _world()
    lumen = make_lumen("S2")
    lumen.deployed = True; lumen.position = (0.0, 1.0); lumen.atk_cd = 999.0
    w.add_unit(lumen)

    # 5 injured allies
    allies = [_ally(pos=(i, 1), hp=1000, hp_ratio=0.1) for i in range(1, 6)]
    for a in allies:
        w.add_unit(a)

    lumen.skill.sp = float(lumen.skill.sp_cost)
    w.tick()  # S2 fires

    assert lumen.heal_targets == _S2_HEAL_TARGETS, (
        f"S2 must set heal_targets to {_S2_HEAL_TARGETS}; got {lumen.heal_targets}"
    )


# ---------------------------------------------------------------------------
# Test 5: S2 ATK buff
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 must grant ATK +30%."""
    w = _world()
    lumen = make_lumen("S2")
    lumen.deployed = True; lumen.position = (0.0, 1.0); lumen.atk_cd = 999.0
    w.add_unit(lumen)
    ally = _ally(pos=(1, 1))
    w.add_unit(ally)

    base_atk = lumen.effective_atk
    lumen.skill.sp = float(lumen.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1.0 + _S2_ATK_RATIO))
    assert lumen.effective_atk == expected, (
        f"S2 must give ATK {expected}; got {lumen.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 reverts on end
# ---------------------------------------------------------------------------

def test_s2_reverts_on_end():
    """After S2 expires, heal_targets reverts to 3 and ATK returns to base."""
    w = _world()
    lumen = make_lumen("S2")
    lumen.deployed = True; lumen.position = (0.0, 1.0); lumen.atk_cd = 999.0
    w.add_unit(lumen)
    ally = _ally(pos=(1, 1))
    w.add_unit(ally)

    base_atk = lumen.effective_atk
    lumen.skill.sp = float(lumen.skill.sp_cost)
    w.tick()
    assert lumen.heal_targets == _S2_HEAL_TARGETS

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert lumen.heal_targets == _BASE_HEAL_TARGETS, (
        f"heal_targets must revert to {_BASE_HEAL_TARGETS}; got {lumen.heal_targets}"
    )
    assert lumen.effective_atk == base_atk, "ATK must revert after S2"

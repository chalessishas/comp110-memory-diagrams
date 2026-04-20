"""Courier talent "Frontline Supply" — grants 3 DP on deployment.

Tests cover:
  - Talent configured correctly
  - 3 DP granted on add_unit (no ticks needed)
  - DP grant is additive (starts from any DP level)
  - slot=None still has talent (talent independent of skill slot)
  - Non-Courier deploy does NOT grant extra DP
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, Profession, TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.courier import (
    make_courier, _TALENT_TAG, _DP_GRANT,
)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: Talent configured correctly
# ---------------------------------------------------------------------------

def test_courier_talent_configured():
    c = make_courier(slot="S1")
    assert len(c.talents) == 1
    assert c.talents[0].name == "Frontline Supply"
    assert c.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: 3 DP granted immediately on add_unit
# ---------------------------------------------------------------------------

def test_frontline_supply_grants_dp():
    w = _world()
    w.global_state.dp = 0.0
    c = make_courier(slot="S1")
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    assert w.global_state.dp == _DP_GRANT, (
        f"Courier Frontline Supply must grant {_DP_GRANT} DP; got {w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 3: DP grant is additive with existing DP
# ---------------------------------------------------------------------------

def test_frontline_supply_additive():
    w = _world()
    w.global_state.dp = 10.0
    c = make_courier(slot=None)
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    assert w.global_state.dp == 10.0 + _DP_GRANT, (
        f"DP must be 10 + {_DP_GRANT}; got {w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 4: slot=None still has talent
# ---------------------------------------------------------------------------

def test_frontline_supply_no_skill_slot():
    c = make_courier(slot=None)
    assert len(c.talents) == 1
    assert c.talents[0].behavior_tag == _TALENT_TAG

    w = _world()
    w.global_state.dp = 0.0
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)
    assert w.global_state.dp == _DP_GRANT


# ---------------------------------------------------------------------------
# Test 5: A bare ally unit added does NOT grant DP via this talent
# ---------------------------------------------------------------------------

def test_non_courier_no_dp_grant():
    w = _world()
    w.global_state.dp = 0.0

    other = UnitState(
        name="OtherAlly", faction=Faction.ALLY,
        max_hp=1000, atk=100, defence=50, res=0.0,
        atk_interval=1.0, attack_range_melee=True,
        profession=Profession.GUARD, block=1, cost=10,
    )
    other.deployed = True; other.position = (0.0, 1.0)
    w.add_unit(other)

    assert w.global_state.dp == 0.0, (
        f"Non-Courier unit must not grant DP; got {w.global_state.dp}"
    )

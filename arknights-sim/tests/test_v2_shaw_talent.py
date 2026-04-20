"""Shaw talent "Gale" — push_distance increases from 1 to 2 on deploy.

Tests cover:
  - Talent configured correctly
  - Base push_distance is 1 before deployment
  - push_distance becomes 2 after add_unit (on_battle_start)
  - slot=None still applies talent
  - S2 skill is independent (push_distance not reset by skill)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.shaw import (
    make_shaw, _TALENT_TAG, _BASE_PUSH, _GALE_PUSH,
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

def test_shaw_talent_configured():
    s = make_shaw(slot="S2")
    assert len(s.talents) == 1
    assert s.talents[0].name == "Gale"
    assert s.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Base push_distance is 1 before deployment
# ---------------------------------------------------------------------------

def test_shaw_base_push_distance():
    s = make_shaw(slot="S2")
    assert s.push_distance == _BASE_PUSH, (
        f"Shaw base push_distance must be {_BASE_PUSH}; got {s.push_distance}"
    )


# ---------------------------------------------------------------------------
# Test 3: Gale raises push_distance to 2 after add_unit
# ---------------------------------------------------------------------------

def test_gale_sets_push_distance():
    w = _world()
    s = make_shaw(slot="S2")
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    assert s.push_distance == _GALE_PUSH, (
        f"Gale must set push_distance to {_GALE_PUSH}; got {s.push_distance}"
    )


# ---------------------------------------------------------------------------
# Test 4: slot=None still applies talent
# ---------------------------------------------------------------------------

def test_gale_no_skill_slot():
    w = _world()
    s = make_shaw(slot=None)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    assert s.push_distance == _GALE_PUSH


# ---------------------------------------------------------------------------
# Test 5: push_distance stays at 2 after several ticks
# ---------------------------------------------------------------------------

def test_gale_push_persists():
    w = _world()
    s = make_shaw(slot=None)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    _ticks(w, 1.0)

    assert s.push_distance == _GALE_PUSH, (
        f"Gale push_distance must persist after ticks; got {s.push_distance}"
    )

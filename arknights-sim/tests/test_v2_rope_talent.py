"""Rope talent "Shadow Step" — pull distance increases from 1 to 2 on deploy.

Tests cover:
  - Talent configured correctly
  - Base push_distance is _BASE_PULL (1) before deployment
  - push_distance becomes 2 after add_unit
  - slot=None still applies talent
  - push_distance stays 2 after several ticks
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.rope import (
    make_rope, _TALENT_TAG, _BASE_PULL, _TALENT_PULL,
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

def test_rope_talent_configured():
    r = make_rope(slot="S2")
    assert len(r.talents) == 1
    assert r.talents[0].name == "Shadow Step"
    assert r.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Base push_distance is 1 before deployment
# ---------------------------------------------------------------------------

def test_rope_base_push_distance():
    r = make_rope(slot="S2")
    assert r.push_distance == _BASE_PULL, (
        f"Rope base push_distance must be {_BASE_PULL}; got {r.push_distance}"
    )


# ---------------------------------------------------------------------------
# Test 3: Shadow Step raises push_distance to 2 after add_unit
# ---------------------------------------------------------------------------

def test_shadow_step_sets_pull():
    w = _world()
    r = make_rope(slot="S2")
    r.deployed = True; r.position = (0.0, 1.0)
    w.add_unit(r)

    assert r.push_distance == _TALENT_PULL, (
        f"Shadow Step must set push_distance to {_TALENT_PULL}; got {r.push_distance}"
    )


# ---------------------------------------------------------------------------
# Test 4: slot=None still applies talent
# ---------------------------------------------------------------------------

def test_shadow_step_no_skill_slot():
    w = _world()
    r = make_rope(slot=None)
    r.deployed = True; r.position = (0.0, 1.0)
    w.add_unit(r)

    assert r.push_distance == _TALENT_PULL


# ---------------------------------------------------------------------------
# Test 5: push_distance stays at 2 after ticks
# ---------------------------------------------------------------------------

def test_shadow_step_persists():
    w = _world()
    r = make_rope(slot=None)
    r.deployed = True; r.position = (0.0, 1.0)
    w.add_unit(r)

    _ticks(w, 1.0)

    assert r.push_distance == _TALENT_PULL, (
        f"Shadow Step push_distance must persist after ticks; got {r.push_distance}"
    )

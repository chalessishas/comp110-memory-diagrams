"""Erato talent "Precision Strike" — 10% crit chance set on deployment.

Tests cover:
  - Talent configured correctly
  - Default crit_chance is 0 before deployment
  - crit_chance is set to 0.10 after add_unit
  - slot=None still applies talent
  - crit_chance persists after several ticks
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.erato import (
    make_erato, _TALENT_TAG, _CRIT_CHANCE,
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

def test_erato_talent_configured():
    e = make_erato(slot="S1")
    assert len(e.talents) == 1
    assert e.talents[0].name == "Precision Strike"
    assert e.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Default crit_chance is 0 before deployment
# ---------------------------------------------------------------------------

def test_erato_default_crit_chance():
    e = make_erato(slot="S1")
    assert e.crit_chance == 0.0, (
        f"crit_chance must be 0 before deployment; got {e.crit_chance}"
    )


# ---------------------------------------------------------------------------
# Test 3: crit_chance set to 0.10 after add_unit
# ---------------------------------------------------------------------------

def test_precision_strike_sets_crit_chance():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    assert e.crit_chance == _CRIT_CHANCE, (
        f"Precision Strike must set crit_chance to {_CRIT_CHANCE}; got {e.crit_chance}"
    )


# ---------------------------------------------------------------------------
# Test 4: slot=None still applies talent
# ---------------------------------------------------------------------------

def test_precision_strike_no_skill_slot():
    w = _world()
    e = make_erato(slot=None)
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    assert e.crit_chance == _CRIT_CHANCE


# ---------------------------------------------------------------------------
# Test 5: crit_chance persists after ticks
# ---------------------------------------------------------------------------

def test_precision_strike_persists():
    w = _world()
    e = make_erato(slot=None)
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    _ticks(w, 2.0)

    assert e.crit_chance == _CRIT_CHANCE, (
        f"crit_chance must persist after ticks; got {e.crit_chance}"
    )

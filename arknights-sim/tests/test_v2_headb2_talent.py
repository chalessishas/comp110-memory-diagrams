"""headb2 (怒潮凛冬) talent "Shockwave" — splash_radius increases from 1.0 to 1.5.

Tests cover:
  - Talent configured correctly
  - Base splash_radius is 1.0 before deployment
  - splash_radius becomes 1.5 after add_unit
  - slot=None still applies talent
  - splash_atk_multiplier stays at 0.5 (unaffected by talent)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.headb2 import (
    make_headb2, _TALENT_TAG, _BASE_SPLASH_RADIUS, _TALENT_SPLASH_RADIUS,
    _WARD_TAG,
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

def test_headb2_talent_configured():
    h = make_headb2(slot=None)
    assert len(h.talents) == 2
    assert h.talents[0].name == "Shockwave"
    assert h.talents[0].behavior_tag == _TALENT_TAG
    assert h.talents[1].name == "Ward of the Fertile Soil"
    assert h.talents[1].behavior_tag == _WARD_TAG


# ---------------------------------------------------------------------------
# Test 2: Base splash_radius is 1.0 before deployment
# ---------------------------------------------------------------------------

def test_headb2_base_splash_radius():
    h = make_headb2(slot=None)
    assert h.splash_radius == _BASE_SPLASH_RADIUS, (
        f"Base splash_radius must be {_BASE_SPLASH_RADIUS}; got {h.splash_radius}"
    )


# ---------------------------------------------------------------------------
# Test 3: Shockwave sets splash_radius to 1.5 after add_unit
# ---------------------------------------------------------------------------

def test_shockwave_sets_splash_radius():
    w = _world()
    h = make_headb2(slot=None)
    h.deployed = True; h.position = (0.0, 1.0)
    w.add_unit(h)

    assert h.splash_radius == _TALENT_SPLASH_RADIUS, (
        f"Shockwave must set splash_radius to {_TALENT_SPLASH_RADIUS}; got {h.splash_radius}"
    )


# ---------------------------------------------------------------------------
# Test 4: slot=None still applies talent
# ---------------------------------------------------------------------------

def test_shockwave_no_skill_slot():
    w = _world()
    h = make_headb2(slot=None)
    h.deployed = True; h.position = (0.0, 1.0)
    w.add_unit(h)

    assert h.splash_radius == _TALENT_SPLASH_RADIUS


# ---------------------------------------------------------------------------
# Test 5: splash_atk_multiplier unaffected by talent
# ---------------------------------------------------------------------------

def test_shockwave_multiplier_unchanged():
    w = _world()
    h = make_headb2(slot=None)
    h.deployed = True; h.position = (0.0, 1.0)
    w.add_unit(h)

    assert h.splash_atk_multiplier == 0.5, (
        f"splash_atk_multiplier must remain 0.5; got {h.splash_atk_multiplier}"
    )

"""Exusiai talent "Eagle Eye" — 15% crit chance on all attacks.

Tests cover:
  - Talent configured correctly (TalentComponent present, name and tag match)
  - crit_chance is 0.0 before battle_start fires
  - crit_chance is set to 0.15 after battle_start (World tick triggers it)
  - slot=None still gets the talent (talent is independent of skill slot)
  - Talent does not affect non-Exusiai units (crit_chance stays 0 on others)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, TileType, TICK_RATE, Profession, RoleArchetype,
)
from core.systems import register_default_systems
from data.characters.exusiai import (
    make_exusiai, _EAGLE_EYE_TAG, _CRIT_CHANCE,
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
# Test 1: Talent is configured correctly
# ---------------------------------------------------------------------------

def test_exusiai_talent_configured():
    e = make_exusiai(slot="S3")
    assert len(e.talents) == 1
    assert e.talents[0].name == "Eagle Eye"
    assert e.talents[0].behavior_tag == _EAGLE_EYE_TAG


# ---------------------------------------------------------------------------
# Test 2: crit_chance is 0.0 on a freshly constructed Exusiai
# ---------------------------------------------------------------------------

def test_exusiai_crit_chance_default_zero():
    e = make_exusiai(slot="S2")
    assert e.crit_chance == 0.0, (
        "crit_chance must be 0.0 before battle_start fires"
    )


# ---------------------------------------------------------------------------
# Test 3: crit_chance is 0.15 after World.tick() fires on_battle_start
# ---------------------------------------------------------------------------

def test_exusiai_crit_chance_after_battle_start():
    w = _world()
    e = make_exusiai(slot="S3")
    e.deployed = True
    e.position = (1.0, 1.0)
    w.add_unit(e)

    _ticks(w, 0.2)   # let talent system fire on_battle_start

    assert e.crit_chance == pytest_approx(_CRIT_CHANCE), (
        f"Eagle Eye must set crit_chance={_CRIT_CHANCE}; got {e.crit_chance}"
    )


# ---------------------------------------------------------------------------
# Test 4: slot=None still gets the talent
# ---------------------------------------------------------------------------

def test_exusiai_talent_without_skill_slot():
    w = _world()
    e = make_exusiai(slot=None)
    e.deployed = True
    e.position = (1.0, 1.0)
    w.add_unit(e)

    _ticks(w, 0.2)

    assert e.crit_chance == _CRIT_CHANCE, (
        "Eagle Eye must apply regardless of skill slot"
    )


# ---------------------------------------------------------------------------
# Test 5: Talent does not mutate crit_chance on other deployed allies
# ---------------------------------------------------------------------------

def test_exusiai_talent_does_not_affect_others():
    w = _world()
    e = make_exusiai(slot="S3")
    e.deployed = True
    e.position = (0.0, 1.0)
    w.add_unit(e)

    # A random ally that starts with crit_chance=0.0
    ally = UnitState(
        name="OtherAlly",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=100, defence=50, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        profession=Profession.GUARD,
        block=1,
    )
    ally.range_shape = RangeShape(tiles=((0, 0), (1, 0)))
    ally.deployed = True
    ally.position = (2.0, 1.0)
    w.add_unit(ally)

    _ticks(w, 0.2)

    assert ally.crit_chance == 0.0, (
        "Eagle Eye is self-only; must not raise other allies' crit_chance"
    )


# pytest.approx import helper
try:
    from pytest import approx as pytest_approx
except ImportError:
    def pytest_approx(v, rel=None, abs=None):  # type: ignore[override]
        return v

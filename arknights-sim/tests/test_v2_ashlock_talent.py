"""Ashlock talent "Steadfast Guard" — permanent +150 flat DEF on deployment.

Tests cover:
  - Talent configured correctly
  - No DEF buff before deployment (no talent buff in buffs list)
  - Buff applied after add_unit (on_battle_start)
  - effective_defence increases by exactly _DEF_BONUS
  - S2 active does not remove the Steadfast Guard DEF buff
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.ashlock import (
    make_ashlock, _TALENT_TAG, _TALENT_BUFF_TAG, _DEF_BONUS,
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

def test_ashlock_talent_configured():
    a = make_ashlock(slot="S2")
    assert len(a.talents) == 1
    assert a.talents[0].name == "Steadfast Guard"
    assert a.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: No talent buff before deployment
# ---------------------------------------------------------------------------

def test_no_buff_before_deployment():
    a = make_ashlock(slot="S2")
    buff_tags = [b.source_tag for b in a.buffs]
    assert _TALENT_BUFF_TAG not in buff_tags, (
        "Steadfast Guard buff must NOT exist before add_unit"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF buff applied after add_unit
# ---------------------------------------------------------------------------

def test_steadfast_buff_after_deploy():
    w = _world()
    a = make_ashlock(slot=None)
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    buff_tags = [b.source_tag for b in a.buffs]
    assert _TALENT_BUFF_TAG in buff_tags, (
        "Steadfast Guard buff must exist after add_unit"
    )


# ---------------------------------------------------------------------------
# Test 4: effective_defence increases by _DEF_BONUS
# ---------------------------------------------------------------------------

def test_steadfast_increases_effective_defence():
    base_def = make_ashlock(slot=None).defence   # raw base stat

    w = _world()
    a = make_ashlock(slot=None)
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    expected = base_def + _DEF_BONUS
    assert a.effective_def == expected, (
        f"effective_def must be {expected}; got {a.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 5: S2 end does not remove the Steadfast Guard buff
# ---------------------------------------------------------------------------

def test_steadfast_survives_s2():
    w = _world()
    a = make_ashlock(slot="S2")
    a.deployed = True; a.position = (0.0, 1.0)
    a.skill.sp = float(a.skill.sp_cost)  # pre-fill S2
    w.add_unit(a)

    _ticks(w, 26.0)   # let S2 run and expire

    buff_tags = [b.source_tag for b in a.buffs]
    assert _TALENT_BUFF_TAG in buff_tags, (
        "Steadfast Guard buff must survive S2 end"
    )

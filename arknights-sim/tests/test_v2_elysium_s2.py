"""Elysium S2 "Tactical Gear" — ATK+60%, 24 DP over 12s, block=0 during skill.

Tests cover:
  - S2 skill configured correctly
  - block drops to 0 on skill start
  - ATK buff applied on skill start
  - ~24 DP generated over full 12s (within ±1 tolerance)
  - block and ATK buff restored/removed after skill ends
  - S1 regression — Support γ DP drip still works
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.elysium import (
    make_elysium, _S2_TAG, _S2_ATK_RATIO, _S2_DP_TOTAL, _S2_DURATION,
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
# Test 1: S2 skill configured correctly
# ---------------------------------------------------------------------------

def test_elysium_s2_configured():
    e = make_elysium(slot="S2")
    assert e.skill is not None
    assert e.skill.name == "Tactical Gear"
    assert e.skill.slot == "S2"
    assert e.skill.behavior_tag == _S2_TAG
    assert e.skill.duration == _S2_DURATION
    assert not e.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: block drops to 0 on skill start
# ---------------------------------------------------------------------------

def test_s2_block_drops_to_zero():
    w = _world()
    e = make_elysium(slot="S2")
    e.deployed = True; e.position = (0.0, 1.0)
    e.skill.sp = float(e.skill.sp_cost)
    w.add_unit(e)

    assert e.block == 1, "block must be 1 before skill"
    _ticks(w, 0.1)
    assert e.block == 0, f"block must be 0 while S2 active; got {e.block}"


# ---------------------------------------------------------------------------
# Test 3: ATK buff applied on skill start
# ---------------------------------------------------------------------------

def test_s2_atk_buff_applied():
    w = _world()
    e = make_elysium(slot="S2")
    e.deployed = True; e.position = (0.0, 1.0)
    e.skill.sp = float(e.skill.sp_cost)
    base_atk = e.atk
    w.add_unit(e)

    _ticks(w, 0.1)

    expected = base_atk * (1.0 + _S2_ATK_RATIO)
    assert abs(e.effective_atk - expected) < 1, (
        f"ATK buff must be +{_S2_ATK_RATIO:.0%}; base={base_atk}, expected~{expected:.0f}, got {e.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 4: ~24 DP generated over full 12s
# ---------------------------------------------------------------------------

def test_s2_generates_twentyfour_dp():
    w = _world()
    w.global_state.dp = 0.0
    e = make_elysium(slot="S2")
    e.deployed = True; e.position = (0.0, 1.0)
    e.skill.sp = float(e.skill.sp_cost)
    w.add_unit(e)

    _ticks(w, _S2_DURATION + 0.5)

    assert abs(w.global_state.dp - _S2_DP_TOTAL) <= 1, (
        f"S2 must generate ~{_S2_DP_TOTAL} DP; got {w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 5: block restored and ATK buff removed after skill ends
# ---------------------------------------------------------------------------

def test_s2_cleanup_after_skill():
    w = _world()
    e = make_elysium(slot="S2")
    e.deployed = True; e.position = (0.0, 1.0)
    e.skill.sp = float(e.skill.sp_cost)
    base_atk = e.atk
    w.add_unit(e)

    _ticks(w, _S2_DURATION + 0.5)

    assert e.block == 1, f"block must restore to 1 after S2; got {e.block}"
    assert abs(e.effective_atk - base_atk) < 1, (
        f"ATK buff must be cleared; base={base_atk}, got {e.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S1 regression — Support γ DP drip still works
# ---------------------------------------------------------------------------

def test_elysium_s1_still_works():
    w = _world()
    w.global_state.dp = 0.0
    e = make_elysium(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    e.skill.sp = float(e.skill.sp_cost)
    w.add_unit(e)

    _ticks(w, 8.0 + 0.5)

    assert abs(w.global_state.dp - 18.0) <= 1, (
        f"S1 must generate ~18 DP; got {w.global_state.dp}"
    )

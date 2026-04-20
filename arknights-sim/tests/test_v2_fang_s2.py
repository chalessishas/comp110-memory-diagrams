"""Fang S2 "Assault Formation" — 20 DP over 15s drip, block=0 during skill.

Tests cover:
  - S2 skill configured correctly
  - block drops to 0 on skill start
  - ~20 DP generated over full 15s duration (within ±1 tolerance)
  - block restored after skill ends
  - S1 still works independently (no regression)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.fang import (
    make_fang, _S1_ATK_RATIO, _S2_TAG, _S2_DP_TOTAL, _S2_DURATION,
)
from data.enemies import make_originium_slug


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

def test_fang_s2_configured():
    f = make_fang(slot="S2")
    assert f.skill is not None
    assert f.skill.name == "Assault Formation"
    assert f.skill.slot == "S2"
    assert f.skill.behavior_tag == _S2_TAG
    assert f.skill.duration == _S2_DURATION
    assert not f.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: block drops to 0 on skill start
# ---------------------------------------------------------------------------

def test_s2_block_drops_to_zero():
    w = _world()
    f = make_fang(slot="S2")
    f.deployed = True; f.position = (0.0, 1.0)
    f.skill.sp = float(f.skill.sp_cost)   # pre-fill to fire immediately
    w.add_unit(f)

    assert f.block == 2, "block must be 2 before skill"
    _ticks(w, 0.1)   # trigger skill activation
    assert f.block == 0, f"block must be 0 while S2 active; got {f.block}"


# ---------------------------------------------------------------------------
# Test 3: ~20 DP generated over full 15s
# ---------------------------------------------------------------------------

def test_s2_generates_twenty_dp():
    w = _world()
    w.global_state.dp = 0.0
    f = make_fang(slot="S2")
    f.deployed = True; f.position = (0.0, 1.0)
    f.skill.sp = float(f.skill.sp_cost)
    w.add_unit(f)

    _ticks(w, _S2_DURATION + 0.5)   # run full skill + margin

    assert abs(w.global_state.dp - _S2_DP_TOTAL) <= 1, (
        f"S2 must generate ~{_S2_DP_TOTAL} DP; got {w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 4: block restored after skill ends
# ---------------------------------------------------------------------------

def test_s2_block_restored_after_skill():
    w = _world()
    f = make_fang(slot="S2")
    f.deployed = True; f.position = (0.0, 1.0)
    f.skill.sp = float(f.skill.sp_cost)
    w.add_unit(f)

    _ticks(w, _S2_DURATION + 0.5)

    assert f.block == 2, f"block must restore to 2 after S2; got {f.block}"


# ---------------------------------------------------------------------------
# Test 5: S1 regression — ATK buff still works (needs enemy target to fire)
# ---------------------------------------------------------------------------

def test_fang_s1_still_works():
    w = _world()
    f = make_fang(slot="S1")
    f.deployed = True; f.position = (0.0, 1.0)
    f.skill.sp = float(f.skill.sp_cost)
    base_atk = f.atk
    w.add_unit(f)

    # S1 requires_target=True — add a stationary enemy so auto-trigger fires
    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.move_speed = 0.0; slug.deployed = True; slug.position = (1.0, 1.0)
    w.add_unit(slug)

    _ticks(w, 0.2)

    assert f.effective_atk > base_atk, (
        f"S1 Assault must increase ATK; base={base_atk}, effective={f.effective_atk}"
    )

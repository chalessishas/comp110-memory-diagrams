"""Gravel S2 "Concealment" — ATK +150% 20s, auto-retreat on skill end.

Tests cover:
  - S2 skill configured correctly
  - ATK buff applied on skill start
  - Gravel auto-retreats when skill ends (deployed=False)
  - DP refunded on retreat (cost=8, refund=4)
  - S1 regression — Hidden Blade ATK buff still works
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.gravel import (
    make_gravel, _S2_TAG, _S2_ATK_RATIO,
)
from data.enemies import make_originium_slug

_S2_DURATION = 20.0


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


def _slug_in_range(w: World) -> object:
    """Stationary enemy adjacent to Gravel so requires_target auto-trigger fires."""
    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.move_speed = 0.0; slug.deployed = True; slug.position = (1.0, 1.0)
    w.add_unit(slug)
    return slug


# ---------------------------------------------------------------------------
# Test 1: S2 skill configured correctly
# ---------------------------------------------------------------------------

def test_gravel_s2_configured():
    g = make_gravel(slot="S2")
    assert g.skill is not None
    assert g.skill.name == "Concealment"
    assert g.skill.slot == "S2"
    assert g.skill.behavior_tag == _S2_TAG
    assert g.skill.duration == _S2_DURATION
    assert g.skill.requires_target is True


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on skill start
# ---------------------------------------------------------------------------

def test_s2_atk_buff_on_start():
    w = _world()
    g = make_gravel(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0)
    g.skill.sp = float(g.skill.sp_cost)
    base_atk = g.atk
    w.add_unit(g)
    _slug_in_range(w)

    _ticks(w, 0.1)

    assert g.effective_atk > base_atk, (
        f"S2 must increase ATK; base={base_atk}, effective={g.effective_atk}"
    )
    expected = base_atk * (1.0 + _S2_ATK_RATIO)
    assert abs(g.effective_atk - expected) < 1, (
        f"ATK should be ~{expected:.0f}; got {g.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Gravel auto-retreats when skill ends
# ---------------------------------------------------------------------------

def test_s2_auto_retreat_on_end():
    w = _world()
    g = make_gravel(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0)
    g.skill.sp = float(g.skill.sp_cost)
    w.add_unit(g)
    _slug_in_range(w)

    assert g.deployed is True
    _ticks(w, 0.1)   # trigger skill activation
    assert g.deployed is True, "must still be deployed during skill"

    _ticks(w, _S2_DURATION + 0.5)   # run full skill + margin
    assert g.deployed is False, f"Gravel must auto-retreat after S2; deployed={g.deployed}"


# ---------------------------------------------------------------------------
# Test 4: DP refunded on auto-retreat (cost=8, floor(8/2)=4)
# ---------------------------------------------------------------------------

def test_s2_dp_refunded_on_retreat():
    w = _world()
    w.global_state.dp = 0.0
    g = make_gravel(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0)
    g.skill.sp = float(g.skill.sp_cost)
    w.add_unit(g)
    _slug_in_range(w)

    _ticks(w, 0.1)
    dp_during_skill = w.global_state.dp
    _ticks(w, _S2_DURATION + 0.5)

    expected_refund = g.cost // 2   # 4 DP
    assert w.global_state.dp >= dp_during_skill + expected_refund, (
        f"Retreat must refund {expected_refund} DP; dp_before={dp_during_skill:.1f}, "
        f"dp_after={w.global_state.dp:.1f}"
    )


# ---------------------------------------------------------------------------
# Test 5: S1 regression — Hidden Blade ATK buff still works
# ---------------------------------------------------------------------------

def test_gravel_s1_still_works():
    w = _world()
    g = make_gravel(slot="S1")
    g.deployed = True; g.position = (0.0, 1.0)
    g.skill.sp = float(g.skill.sp_cost)
    base_atk = g.atk
    w.add_unit(g)
    _slug_in_range(w)

    _ticks(w, 0.2)

    assert g.effective_atk > base_atk, (
        f"S1 Hidden Blade must increase ATK; base={base_atk}, effective={g.effective_atk}"
    )

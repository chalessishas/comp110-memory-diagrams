"""Leizi S2 "Thunderclap" — ATK+100%, chain_count=3 (4 total) for 20s.

Tests cover:
  - S2 configured correctly
  - chain_count raised to 3 on skill start
  - ATK buff applied on skill start
  - chain_count restored to base after skill ends
  - ATK buff removed after skill ends
  - S3 regression — Thunderstruck Mane still works (chain_count=5)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.leizi import (
    make_leizi, _S2_TAG, _S2_ATK_RATIO, _S2_CHAIN_COUNT, _BASE_CHAIN_COUNT,
)
from data.enemies import make_originium_slug

_S2_DURATION = 20.0


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
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
    slug = make_originium_slug(path=[(2, 1)] * 5)
    slug.move_speed = 0.0; slug.deployed = True; slug.position = (2.0, 1.0)
    w.add_unit(slug)
    return slug


# ---------------------------------------------------------------------------
# Test 1: S2 configured correctly
# ---------------------------------------------------------------------------

def test_leizi_s2_configured():
    l = make_leizi(slot="S2")
    assert l.skill is not None
    assert l.skill.name == "Thunderclap"
    assert l.skill.slot == "S2"
    assert l.skill.behavior_tag == _S2_TAG
    assert l.skill.duration == _S2_DURATION
    assert l.skill.requires_target is True


# ---------------------------------------------------------------------------
# Test 2: chain_count raised to 3 on skill start
# ---------------------------------------------------------------------------

def test_s2_raises_chain_count():
    w = _world()
    l = make_leizi(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0)
    l.skill.sp = float(l.skill.sp_cost)
    w.add_unit(l)
    _slug_in_range(w)

    assert l.chain_count == _BASE_CHAIN_COUNT, f"base chain must be {_BASE_CHAIN_COUNT}"
    _ticks(w, 0.1)
    assert l.chain_count == _S2_CHAIN_COUNT, (
        f"S2 must raise chain_count to {_S2_CHAIN_COUNT}; got {l.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff applied on skill start
# ---------------------------------------------------------------------------

def test_s2_atk_buff_applied():
    w = _world()
    l = make_leizi(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0)
    l.skill.sp = float(l.skill.sp_cost)
    base_atk = l.atk
    w.add_unit(l)
    _slug_in_range(w)

    _ticks(w, 0.1)

    expected = base_atk * (1.0 + _S2_ATK_RATIO)
    assert abs(l.effective_atk - expected) < 1, (
        f"ATK buff must be +{_S2_ATK_RATIO:.0%}; expected~{expected:.0f}, got {l.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 4: chain_count restored to base after skill ends
# ---------------------------------------------------------------------------

def test_s2_chain_count_restored():
    w = _world()
    l = make_leizi(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0)
    l.skill.sp = float(l.skill.sp_cost)
    w.add_unit(l)
    _slug_in_range(w)

    _ticks(w, _S2_DURATION + 0.5)

    assert l.chain_count == _BASE_CHAIN_COUNT, (
        f"chain_count must restore to {_BASE_CHAIN_COUNT} after S2; got {l.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK buff removed after skill ends
# ---------------------------------------------------------------------------

def test_s2_atk_buff_removed():
    w = _world()
    l = make_leizi(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0)
    l.skill.sp = float(l.skill.sp_cost)
    base_atk = l.atk
    w.add_unit(l)
    _slug_in_range(w)

    _ticks(w, _S2_DURATION + 0.5)

    assert abs(l.effective_atk - base_atk) < 1, (
        f"ATK buff must be cleared after S2; base={base_atk}, got {l.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 regression — Thunderstruck Mane raises chain_count to 5
# ---------------------------------------------------------------------------

def test_leizi_s3_still_works():
    w = _world()
    l = make_leizi(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0)
    l.skill.sp = float(l.skill.sp_cost)
    w.add_unit(l)
    _slug_in_range(w)

    _ticks(w, 0.1)

    assert l.chain_count == 5, (
        f"S3 must raise chain_count to 5; got {l.chain_count}"
    )

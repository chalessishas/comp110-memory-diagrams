"""Leizi talent "Voltage" — chain_count scales with current SP (passive).

Formula: chain_count = BASE(2) + min(floor(sp / 10), 3)
  - 0-9 SP → chain = 2
  - 10-19 SP → chain = 3
  - 20-29 SP → chain = 4
  - 30+ SP → chain = 5 (capped)

During S3 active, S3 manages chain_count (5); talent defers.

Tests cover:
  - Talent configured correctly
  - At 0 SP, chain_count stays at BASE (2)
  - At 10 SP, chain_count becomes 3
  - At 20 SP, chain_count becomes 4
  - At 30 SP, chain_count is capped at 5 (BASE + MAX_BONUS=3)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.leizi import (
    make_leizi, _VOLTAGE_TAG, _BASE_CHAIN_COUNT, _SP_PER_CHAIN, _MAX_BONUS_CHAINS,
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

def test_leizi_talent_configured():
    l = make_leizi(slot="S3")
    assert len(l.talents) == 1
    assert l.talents[0].name == "Voltage"
    assert l.talents[0].behavior_tag == _VOLTAGE_TAG


# ---------------------------------------------------------------------------
# Test 2: At 0 SP, chain_count stays at BASE (2)
# ---------------------------------------------------------------------------

def test_voltage_at_zero_sp():
    w = _world()
    l = make_leizi(slot="S3")
    l.skill.sp = 0.0
    l.skill.sp_cost = 40
    l.deployed = True; l.position = (0.0, 1.0)
    w.add_unit(l)

    _ticks(w, 0.2)

    assert l.chain_count == _BASE_CHAIN_COUNT, (
        f"At 0 SP, chain_count must be {_BASE_CHAIN_COUNT}; got {l.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 3: At 10 SP, chain_count becomes 3
# ---------------------------------------------------------------------------

def test_voltage_at_ten_sp():
    w = _world()
    l = make_leizi(slot="S3")
    l.skill.sp = 10.0
    l.deployed = True; l.position = (0.0, 1.0)
    w.add_unit(l)

    _ticks(w, 0.2)

    expected = _BASE_CHAIN_COUNT + 1
    assert l.chain_count == expected, (
        f"At 10 SP, chain_count must be {expected}; got {l.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 4: At 20 SP, chain_count becomes 4
# ---------------------------------------------------------------------------

def test_voltage_at_twenty_sp():
    w = _world()
    l = make_leizi(slot="S3")
    l.skill.sp = 20.0
    l.deployed = True; l.position = (0.0, 1.0)
    w.add_unit(l)

    _ticks(w, 0.2)

    expected = _BASE_CHAIN_COUNT + 2
    assert l.chain_count == expected, (
        f"At 20 SP, chain_count must be {expected}; got {l.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 5: At 30+ SP, chain_count is capped at BASE + MAX_BONUS
# ---------------------------------------------------------------------------

def test_voltage_capped_at_max():
    w = _world()
    l = make_leizi(slot="S3")
    l.skill.sp = 40.0   # max sp_cost — should cap at BASE + MAX_BONUS
    l.deployed = True; l.position = (0.0, 1.0)
    w.add_unit(l)

    _ticks(w, 0.2)

    expected_max = _BASE_CHAIN_COUNT + _MAX_BONUS_CHAINS
    assert l.chain_count == expected_max, (
        f"At 40 SP, chain_count must be capped at {expected_max}; got {l.chain_count}"
    )

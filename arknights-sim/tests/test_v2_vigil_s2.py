"""Vigil S2 Pack Rally — 6 DP over 12s drip."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.vigil import (
    make_vigil, _S2_TAG, _S2_DP_RATE, _S2_DURATION,
)


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    world.global_state.dp = 0.0
    register_default_systems(world)
    return world


def test_vigil_s2_config():
    v = make_vigil(slot="S2")
    sk = v.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Pack Rally"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


def test_s2_generates_dp():
    """S2 drips DP over its duration — should accumulate ~6 DP total."""
    w = _world()
    v = make_vigil(slot="S2")
    v.deployed = True; v.position = (0.0, 1.0)
    w.add_unit(v)

    v.skill.sp = float(v.skill.sp_cost)
    start_dp = w.global_state.dp

    for _ in range(int(TICK_RATE * _S2_DURATION)):
        w.tick()

    gained = w.global_state.dp - start_dp
    assert gained >= 5, f"S2 should drip ≥5 DP over {_S2_DURATION}s, got {gained}"


def test_s2_does_not_reset_block():
    """S2 does not modify block (unlike S3 which sets block=0)."""
    w = _world()
    v = make_vigil(slot="S2")
    original_block = v.block
    v.deployed = True; v.position = (0.0, 1.0)
    w.add_unit(v)

    v.skill.sp = float(v.skill.sp_cost)
    w.tick()

    assert v.block == original_block


def test_s3_regression():
    v = make_vigil(slot="S3")
    assert v.skill is not None and v.skill.slot == "S3"
    assert v.skill.name == "Packleader's Dignity"

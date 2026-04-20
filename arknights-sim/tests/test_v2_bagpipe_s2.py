"""Bagpipe S2 Pump Up — ATK+100% for 15s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.bagpipe import (
    make_bagpipe, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_bagpipe_s2_config():
    b = make_bagpipe(slot="S2")
    sk = b.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Pump Up"
    assert sk.sp_cost == 20
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+100% buff."""
    w = _world()
    b = make_bagpipe(slot="S2")
    base_atk = b.effective_atk
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()

    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert b.effective_atk == expected_atk, f"ATK: expected {expected_atk}, got {b.effective_atk}"


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    b = make_bagpipe(slot="S2")
    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)

    w = _world()
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b2.source_tag == _S2_BUFF_TAG for b2 in b.buffs)
    assert b.effective_atk == base_atk


def test_s3_regression():
    b = make_bagpipe(slot="S3")
    assert b.skill is not None and b.skill.slot == "S3"
    assert b.skill.name == "Last Wish"

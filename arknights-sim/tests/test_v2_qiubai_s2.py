"""Qiubai S2 Wind Slash — ATK+80% for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.qiubai import (
    make_qiubai, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def test_qiubai_s2_config():
    q = make_qiubai(slot="S2")
    sk = q.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Wind Slash"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+80% buff."""
    w = _world()
    q = make_qiubai(slot="S2")
    base_atk = q.effective_atk
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    w.add_unit(q)

    q.skill.sp = float(q.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert q.effective_atk == expected, f"ATK: expected {expected}, got {q.effective_atk}"


def test_s2_no_block_change():
    """S2 does not change block (unlike S3 which sets block=3)."""
    w = _world()
    q = make_qiubai(slot="S2")
    base_block = q.block
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    w.add_unit(q)

    q.skill.sp = float(q.skill.sp_cost)
    w.tick()

    assert q.block == base_block


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    w = _world()
    q = make_qiubai(slot="S2")
    base_atk = q.effective_atk
    q.deployed = True; q.position = (0.0, 1.0); q.atk_cd = 999.0
    q.skill.sp = float(q.skill.sp_cost)
    w.add_unit(q)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in q.buffs)
    assert q.effective_atk == base_atk


def test_s3_regression():
    q = make_qiubai(slot="S3")
    assert q.skill is not None and q.skill.slot == "S3"
    assert q.skill.name == "Soulwind"

"""Tests for Mayer S3 "Full Assembly" — ATK+60%, spawn 2 mech-otter tokens, 30s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import Faction, TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
import pytest
from data.characters.mayer import make_mayer, _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _TOKEN_NAME, _MAYER_TOKENS_ATTR


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


def test_s3_config():
    op = make_mayer(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 45
    assert op.skill.duration == _S3_DURATION


def test_s3_atk_buff_applied():
    from core.types import BuffAxis, BuffStack
    w = _world()
    op = make_mayer(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK and b.source_tag == "mayer_s3_atk"]
    assert len(atk_buffs) == 1
    assert atk_buffs[0].value == pytest.approx(_S3_ATK_RATIO)


def test_s3_spawns_two_tokens():
    w = _world()
    op = make_mayer(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    tokens_before = len(getattr(op, _MAYER_TOKENS_ATTR, []))
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    tokens_after = getattr(op, _MAYER_TOKENS_ATTR, [])
    new_tokens = tokens_after[tokens_before:]
    assert len(new_tokens) == 2
    units = [w.unit_by_id(tid) for tid in new_tokens]
    assert all(u is not None and u.name == _TOKEN_NAME for u in units)


def test_s3_tokens_alive():
    w = _world()
    op = make_mayer(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    all_ids = getattr(op, _MAYER_TOKENS_ATTR, [])
    assert all(w.unit_by_id(tid).alive for tid in all_ids)


def test_s3_buff_cleared_on_end():
    w = _world()
    op = make_mayer(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == "mayer_s3_atk" for b in op.buffs)


def test_s3_more_atk_than_s2():
    from data.characters.mayer import _S2_ATK_RATIO
    assert _S3_ATK_RATIO > _S2_ATK_RATIO

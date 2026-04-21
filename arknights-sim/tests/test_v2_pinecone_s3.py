"""Tests for Pinecone S3 "Grand Barrage" — ATK+100%, splash radius 2.5, AoE primary, 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import Faction, TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
import pytest
from data.characters.pinecone import make_pinecone, _S3_TAG, _S3_ATK_RATIO, _S3_SPLASH_RADIUS, _S3_DURATION


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def test_s3_config():
    op = make_pinecone(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 45
    assert op.skill.duration == _S3_DURATION


def test_s3_atk_buff_applied():
    from core.types import BuffAxis, BuffStack
    w = _world()
    op = make_pinecone(slot="S3")
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK and b.source_tag == "pinecone_s3_atk"]
    assert len(atk_buffs) == 1
    assert atk_buffs[0].value == pytest.approx(_S3_ATK_RATIO)


def test_s3_enables_attack_all_in_range():
    w = _world()
    op = make_pinecone(slot="S3")
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert getattr(op, "_attack_all_in_range", False)


def test_s3_wider_splash_than_s2():
    from data.characters.pinecone import _S2_SPLASH_RADIUS
    assert _S3_SPLASH_RADIUS > _S2_SPLASH_RADIUS


def test_s3_buff_cleared_on_end():
    w = _world()
    op = make_pinecone(slot="S3")
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == "pinecone_s3_atk" for b in op.buffs)
    assert not getattr(op, "_attack_all_in_range", False)


def test_s3_higher_atk_than_s2():
    from data.characters.pinecone import _S2_ATK_RATIO
    assert _S3_ATK_RATIO > _S2_ATK_RATIO

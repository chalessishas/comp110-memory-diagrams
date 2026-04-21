"""Tests for Dur-nar S3 "Iron Fortress" — DEF+80%, ATK+30%, block→5, 30s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.durnar import (
    make_durnar, _S3_TAG, _S3_DEF_RATIO, _S3_ATK_RATIO, _S3_DURATION,
    _S3_BLOCK, _S3_DEF_BUFF_TAG, _S3_ATK_BUFF_TAG, _S2_BASE_BLOCK,
)


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def test_s3_config():
    op = make_durnar(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 60
    assert op.skill.initial_sp == 30
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_def_buff_applied():
    w = _world()
    op = make_durnar(slot="S3")
    op.position = (1, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert any(b.source_tag == _S3_DEF_BUFF_TAG for b in op.buffs)
    def_val = next(b.value for b in op.buffs if b.source_tag == _S3_DEF_BUFF_TAG)
    assert abs(def_val - _S3_DEF_RATIO) < 1e-6


def test_s3_atk_buff_applied():
    w = _world()
    op = make_durnar(slot="S3")
    op.position = (1, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert any(b.source_tag == _S3_ATK_BUFF_TAG for b in op.buffs)
    atk_val = next(b.value for b in op.buffs if b.source_tag == _S3_ATK_BUFF_TAG)
    assert abs(atk_val - _S3_ATK_RATIO) < 1e-6


def test_s3_block_increased():
    w = _world()
    op = make_durnar(slot="S3")
    op.position = (1, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert op.block == _S3_BLOCK


def test_s3_buffs_cleared_on_end():
    w = _world()
    op = make_durnar(slot="S3")
    op.position = (1, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag in (_S3_DEF_BUFF_TAG, _S3_ATK_BUFF_TAG) for b in op.buffs)
    assert op.block == _S2_BASE_BLOCK


def test_s3_stronger_def_than_s2():
    # S2 DEF+50%, S3 DEF+80%
    assert _S3_DEF_RATIO > 0.50
    assert _S3_BLOCK > 4  # S2 → block 4, S3 → block 5

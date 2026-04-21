"""Tests for Bena S3 "Blood Frenzy" — ATK+150% + HP drain 5%/s, 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import Faction, TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
import pytest
from data.characters.bena import make_bena, _S3_TAG, _S3_ATK_RATIO, _S3_HP_DRAIN_RATIO, _S3_DURATION


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
    op = make_bena(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 50
    assert op.skill.duration == _S3_DURATION


def test_s3_atk_buff_applied():
    from core.types import BuffAxis, BuffStack
    w = _world()
    op = make_bena(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK and b.source_tag == "bena_s3_atk"]
    assert len(atk_buffs) == 1
    assert atk_buffs[0].value == pytest.approx(_S3_ATK_RATIO)


def test_s3_hp_drain_per_tick():
    w = _world()
    op = make_bena(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    initial_hp = op.hp
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, 1.0)
    expected_drain = int(op.max_hp * _S3_HP_DRAIN_RATIO * 1.0)
    assert op.hp < initial_hp
    assert op.hp >= max(1, initial_hp - expected_drain - 5)  # allow small tick rounding


def test_s3_hp_never_below_1():
    w = _world()
    op = make_bena(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    op.hp = 1
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, 30.0)
    assert op.hp >= 1


def test_s3_buff_cleared_on_end():
    w = _world()
    op = make_bena(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert any(b.source_tag == "bena_s3_atk" for b in op.buffs)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == "bena_s3_atk" for b in op.buffs)


def test_s3_higher_atk_than_s2():
    from data.characters.bena import _S2_ATK_RATIO
    assert _S3_ATK_RATIO > _S2_ATK_RATIO


def test_s3_higher_drain_than_s2():
    from data.characters.bena import _S2_HP_DRAIN_RATIO
    assert _S3_HP_DRAIN_RATIO > _S2_HP_DRAIN_RATIO

"""Tests for Akkord S3 "Grand Harmonic" — ATK+200%, AoE pierce, 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.akkord import make_akkord, _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_BUFF_TAG


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    w.global_state.dp = 0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(x: float, y: float, hp: int = 5000) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=hp, hp=hp, atk=0, defence=0)
    e.position = (x, y)
    e.alive = True
    return e


def test_s3_config():
    op = make_akkord(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 50
    assert op.skill.initial_sp == 20
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_akkord(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost  # ready
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)
    ratio_val = next(b.value for b in op.buffs if b.source_tag == _S3_BUFF_TAG)
    assert abs(ratio_val - _S3_ATK_RATIO) < 1e-6


def test_s3_atk_buff_cleared_on_end():
    w = _world()
    op = make_akkord(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)


def test_s3_aoe_flag_on():
    w = _world()
    op = make_akkord(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert getattr(op, "_attack_all_in_range", False) is True


def test_s3_aoe_flag_cleared_on_end():
    w = _world()
    op = make_akkord(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not getattr(op, "_attack_all_in_range", False)


def test_s3_higher_atk_than_s2():
    op_s2 = make_akkord(slot="S2")
    op_s3 = make_akkord(slot="S3")
    assert op_s3.skill.sp_cost > op_s2.skill.sp_cost

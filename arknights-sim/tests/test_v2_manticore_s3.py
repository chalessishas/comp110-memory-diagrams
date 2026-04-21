"""Tests for Manticore S3 "Predator's Domain" — ATK+200%, AoE BIND (4s), 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, SkillTrigger, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.manticore import (
    make_manticore, _S3_TAG, _S3_ATK_RATIO, _S3_DURATION,
    _S3_BIND_DURATION, _S3_BIND_TAG, _S3_BUFF_TAG,
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


def _enemy(x: float, y: float, hp: int = 5000) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=hp, hp=hp, atk=0, defence=0)
    e.position = (x, y)
    e.alive = True
    return e


def test_s3_config():
    op = make_manticore(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 45
    assert op.skill.initial_sp == 15
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_manticore(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)
    ratio_val = next(b.value for b in op.buffs if b.source_tag == _S3_BUFF_TAG)
    assert abs(ratio_val - _S3_ATK_RATIO) < 1e-6


def test_s3_binds_enemies_in_range():
    w = _world()
    op = make_manticore(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    e1 = _enemy(0.0, 1.0)
    e2 = _enemy(1.0, 1.0)
    w.add_unit(e1)
    w.add_unit(e2)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert any(s.kind == StatusKind.BIND and s.source_tag == _S3_BIND_TAG for s in e1.statuses)
    assert any(s.kind == StatusKind.BIND and s.source_tag == _S3_BIND_TAG for s in e2.statuses)


def test_s3_bind_longer_than_s2():
    assert _S3_BIND_DURATION > 2.0  # S2 BIND is 2s, S3 is 4s


def test_s3_atk_buff_cleared_on_end():
    w = _world()
    op = make_manticore(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)


def test_s3_atk_higher_than_s2():
    # S2 is +100%, S3 is +200%
    assert _S3_ATK_RATIO == 2.00
    op_s2 = make_manticore(slot="S2")
    op_s3 = make_manticore(slot="S3")
    assert op_s3.skill.sp_cost > op_s2.skill.sp_cost

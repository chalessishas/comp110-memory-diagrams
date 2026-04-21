"""Tests for Ethan S3 "Binding Storm" — ATK+100%, BIND on hit (3s), 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, SkillTrigger, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_attack_hit
from data.characters.ethan import (
    make_ethan, _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_BUFF_TAG,
    _S3_BIND_DURATION, _S3_BIND_TAG, _S3_ACTIVE_ATTR,
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
    op = make_ethan(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 40
    assert op.skill.initial_sp == 10
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_ethan(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    assert any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)


def test_s3_bind_on_hit():
    w = _world()
    op = make_ethan(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    e = _enemy(1.0, 1.0)
    w.add_unit(e)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, 0.1)
    setattr(op, op.skill.behavior_tag, None)  # mark S3 active
    fire_on_attack_hit(w, op, e, 100)
    assert any(s.kind == StatusKind.BIND and s.source_tag == _S3_BIND_TAG for s in e.statuses)


def test_s3_no_bind_when_inactive():
    w = _world()
    op = make_ethan(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    e = _enemy(1.0, 1.0)
    w.add_unit(e)
    # S3 not triggered — _S3_ACTIVE_ATTR is False
    fire_on_attack_hit(w, op, e, 100)
    assert not any(s.kind == StatusKind.BIND and s.source_tag == _S3_BIND_TAG for s in e.statuses)


def test_s3_atk_buff_cleared_on_end():
    w = _world()
    op = make_ethan(slot="S3")
    op.position = (0, 1)
    op.deployed = True
    w.add_unit(op)
    op.skill.sp = op.skill.sp_cost
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)
    assert not getattr(op, _S3_ACTIVE_ATTR, False)


def test_s3_atk_higher_than_s2():
    op_s2 = make_ethan(slot="S2")
    op_s3 = make_ethan(slot="S3")
    assert _S3_ATK_RATIO > 0.50  # S2 is +50%, S3 is +100%
    assert op_s3.skill.sp_cost > op_s2.skill.sp_cost

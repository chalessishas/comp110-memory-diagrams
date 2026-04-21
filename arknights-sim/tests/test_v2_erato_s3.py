"""Tests for Erato S3 "Lullaby" — ATK+120%, SLEEP on every hit, 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_attack_hit
import pytest
from data.characters.erato import make_erato, _S3_TAG, _S3_ATK_RATIO, _S3_SLEEP_DURATION, _S3_DURATION


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
    op = make_erato(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 45
    assert op.skill.duration == _S3_DURATION


def test_s3_atk_buff_applied():
    from core.types import BuffAxis, BuffStack
    w = _world()
    op = make_erato(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK and b.source_tag == "erato_s3_atk"]
    assert len(atk_buffs) == 1
    assert atk_buffs[0].value == pytest.approx(_S3_ATK_RATIO)


def test_s3_sleep_applied_on_hit():
    w = _world()
    op = make_erato(slot="S3")
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=3000, atk=0, defence=0, res=0.0)
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    w.add_unit(e)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    op._erato_s3_active = True
    fire_on_attack_hit(w, op, e, 100)
    assert any(s.kind == StatusKind.SLEEP for s in e.statuses)


def test_s3_sleep_duration():
    w = _world()
    op = make_erato(slot="S3")
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=3000, atk=0, defence=0, res=0.0)
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    w.add_unit(e)
    op._erato_s3_active = True
    fire_on_attack_hit(w, op, e, 100)
    sleep = next(s for s in e.statuses if s.kind == StatusKind.SLEEP)
    assert sleep.expires_at == pytest.approx(w.global_state.elapsed + _S3_SLEEP_DURATION)


def test_s3_no_sleep_when_inactive():
    w = _world()
    op = make_erato(slot="S3")
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=3000, atk=0, defence=0, res=0.0)
    op.deployed = True
    op.position = (0.0, 1.0)
    w.add_unit(op)
    w.add_unit(e)
    op._erato_s3_active = False
    fire_on_attack_hit(w, op, e, 100)
    assert not any(s.kind == StatusKind.SLEEP for s in e.statuses)


def test_s3_buff_cleared_on_end():
    w = _world()
    op = make_erato(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op._erato_s3_active
    _ticks(w, _S3_DURATION + 0.5)
    assert not op._erato_s3_active
    assert not any(b.source_tag == "erato_s3_atk" for b in op.buffs)

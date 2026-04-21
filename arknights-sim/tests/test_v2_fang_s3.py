"""Tests for Fang S3 "Full Assault" — ATK +200%, 30s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_kill
from data.characters.fang import make_fang, _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_BUFF_TAG


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
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


def test_s3_config():
    op = make_fang(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 50
    assert op.skill.initial_sp == 20
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_fang(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    base_atk = op.effective_atk

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(base_atk * (1 + _S3_ATK_RATIO))


def test_s3_buff_cleared_on_end():
    w = _world()
    op = make_fang(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    base_atk = op.effective_atk

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.1)
    assert op.effective_atk == base_atk
    assert not any(b.source_tag == _S3_BUFF_TAG for b in op.buffs)


def test_s3_stronger_than_s1():
    # S1 = +50%, S3 = +200%
    assert _S3_ATK_RATIO > 0.50


def test_s3_charger_trait_grants_dp_on_kill():
    w = _world()
    op = make_fang(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    enemy = UnitState(
        name="e", faction=Faction.ENEMY,
        max_hp=100, atk=0, defence=0, res=0.0,
        atk_interval=1.0, attack_range_melee=True,
    )
    enemy.position = (1.0, 1.0)
    w.add_unit(enemy)
    enemy.hp = 1

    dp_before = w.global_state.dp
    fire_on_kill(w, op, enemy)
    assert w.global_state.dp == dp_before + 1


def test_s3_s2_regression():
    op = make_fang(slot="S2")
    assert op.skill.slot == "S2"
    assert op.skill.sp_cost == 30
    assert op.skill.duration == 15.0

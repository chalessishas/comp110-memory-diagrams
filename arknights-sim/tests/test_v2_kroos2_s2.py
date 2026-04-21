"""Kroos2 S2 "Permafrost Hail" — 30s AUTO, ATK+100%, direct FREEZE on every hit.

Tests cover:
  - S2 config (name, sp_cost=30, initial_sp=10, duration=30s, AUTO, requires_target)
  - ATK buff: effective_atk = base * (1 + 1.0)
  - _kroos2_s2_active flag set during skill
  - ATK buff cleared after skill ends
  - _kroos2_s2_active cleared after skill ends
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from data.characters.kroos2 import (
    make_kroos2, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_kroos2_s2_config():
    op = make_kroos2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Permafrost Hail"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 10
    assert sk.duration == _S2_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_kroos2(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_active_flag_set():
    w = _world()
    op = make_kroos2(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert getattr(op, "_kroos2_s2_active", False) is True


def test_s2_buff_cleared_on_end():
    w = _world()
    op = make_kroos2(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


def test_s2_active_flag_cleared_on_end():
    w = _world()
    op = make_kroos2(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not getattr(op, "_kroos2_s2_active", False)


def test_s3_regression():
    op = make_kroos2(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Blizzard Barrage"

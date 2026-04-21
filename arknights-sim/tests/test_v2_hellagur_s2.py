"""Hellagur S2 "Tenacity" — ATK+200% for 30s, AUTO_TIME trigger.

Tests cover:
  - S2 config (slot, name, sp_cost, initial_sp, duration, behavior_tag)
  - ATK buff applied on skill start
  - effective_atk = base_atk * (1 + 2.00)
  - ATK buff cleared after skill ends
  - S3 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.state.unit_state import UnitState
from data.characters.hellagur import (
    make_hellagur, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def _activate_s2(w: World, op) -> None:
    _enemy(w, 1.0, 1.0)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()


def test_hellagur_s2_config():
    op = make_hellagur(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Tenacity"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 30
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_hellagur(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _activate_s2(w, op)

    assert op.effective_atk > base_atk
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_atk_amount():
    w = _world()
    op = make_hellagur(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _activate_s2(w, op)

    s2_buff = next(b for b in op.buffs if b.source_tag == _S2_BUFF_TAG)
    assert s2_buff.value == _S2_ATK_RATIO


def test_s2_buff_cleared_on_end():
    w = _world()
    op = make_hellagur(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)
    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


def test_s3_regression():
    op = make_hellagur(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Iron Will"

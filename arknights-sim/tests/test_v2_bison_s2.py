"""Bison S2 "Deepen Battleline" — 40s MANUAL, self DEF+120% + allies DEF+30%.

Tests cover:
  - S2 config (name, sp_cost=50, initial_sp=20, duration=40s, MANUAL)
  - Self DEF buff applied on trigger
  - Allied DEF buff applied on trigger
  - Self and allied buffs cleared on skill end
  - S1 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.bison import (
    make_bison, _S2_TAG, _S2_SELF_DEF_RATIO, _S2_ALLY_DEF_RATIO,
    _S2_SELF_BUFF_TAG, _S2_ALLY_BUFF_TAG, _S2_DURATION,
)
from core.state.unit_state import UnitState
from core.types import AttackType, Profession


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(pos=(2.0, 1.0)) -> UnitState:
    a = UnitState(
        name="Ally", faction=Faction.ALLY,
        max_hp=2000, atk=300, defence=400, res=0.0,
        atk_interval=1.5, profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL, block=3, cost=15,
    )
    a.deployed = True; a.position = pos; a.atk_cd = 999.0
    return a


def test_bison_s2_config():
    op = make_bison(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Deepen Battleline"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 20
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_self_def_buff():
    w = _world()
    op = make_bison(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S2_SELF_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S2_SELF_BUFF_TAG for b in op.buffs)


def test_s2_ally_def_buff():
    w = _world()
    op = make_bison(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    ally = _ally()
    base_ally_def = ally.effective_def
    w.add_unit(ally)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_ally_def * (1 + _S2_ALLY_DEF_RATIO))
    assert ally.effective_def == expected
    assert any(b.source_tag == _S2_ALLY_BUFF_TAG for b in ally.buffs)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_bison(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    ally = _ally()
    base_ally_def = ally.effective_def
    w.add_unit(ally)
    base_def = op.effective_def

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_SELF_BUFF_TAG for b in op.buffs)
    assert not any(b.source_tag == _S2_ALLY_BUFF_TAG for b in ally.buffs)
    assert op.effective_def == base_def
    assert ally.effective_def == base_ally_def


def test_s1_regression():
    op = make_bison(slot="S1")
    assert op.skill is not None and op.skill.slot == "S1"
    assert op.skill.name == "DEF Up γ"

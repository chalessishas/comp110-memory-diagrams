"""Perfumer S3 "Shining Stars" — ATK+120%, heals ALL deployed allies per attack, 30s MANUAL.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - ATK +120% buff applied on start
  - heal_targets set to 999 (all allies) during S3
  - Multiple deployed allies healed when Perfumer attacks during S3
  - heal_targets restored on end, ATK buff cleared
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState
from data.characters.perfumer import (
    make_perfumer,
    _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_BUFF_TAG, _S3_HEAL_TARGETS,
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


def _ticks(w, seconds):
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _injured_ally(name, pos, hp_frac=0.5, max_hp=1000):
    a = UnitState(name=name, faction=Faction.ALLY, max_hp=max_hp, atk=100, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = pos
    a.hp = int(max_hp * hp_frac)
    return a


_PERFUMER_POS = (0.0, 1.0)


def test_s3_config():
    p = make_perfumer(slot="S3")
    assert p.skill is not None and p.skill.slot == "S3"
    assert p.skill.name == "Shining Stars"
    assert p.skill.sp_cost == 40
    from core.types import SkillTrigger
    assert p.skill.trigger == SkillTrigger.MANUAL
    assert p.skill.behavior_tag == _S3_TAG


def test_s3_atk_buff():
    w = _world()
    p = make_perfumer(slot="S3")
    p.deployed = True; p.position = _PERFUMER_POS; p.atk_cd = 999.0
    w.add_unit(p)
    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(p.effective_atk - expected) <= 2


def test_s3_sets_heal_targets():
    w = _world()
    p = make_perfumer(slot="S3")
    p.deployed = True; p.position = _PERFUMER_POS; p.atk_cd = 999.0
    w.add_unit(p)
    assert p.heal_targets == 1, "Perfumer defaults to 1 heal target"
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    assert p.heal_targets == _S3_HEAL_TARGETS, f"S3 must set heal_targets={_S3_HEAL_TARGETS}"


def test_s3_heals_multiple_allies():
    w = _world()
    p = make_perfumer(slot="S3")
    p.deployed = True; p.position = _PERFUMER_POS
    w.add_unit(p)
    ally1 = _injured_ally("Ally1", (0.0, 0.0))
    ally2 = _injured_ally("Ally2", (1.0, 1.0))
    w.add_unit(ally1); w.add_unit(ally2)
    hp1_before = ally1.hp; hp2_before = ally2.hp
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    p.atk_cd = 0.0
    _ticks(w, 2.0)
    assert ally1.hp > hp1_before, "Ally1 must be healed during S3"
    assert ally2.hp > hp2_before, "Ally2 must be healed during S3"


def test_s3_cleanup_on_end():
    w = _world()
    p = make_perfumer(slot="S3")
    p.deployed = True; p.position = _PERFUMER_POS; p.atk_cd = 999.0
    w.add_unit(p)
    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    _ticks(w, _S3_DURATION + 1)
    assert p.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in p.buffs)
    assert p.heal_targets == 1, "heal_targets must revert to 1 after S3"
    assert abs(p.effective_atk - base_atk) <= 2


def test_s2_regression():
    p = make_perfumer(slot="S2")
    assert p.skill is not None and p.skill.slot == "S2"
    assert p.skill.name == "Soothing Fume"

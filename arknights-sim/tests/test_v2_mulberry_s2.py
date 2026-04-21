"""Mulberry S2 "Spring Breeze" — instant MANUAL, AoE heal 150% ATK + clear elemental bars for all allies.

Tests cover:
  - S2 config (name, sp_cost=15, initial_sp=5, instant, MANUAL, requires_target=False)
  - AoE heal: all allies receive heal_amount = 150% ATK
  - Elemental bars cleared on all allies
  - Heal capped at max_hp (no overflow)
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
from core.systems.skill_system import manual_trigger
from data.characters.mulberry import (
    make_mulberry, _S2_TAG, _S2_HEAL_RATIO,
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


def _ally(world: World, x: float, y: float, max_hp: int = 5000, hp: int = None) -> UnitState:
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=max_hp, atk=0, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    if hp is not None:
        a.hp = hp
    world.add_unit(a)
    return a


def test_mulberry_s2_config():
    op = make_mulberry(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Spring Breeze"
    assert sk.sp_cost == 15
    assert sk.initial_sp == 5
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.behavior_tag == _S2_TAG


def test_s2_heals_all_allies():
    w = _world()
    mb = make_mulberry(slot="S2")
    mb.deployed = True; mb.position = (0.0, 1.0); mb.atk_cd = 999.0
    w.add_unit(mb)
    ally1 = _ally(w, 1.0, 1.0, max_hp=5000, hp=1000)
    ally2 = _ally(w, 2.0, 1.0, max_hp=4000, hp=500)

    mb.skill.sp = float(mb.skill.sp_cost)
    manual_trigger(w, mb)

    heal_amount = int(mb.effective_atk * _S2_HEAL_RATIO)
    assert ally1.hp >= 1000 + heal_amount - 1, f"ally1 not healed: hp={ally1.hp}"
    assert ally2.hp >= 500 + heal_amount - 1, f"ally2 not healed: hp={ally2.hp}"


def test_s2_clears_elemental_bars():
    w = _world()
    mb = make_mulberry(slot="S2")
    mb.deployed = True; mb.position = (0.0, 1.0); mb.atk_cd = 999.0
    w.add_unit(mb)
    ally = _ally(w, 1.0, 1.0)
    ally.elemental_bars["fire"] = 50

    mb.skill.sp = float(mb.skill.sp_cost)
    manual_trigger(w, mb)

    assert len(ally.elemental_bars) == 0, "elemental bars should be cleared"


def test_s2_heal_capped_at_max_hp():
    w = _world()
    mb = make_mulberry(slot="S2")
    mb.deployed = True; mb.position = (0.0, 1.0); mb.atk_cd = 999.0
    w.add_unit(mb)
    ally = _ally(w, 1.0, 1.0, max_hp=1000, hp=999)

    mb.skill.sp = float(mb.skill.sp_cost)
    manual_trigger(w, mb)

    assert ally.hp <= ally.max_hp


def test_s3_regression():
    op = make_mulberry(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Bloom Storm"

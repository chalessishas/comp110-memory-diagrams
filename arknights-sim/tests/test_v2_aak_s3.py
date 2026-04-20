"""Aak S3 "Fatal Dose" — instant MANUAL, all in-range allies take 50% max HP true + ATK+45% 25s.

Tests cover:
  - S3 configured correctly (slot, sp_cost=50, MANUAL, instant duration=0.0)
  - In-range ally takes 50% max HP as true damage
  - ATK+45% buff applied to surviving in-range ally for 25s
  - Out-of-range ally takes no damage and receives no buff
  - Dead ally (killed by damage) does NOT receive ATK buff
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Faction, BuffAxis, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.aak import (
    make_aak,
    _S3_TAG, _S3_HP_RATIO, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_BUFF_DURATION,
)

_AAK_POS = (0.0, 1.0)
# GEEK_RANGE: dx in [1,3], dy in [-1,0,1]
_ALLY_IN  = (1.0, 1.0)    # dx=1, dy=0 — in range
_ALLY_OUT = (0.0, 0.0)    # dx=0, dy=-1 — NOT in GEEK_RANGE (dx must be >= 1)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(world: World, x: float, y: float, max_hp: int = 5000) -> UnitState:
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=max_hp, atk=500,
                  defence=200, res=0.0, atk_interval=1.5)
    a.alive = True; a.deployed = True; a.position = (x, y)
    world.add_unit(a)
    return a


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    a = make_aak(slot="S3")
    assert a.skill is not None
    assert a.skill.slot == "S3"
    assert a.skill.name == "Fatal Dose"
    assert a.skill.sp_cost == 50
    assert a.skill.initial_sp == 25
    assert a.skill.duration == 0.0, "Fatal Dose must be instant"
    from core.types import SkillTrigger
    assert a.skill.trigger == SkillTrigger.MANUAL
    assert a.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert a.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: In-range ally takes 50% max HP as true damage
# ---------------------------------------------------------------------------

def test_s3_true_damage_in_range():
    w = _world()
    a = make_aak(slot="S3")
    a.deployed = True; a.position = _AAK_POS; a.atk_cd = 999.0
    w.add_unit(a)
    ally = _ally(w, *_ALLY_IN, max_hp=2000)

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    expected_dmg = int(ally.max_hp * _S3_HP_RATIO)
    actual_dmg = ally.max_hp - ally.hp
    assert abs(actual_dmg - expected_dmg) <= 1, (
        f"In-range ally must take {_S3_HP_RATIO:.0%} max HP true dmg; "
        f"expected {expected_dmg}, got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK+45% buff applied to surviving ally
# ---------------------------------------------------------------------------

def test_s3_atk_buff_in_range():
    w = _world()
    a = make_aak(slot="S3")
    a.deployed = True; a.position = _AAK_POS; a.atk_cd = 999.0
    w.add_unit(a)
    ally = _ally(w, *_ALLY_IN, max_hp=5000)
    base_atk = ally.effective_atk

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    buff = next((b for b in ally.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "In-range ally must receive ATK buff"
    assert buff.axis == BuffAxis.ATK
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(ally.effective_atk - expected) <= 2, (
        f"Ally ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {ally.effective_atk}"
    )

    assert buff.expires_at is not None
    assert abs(buff.expires_at - (w.global_state.elapsed + _S3_BUFF_DURATION)) <= 0.1


# ---------------------------------------------------------------------------
# Test 4: Out-of-range ally takes no damage and receives no buff
# ---------------------------------------------------------------------------

def test_s3_no_effect_out_of_range():
    w = _world()
    a = make_aak(slot="S3")
    a.deployed = True; a.position = _AAK_POS; a.atk_cd = 999.0
    w.add_unit(a)
    ally_out = _ally(w, *_ALLY_OUT, max_hp=2000)

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    assert ally_out.hp == ally_out.max_hp, "Out-of-range ally must take no damage"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in ally_out.buffs), (
        "Out-of-range ally must not receive ATK buff"
    )


# ---------------------------------------------------------------------------
# Test 5: Ally killed by damage does NOT receive ATK buff
# ---------------------------------------------------------------------------

def test_s3_dead_ally_no_buff():
    w = _world()
    a = make_aak(slot="S3")
    a.deployed = True; a.position = _AAK_POS; a.atk_cd = 999.0
    w.add_unit(a)
    # Ally with only 1 HP — 50% max HP damage (500) will kill it
    ally = _ally(w, *_ALLY_IN, max_hp=1000)
    ally.hp = 1

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    assert not ally.alive, "Ally must die from Fatal Dose true damage"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in ally.buffs), (
        "Dead ally must not receive ATK buff"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    a = make_aak(slot="S2")
    assert a.skill is not None and a.skill.slot == "S2"
    assert a.skill.name == "Medical Protocol"
    assert a.skill.sp_cost == 30

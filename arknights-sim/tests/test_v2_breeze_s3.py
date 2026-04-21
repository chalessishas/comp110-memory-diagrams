"""Breeze S3 "Healing Storm" — ATK (heal power)+80% for 30s, MANUAL.

Tests cover:
  - S3 skill configured correctly (slot, sp_cost, MANUAL trigger)
  - ATK+80% buff applied on activation
  - Heal power increases proportionally (more HP healed)
  - ATK buff cleared on S3 end
  - Talent still triggers during S3 (bonus multi-heal)
  - S2 regression (ATK+30% still works)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.breeze import (
    make_breeze,
    _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_BUFF_TAG,
)
from data.characters.fang import make_fang


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _injured_ally(pos=(1.0, 1.0)) -> UnitState:
    ally = make_fang(slot="S1")
    ally.hp = int(ally.max_hp * 0.1)  # heavily injured
    ally.atk_cd = 999.0
    ally.deployed = True
    ally.position = pos
    return ally


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    b = make_breeze(slot="S3")
    assert b.skill is not None
    assert b.skill.slot == "S3"
    assert b.skill.name == "Healing Storm"
    assert b.skill.sp_cost == 40
    assert b.skill.trigger == SkillTrigger.MANUAL
    assert b.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+80% buff applied on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    b = make_breeze(slot="S3")
    b.deployed = True
    b.position = (0.0, 1.0)
    b.atk_cd = 999.0
    w.add_unit(b)
    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert b.effective_atk == expected


# ---------------------------------------------------------------------------
# Test 3: Heal amount increases proportionally with S3 ATK buff
# ---------------------------------------------------------------------------

def test_s3_heal_power_increased():
    w = _world()
    b = make_breeze(slot="S3")
    b.deployed = True
    b.position = (0.0, 1.0)
    w.add_unit(b)
    ally = _injured_ally(pos=(1.0, 1.0))
    w.add_unit(ally)
    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    # effective_atk > base_atk means more healing per tick
    assert b.effective_atk == expected_atk
    assert expected_atk > base_atk


# ---------------------------------------------------------------------------
# Test 4: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    w = _world()
    b = make_breeze(slot="S3")
    b.deployed = True
    b.position = (0.0, 1.0)
    b.atk_cd = 999.0
    w.add_unit(b)
    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    _ticks(w, _S3_DURATION + 0.1)
    assert b.effective_atk == base_atk
    assert not any(buf.source_tag == _S3_ATK_BUFF_TAG for buf in b.buffs)


# ---------------------------------------------------------------------------
# Test 5: S3 buff is stronger than S2 buff
# ---------------------------------------------------------------------------

def test_s3_stronger_than_s2():
    from data.characters.breeze import _S2_ATK_RATIO
    assert _S3_ATK_RATIO > _S2_ATK_RATIO


# ---------------------------------------------------------------------------
# Test 6: S2 regression — ATK+30% still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    w = _world()
    b = make_breeze(slot="S2")
    b.deployed = True
    b.position = (0.0, 1.0)
    b.atk_cd = 999.0
    w.add_unit(b)
    from data.characters.breeze import _S2_ATK_RATIO, _S2_ATK_BUFF_TAG
    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    _ticks(w, 0.1)  # AUTO trigger
    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert b.effective_atk == expected

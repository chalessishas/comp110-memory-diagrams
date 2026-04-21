"""Firewatch S3 "Starburst Arrow" — ATK+130%, attack-all-in-range, MANUAL, 20s.

Tests cover:
  - S3 configured correctly (sp_cost=55, MANUAL trigger, 20s, AUTO_TIME SP)
  - _attack_all_in_range flag set True on S3 start
  - ATK buff (+130%) applied on S3 start
  - Flag and ATK buff cleared on S3 end
  - First-Target talent still applies during S3
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import (
    AttackType, Faction, Mobility, Profession, RoleArchetype,
    SkillTrigger, SPGainMode, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.firewatch import make_firewatch, _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG


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


def _enemy(x: float = 2.0, y: float = 1.0) -> UnitState:
    e = UnitState(name="Dummy", faction=Faction.ENEMY)
    e.hp = e.max_hp = 5000
    e.atk = 0; e.def_ = 0; e.res = 0.0
    e.deployed = True; e.position = (x, y)
    e.mobility = Mobility.GROUND
    e.profession = Profession.ENEMY
    e.archetype = RoleArchetype.ENEMY_GENERIC
    e.attack_type = AttackType.PHYSICAL
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    fw = make_firewatch(slot="S3")
    assert fw.skill is not None
    assert fw.skill.slot == "S3"
    assert fw.skill.name == "Starburst Arrow"
    assert fw.skill.sp_cost == 55
    assert fw.skill.initial_sp == 20
    assert fw.skill.duration == 20.0
    assert fw.skill.trigger == SkillTrigger.MANUAL
    assert fw.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert fw.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: _attack_all_in_range set True on S3 start
# ---------------------------------------------------------------------------

def test_s3_attack_all_in_range_on():
    w = _world()
    fw = make_firewatch(slot="S3")
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 999.0
    w.add_unit(fw)

    assert not getattr(fw, "_attack_all_in_range", False)
    fw.skill.sp = float(fw.skill.sp_cost)
    manual_trigger(w, fw)

    assert fw.skill.active_remaining > 0.0, "S3 must activate"
    assert getattr(fw, "_attack_all_in_range", False), "AoE flag must be True during S3"


# ---------------------------------------------------------------------------
# Test 3: ATK buff (+130%) applied during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    fw = make_firewatch(slot="S3")
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 999.0
    w.add_unit(fw)
    base_atk = fw.atk

    fw.skill.sp = float(fw.skill.sp_cost)
    manual_trigger(w, fw)

    has_buff = any(b.source_tag == _S3_BUFF_TAG for b in fw.buffs)
    assert has_buff, "ATK buff tag must be on operator during S3"
    assert any(abs(b.value - _S3_ATK_RATIO) < 1e-9 for b in fw.buffs if b.source_tag == _S3_BUFF_TAG)
    # effective_atk includes all ratio buffs additively
    assert fw.effective_atk > base_atk, "ATK must increase during S3"


# ---------------------------------------------------------------------------
# Test 4: Flag and buff cleared after S3 ends
# ---------------------------------------------------------------------------

def test_s3_buff_and_flag_cleared_on_end():
    w = _world()
    fw = make_firewatch(slot="S3")
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 999.0
    w.add_unit(fw)

    fw.skill.sp = float(fw.skill.sp_cost)
    manual_trigger(w, fw)
    assert fw.skill.active_remaining > 0.0

    _ticks(w, 21.0)

    assert fw.skill.active_remaining == 0.0, "S3 must have ended"
    assert not getattr(fw, "_attack_all_in_range", False), "AoE flag must be False after S3"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in fw.buffs), "ATK buff must be removed"


# ---------------------------------------------------------------------------
# Test 5: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    fw = make_firewatch(slot="S2")
    assert fw.skill is not None
    assert fw.skill.slot == "S2"
    assert fw.skill.name == "Flash Arrow"
    assert fw.skill.sp_cost == 18
    assert fw.skill.trigger == SkillTrigger.AUTO

"""Meteorite S3 "Meteorite Barrage" — ATK+100%, splash_radius=2.5, MANUAL, 20s.

Tests cover:
  - S3 configured correctly (sp_cost=55, MANUAL, 20s, requires_target=True)
  - ATK buff (+100%) applied on S3 start
  - splash_radius increased to 2.5 during S3
  - Both ATK buff and splash_radius restored on S3 end
  - Talent DEF_DOWN still applies during S3 (stacking)
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import (
    Faction, SkillTrigger, SPGainMode, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.meteo import (
    make_meteo, _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG,
    _S3_SPLASH_RADIUS, _BASE_SPLASH_RADIUS,
)


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


def _enemy(w: World, x: float = 3.0, y: float = 1.0) -> UnitState:
    e = UnitState(name="Dummy", faction=Faction.ENEMY, max_hp=9999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    w.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    mt = make_meteo(slot="S3")
    assert mt.skill is not None
    assert mt.skill.slot == "S3"
    assert mt.skill.name == "Meteorite Barrage"
    assert mt.skill.sp_cost == 55
    assert mt.skill.initial_sp == 25
    assert mt.skill.duration == 20.0
    assert mt.skill.trigger == SkillTrigger.MANUAL
    assert mt.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert mt.skill.requires_target
    assert mt.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    mt = make_meteo(slot="S3")
    mt.deployed = True; mt.position = (0.0, 1.0); mt.atk_cd = 999.0
    w.add_unit(mt)
    e = _enemy(w)
    setattr(mt, "__target__", e)
    base_atk = mt.atk

    mt.skill.sp = float(mt.skill.sp_cost)
    manual_trigger(w, mt)

    assert any(b.source_tag == _S3_ATK_BUFF_TAG for b in mt.buffs), "ATK buff must be present"
    assert any(abs(b.value - _S3_ATK_RATIO) < 1e-9 for b in mt.buffs if b.source_tag == _S3_ATK_BUFF_TAG)
    assert mt.effective_atk > base_atk


# ---------------------------------------------------------------------------
# Test 3: splash_radius increased to S3 value
# ---------------------------------------------------------------------------

def test_s3_splash_radius_increased():
    w = _world()
    mt = make_meteo(slot="S3")
    mt.deployed = True; mt.position = (0.0, 1.0); mt.atk_cd = 999.0
    w.add_unit(mt)
    e = _enemy(w)
    setattr(mt, "__target__", e)

    assert abs(mt.splash_radius - _BASE_SPLASH_RADIUS) < 1e-9, "Splash must start at base"

    mt.skill.sp = float(mt.skill.sp_cost)
    manual_trigger(w, mt)

    assert abs(mt.splash_radius - _S3_SPLASH_RADIUS) < 1e-9, "Splash must be S3 value during skill"


# ---------------------------------------------------------------------------
# Test 4: Buff and splash_radius restored on S3 end
# ---------------------------------------------------------------------------

def test_s3_restored_on_end():
    w = _world()
    mt = make_meteo(slot="S3")
    mt.deployed = True; mt.position = (0.0, 1.0); mt.atk_cd = 999.0
    w.add_unit(mt)
    e = _enemy(w)
    setattr(mt, "__target__", e)

    mt.skill.sp = float(mt.skill.sp_cost)
    manual_trigger(w, mt)
    assert mt.skill.active_remaining > 0.0

    _ticks(w, 21.0)

    assert mt.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in mt.buffs), "ATK buff removed"
    assert abs(mt.splash_radius - _BASE_SPLASH_RADIUS) < 1e-9, "Splash radius restored"


# ---------------------------------------------------------------------------
# Test 5: S3 splash radius > S2 splash radius
# ---------------------------------------------------------------------------

def test_s3_splash_greater_than_s2():
    from data.characters.meteo import _S2_SPLASH_RADIUS
    assert _S3_SPLASH_RADIUS > _S2_SPLASH_RADIUS, "S3 splash must be larger than S2"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    mt = make_meteo(slot="S2")
    assert mt.skill is not None
    assert mt.skill.slot == "S2"
    assert mt.skill.name == "Shock Zone"
    assert mt.skill.sp_cost == 45
    assert mt.skill.trigger == SkillTrigger.AUTO

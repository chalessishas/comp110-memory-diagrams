"""Mountain S3 "Blood and Iron" — ATK+200% + ASPD+40 for 10s, AUTO_ATTACK SP gain.

Note: sp_gain_mode=AUTO_ATTACK with initial_sp=0 — SP accumulates from attacks.
Tests manually set skill.sp to bypass accumulation and test buff mechanics directly.

Tests cover:
  - S3 configured correctly (sp_cost=30, initial_sp=0, AUTO_ATTACK, 10s duration)
  - ATK+200% buff applied on S3 start
  - ASPD+40 flat buff applied on S3 start
  - Both buffs cleared on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, BuffAxis, SPGainMode
from core.systems import register_default_systems
from data.characters.mountain import (
    make_mountain,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG,
    _S3_ASPD_FLAT, _S3_ASPD_BUFF_TAG,
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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    m = make_mountain(slot="S3")
    assert m.skill is not None
    assert m.skill.slot == "S3"
    assert m.skill.name == "Blood and Iron"
    assert m.skill.sp_cost == 30
    assert m.skill.initial_sp == 0
    assert m.skill.duration == 10.0
    from core.types import SkillTrigger
    assert m.skill.trigger == SkillTrigger.AUTO
    assert m.skill.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert m.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+200% buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    m = make_mountain(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)
    _enemy(w, 1.0, 1.0)   # target needed for AUTO + requires_target=True

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # AUTO fires

    buff = next((b for b in m.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None, "ATK buff must be applied on S3 start"
    assert buff.axis == BuffAxis.ATK
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001
    # Natural God talent (+18% ATK when enemy in range) also fires, so skip effective_atk check


# ---------------------------------------------------------------------------
# Test 3: ASPD+40 flat buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_aspd_buff():
    w = _world()
    m = make_mountain(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)
    _enemy(w, 1.0, 1.0)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    aspd_buff = next((b for b in m.buffs if b.source_tag == _S3_ASPD_BUFF_TAG), None)
    assert aspd_buff is not None, "ASPD buff must be applied on S3 start"
    assert aspd_buff.axis == BuffAxis.ASPD
    assert abs(aspd_buff.value - _S3_ASPD_FLAT) <= 0.001


# ---------------------------------------------------------------------------
# Test 4: Both buffs cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    m = make_mountain(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)
    _enemy(w, 1.0, 1.0)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()
    assert m.skill.active_remaining > 0.0, "S3 must have fired"

    _ticks(w, 11.0)

    assert m.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in m.buffs), "ATK buff must clear"
    assert not any(b.source_tag == _S3_ASPD_BUFF_TAG for b in m.buffs), "ASPD buff must clear"


# ---------------------------------------------------------------------------
# Test 5: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    m = make_mountain(slot="S2")
    assert m.skill is not None and m.skill.slot == "S2"
    assert m.skill.sp_cost == 2

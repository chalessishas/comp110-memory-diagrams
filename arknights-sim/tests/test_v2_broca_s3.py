"""Broca S3 "Decisive Battle" — ATK+160%, DEF+75%, splash×1.5 for 25s MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost=40, MANUAL, duration=25s)
  - ATK+160% and DEF+75% buffs applied on S3 start
  - splash_atk_multiplier boosted to 1.5 during S3
  - Buffs and splash multiplier cleared on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction, BuffAxis, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.broca import (
    make_broca,
    _S3_TAG, _S3_ATK_RATIO, _S3_DEF_RATIO, _S3_SPLASH_MULT,
    _S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG,
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


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    b = make_broca(slot="S3")
    assert b.skill is not None
    assert b.skill.slot == "S3"
    assert b.skill.name == "Decisive Battle"
    assert b.skill.sp_cost == 40
    assert b.skill.initial_sp == 20
    assert b.skill.duration == 25.0
    from core.types import SkillTrigger
    assert b.skill.trigger == SkillTrigger.MANUAL
    assert b.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert b.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+160% buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    b = make_broca(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    base_atk = b.effective_atk

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)

    buff = next((bf for bf in b.buffs if bf.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(b.effective_atk - expected) <= 2, (
        f"ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {b.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF+75% buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_def_buff():
    w = _world()
    b = make_broca(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    base_def = b.effective_def

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)

    buff = next((bf for bf in b.buffs if bf.source_tag == _S3_DEF_BUFF_TAG), None)
    assert buff is not None, "S3 DEF buff must be applied"
    assert buff.axis == BuffAxis.DEF
    assert abs(buff.value - _S3_DEF_RATIO) <= 0.001

    expected = int(base_def * (1 + _S3_DEF_RATIO))
    assert abs(b.effective_def - expected) <= 2, (
        f"DEF must be ×{1 + _S3_DEF_RATIO}; expected {expected}, got {b.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: splash_atk_multiplier boosted to 1.5 during S3
# ---------------------------------------------------------------------------

def test_s3_splash_multiplier():
    w = _world()
    b = make_broca(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    assert b.splash_atk_multiplier == 1.0, "Base splash multiplier must be 1.0"

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)

    assert abs(b.splash_atk_multiplier - _S3_SPLASH_MULT) <= 0.001, (
        f"Splash multiplier must be {_S3_SPLASH_MULT} during S3; got {b.splash_atk_multiplier}"
    )


# ---------------------------------------------------------------------------
# Test 5: Buffs and splash multiplier cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    b = make_broca(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    base_atk = b.effective_atk
    base_def = b.effective_def

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    _ticks(w, 26.0)

    assert b.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(bf.source_tag == _S3_ATK_BUFF_TAG for bf in b.buffs), "ATK buff must clear"
    assert not any(bf.source_tag == _S3_DEF_BUFF_TAG for bf in b.buffs), "DEF buff must clear"
    assert abs(b.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert abs(b.effective_def - base_def) <= 2, "DEF must revert to base"
    assert abs(b.splash_atk_multiplier - 1.0) <= 0.001, "Splash multiplier must revert to 1.0"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    b = make_broca(slot="S2")
    assert b.skill is not None and b.skill.slot == "S2"
    assert b.skill.name == "All In"
    assert b.skill.sp_cost == 40

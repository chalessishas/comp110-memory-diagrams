"""Bubble S3 "Grand Surf" — SHIELD=100% max_hp, DEF+600, MANUAL, 25s.

Tests cover:
  - S3 configured correctly (sp_cost=50, MANUAL, 25s)
  - SHIELD = 100% max_hp applied on S3 start
  - DEF buff (+600) applied on S3 start
  - Both SHIELD and DEF buff removed on S3 end
  - S3 SHIELD larger than S2 SHIELD (60% vs 100% max_hp)
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import (
    SkillTrigger, SPGainMode, StatusKind, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.bubble import (
    make_bubble, _S3_TAG, _S3_SHIELD_RATIO, _S3_DEF_BUFF,
    _S3_SHIELD_TAG, _S3_DEF_BUFF_TAG,
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
    bb = make_bubble(slot="S3")
    assert bb.skill is not None
    assert bb.skill.slot == "S3"
    assert bb.skill.name == "Grand Surf"
    assert bb.skill.sp_cost == 50
    assert bb.skill.initial_sp == 20
    assert bb.skill.duration == 25.0
    assert bb.skill.trigger == SkillTrigger.MANUAL
    assert bb.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert bb.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: SHIELD = 100% max_hp applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_shield_applied():
    w = _world()
    bb = make_bubble(slot="S3")
    bb.deployed = True; bb.position = (0.0, 1.0); bb.atk_cd = 999.0
    w.add_unit(bb)

    bb.skill.sp = float(bb.skill.sp_cost)
    manual_trigger(w, bb)

    shield = next((s for s in bb.statuses if s.source_tag == _S3_SHIELD_TAG), None)
    assert shield is not None, "SHIELD status must be applied"
    assert shield.kind == StatusKind.SHIELD
    expected_shield = int(bb.max_hp * _S3_SHIELD_RATIO)
    assert abs(shield.params["amount"] - expected_shield) <= 1, f"SHIELD must be ~{expected_shield}"


# ---------------------------------------------------------------------------
# Test 3: DEF buff (+600) applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_def_buff():
    w = _world()
    bb = make_bubble(slot="S3")
    bb.deployed = True; bb.position = (0.0, 1.0); bb.atk_cd = 999.0
    w.add_unit(bb)
    base_def = bb.effective_def

    bb.skill.sp = float(bb.skill.sp_cost)
    manual_trigger(w, bb)

    def_buff = next((b for b in bb.buffs if b.source_tag == _S3_DEF_BUFF_TAG), None)
    assert def_buff is not None, "DEF buff must be present"
    assert abs(def_buff.value - _S3_DEF_BUFF) < 1e-9
    assert bb.effective_def > base_def


# ---------------------------------------------------------------------------
# Test 4: SHIELD and DEF buff removed on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleared_on_end():
    w = _world()
    bb = make_bubble(slot="S3")
    bb.deployed = True; bb.position = (0.0, 1.0); bb.atk_cd = 999.0
    w.add_unit(bb)

    bb.skill.sp = float(bb.skill.sp_cost)
    manual_trigger(w, bb)
    assert bb.skill.active_remaining > 0.0

    _ticks(w, 26.0)

    assert bb.skill.active_remaining == 0.0
    assert not any(s.source_tag == _S3_SHIELD_TAG for s in bb.statuses), "SHIELD removed"
    assert not any(b.source_tag == _S3_DEF_BUFF_TAG for b in bb.buffs), "DEF buff removed"


# ---------------------------------------------------------------------------
# Test 5: S3 SHIELD amount > S2 SHIELD amount
# ---------------------------------------------------------------------------

def test_s3_shield_larger_than_s2():
    from data.characters.bubble import _S2_SHIELD_RATIO
    assert _S3_SHIELD_RATIO > _S2_SHIELD_RATIO, "S3 must provide more SHIELD than S2"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    bb = make_bubble(slot="S2")
    assert bb.skill is not None
    assert bb.skill.slot == "S2"
    assert bb.skill.name == "Surfing Time"
    assert bb.skill.sp_cost == 40
    assert bb.skill.trigger == SkillTrigger.AUTO

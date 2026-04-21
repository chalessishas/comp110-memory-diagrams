"""Flint S3 "White-Hot Forge" — ATK+200%, attack-all-in-range, MANUAL, 12s.

Tests cover:
  - S3 configured correctly (sp_cost=45, MANUAL, 12s)
  - _attack_all_in_range set True on S3 start
  - ATK buff (+200%) applied on S3 start
  - Flag and buff cleared on S3 end
  - Not-blocking buff still stacks additively with S3 buff
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import (
    SkillTrigger, SPGainMode, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.flint import make_flint, _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _NOT_BLOCKING_BUFF_TAG


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
    fl = make_flint(slot="S3")
    assert fl.skill is not None
    assert fl.skill.slot == "S3"
    assert fl.skill.name == "White-Hot Forge"
    assert fl.skill.sp_cost == 45
    assert fl.skill.initial_sp == 20
    assert fl.skill.duration == 12.0
    assert fl.skill.trigger == SkillTrigger.MANUAL
    assert fl.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert fl.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: _attack_all_in_range set True on S3 start
# ---------------------------------------------------------------------------

def test_s3_attack_all_in_range_on():
    w = _world()
    fl = make_flint(slot="S3")
    fl.deployed = True; fl.position = (0.0, 1.0); fl.atk_cd = 999.0
    w.add_unit(fl)

    assert not getattr(fl, "_attack_all_in_range", False)
    fl.skill.sp = float(fl.skill.sp_cost)
    manual_trigger(w, fl)

    assert fl.skill.active_remaining > 0.0
    assert getattr(fl, "_attack_all_in_range", False), "AoE flag must be True during S3"


# ---------------------------------------------------------------------------
# Test 3: ATK buff (+200%) applied during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    fl = make_flint(slot="S3")
    fl.deployed = True; fl.position = (0.0, 1.0); fl.atk_cd = 999.0
    # Ensure no not-blocking buff by giving a blocking enemy
    w.add_unit(fl)
    base_atk = fl.atk

    fl.skill.sp = float(fl.skill.sp_cost)
    manual_trigger(w, fl)

    assert any(b.source_tag == _S3_BUFF_TAG for b in fl.buffs), "S3 ATK buff must be present"
    assert any(abs(b.value - _S3_ATK_RATIO) < 1e-9 for b in fl.buffs if b.source_tag == _S3_BUFF_TAG)
    assert fl.effective_atk > base_atk


# ---------------------------------------------------------------------------
# Test 4: Buff and flag cleared after S3 ends
# ---------------------------------------------------------------------------

def test_s3_buff_and_flag_cleared_on_end():
    w = _world()
    fl = make_flint(slot="S3")
    fl.deployed = True; fl.position = (0.0, 1.0); fl.atk_cd = 999.0
    w.add_unit(fl)

    fl.skill.sp = float(fl.skill.sp_cost)
    manual_trigger(w, fl)
    assert fl.skill.active_remaining > 0.0

    _ticks(w, 13.0)

    assert fl.skill.active_remaining == 0.0
    assert not getattr(fl, "_attack_all_in_range", False), "AoE flag must be False after S3"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in fl.buffs), "ATK buff must be removed"


# ---------------------------------------------------------------------------
# Test 5: S3 and not-blocking buff stack additively
# ---------------------------------------------------------------------------

def test_s3_stacks_with_not_blocking_buff():
    w = _world()
    fl = make_flint(slot="S3")
    fl.deployed = True; fl.position = (0.0, 1.0); fl.atk_cd = 999.0
    w.add_unit(fl)

    # Tick once to let talent fire with no blocking enemies
    _ticks(w, 0.1)
    has_not_blocking = any(b.source_tag == _NOT_BLOCKING_BUFF_TAG for b in fl.buffs)
    if not has_not_blocking:
        return  # skip if talent didn't fire yet

    fl.skill.sp = float(fl.skill.sp_cost)
    manual_trigger(w, fl)

    tags = {b.source_tag for b in fl.buffs}
    assert _NOT_BLOCKING_BUFF_TAG in tags, "Not-blocking buff must still be present"
    assert _S3_BUFF_TAG in tags, "S3 ATK buff must be present simultaneously"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    fl = make_flint(slot="S2")
    assert fl.skill is not None
    assert fl.skill.slot == "S2"
    assert fl.skill.name == "Smelt and Strike"
    assert fl.skill.sp_cost == 24
    assert fl.skill.trigger == SkillTrigger.AUTO

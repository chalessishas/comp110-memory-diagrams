"""Ceylon S3 "Quiet Recovery" — ATK+20%, ATK_INTERVAL -0.30s to nearby allies, heal_targets→5, 30s MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, MANUAL trigger)
  - Ceylon ATK +20% during S3
  - heal_targets raised from 3 → 5 during S3
  - Nearby ally gets ATK_INTERVAL buff (-0.30s) during S3
  - Out-of-range ally does NOT get ATK_INTERVAL buff
  - All interval buffs cleared on S3 end; heal_targets restored to 3
  - S2 regression (Soothing Waves)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.ceylon import (
    make_ceylon,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_INTERVAL_BUFF_TAG,
    _S3_INTERVAL_OFFSET, _S3_DURATION, _S3_HEAL_TARGETS, _BASE_HEAL_TARGETS,
    _S2_ATK_RATIO,
)
from data.characters.fartth import make_fartth


def _world(w: int = 10, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    c = make_ceylon(slot="S3")
    sk = c.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Quiet Recovery"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Ceylon ATK +20% during S3
# ---------------------------------------------------------------------------

def test_s3_ceylon_atk_buff():
    w = _world()
    c = make_ceylon(slot="S3")
    base_atk = c.effective_atk
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    assert c.skill.active_remaining > 0.0, "S3 must be active"
    buff = next((b for b in c.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be present"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO
    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(c.effective_atk - expected) <= 2


# ---------------------------------------------------------------------------
# Test 3: heal_targets raised to 5 during S3
# ---------------------------------------------------------------------------

def test_s3_heal_targets_raised():
    w = _world()
    c = make_ceylon(slot="S3")
    assert c.heal_targets == _BASE_HEAL_TARGETS, "Pre-S3: heal_targets must be 3"
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    assert c.heal_targets == _S3_HEAL_TARGETS, f"During S3: heal_targets must be {_S3_HEAL_TARGETS}"


# ---------------------------------------------------------------------------
# Test 4: Nearby ally gets ATK_INTERVAL buff
# ---------------------------------------------------------------------------

def test_s3_interval_buff_nearby_ally():
    w = _world()
    c = make_ceylon(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    # Ally at Manhattan distance 2 (within _S3_RANGE=3)
    ally = make_fartth(slot="S2")
    ally.deployed = True; ally.position = (2.0, 1.0); ally.atk_cd = 999.0
    ally.skill.sp = 0.0
    w.add_unit(ally)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    interval_buff = next(
        (b for b in ally.buffs if b.source_tag == _S3_INTERVAL_BUFF_TAG), None
    )
    assert interval_buff is not None, "Nearby ally must receive ATK_INTERVAL buff"
    assert interval_buff.axis == BuffAxis.ATK_INTERVAL
    assert interval_buff.value == _S3_INTERVAL_OFFSET


# ---------------------------------------------------------------------------
# Test 5: Out-of-range ally does NOT get ATK_INTERVAL buff
# ---------------------------------------------------------------------------

def test_s3_interval_buff_not_applied_out_of_range():
    w = _world()
    c = make_ceylon(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    # Ally at Manhattan distance 5 (beyond _S3_RANGE=3)
    ally = make_fartth(slot="S2")
    ally.deployed = True; ally.position = (5.0, 1.0); ally.atk_cd = 999.0
    ally.skill.sp = 0.0
    w.add_unit(ally)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    has_buff = any(b.source_tag == _S3_INTERVAL_BUFF_TAG for b in ally.buffs)
    assert not has_buff, "Out-of-range ally must not receive ATK_INTERVAL buff"


# ---------------------------------------------------------------------------
# Test 6: Buffs cleared on S3 end; heal_targets restored
# ---------------------------------------------------------------------------

def test_s3_cleared_on_end():
    w = _world()
    c = make_ceylon(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    ally = make_fartth(slot="S2")
    ally.deployed = True; ally.position = (2.0, 1.0); ally.atk_cd = 999.0
    ally.skill.sp = 0.0
    w.add_unit(ally)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    _ticks(w, _S3_DURATION + 1.0)

    assert c.skill.active_remaining == 0.0, "S3 must have ended"
    assert c.heal_targets == _BASE_HEAL_TARGETS, "heal_targets must revert to 3"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in c.buffs), "ATK buff cleared"
    assert not any(b.source_tag == _S3_INTERVAL_BUFF_TAG for b in ally.buffs), "Interval buff cleared"


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    c = make_ceylon(slot="S2")
    sk = c.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Soothing Waves"
    assert sk.sp_cost == 20
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME

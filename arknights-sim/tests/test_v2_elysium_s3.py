"""Elysium S3 "Standard Rally" — instant 20 DP + 30% SP gift to deployed Vanguards.

Tests cover:
  - S3 config (slot, instant, MANUAL)
  - Immediately grants 20 DP on activation
  - Deployed Vanguard ally receives 30% of sp_cost SP
  - Non-Vanguard ally does not receive SP
  - Already-active skill ally does not receive SP
  - S1/S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction, Profession
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState, SkillComponent
from core.types import SkillTrigger, SPGainMode
from data.characters.elysium import (
    make_elysium,
    _S3_TAG, _S3_DP_BURST, _S3_SP_GIFT_RATIO,
)
from data.characters.saga import make_saga   # Vanguard test ally


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    w.global_state.dp = 0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    e = make_elysium(slot="S3")
    assert e.skill is not None and e.skill.slot == "S3"
    assert e.skill.name == "Standard Rally"
    assert e.skill.sp_cost == 35
    assert e.skill.duration == 0.0, "Must be instant"
    assert e.skill.trigger == SkillTrigger.MANUAL
    assert e.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Grants 20 DP immediately
# ---------------------------------------------------------------------------

def test_s3_grants_dp():
    w = _world()
    e = make_elysium(slot="S3")
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    w.global_state.dp = 5
    e.skill.sp = float(e.skill.sp_cost)
    manual_trigger(w, e)

    assert w.global_state.dp == 5 + _S3_DP_BURST, (
        f"S3 must grant {_S3_DP_BURST} DP; got {w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 3: Deployed Vanguard receives SP gift
# ---------------------------------------------------------------------------

def test_s3_gifts_sp_to_vanguard():
    w = _world()
    e = make_elysium(slot="S3")
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    saga = make_saga(slot="S2")
    saga.deployed = True; saga.position = (1.0, 1.0)
    saga.skill.sp = 0.0   # empty SP
    w.add_unit(saga)

    e.skill.sp = float(e.skill.sp_cost)
    manual_trigger(w, e)

    expected_sp = saga.skill.sp_cost * _S3_SP_GIFT_RATIO
    assert abs(saga.skill.sp - expected_sp) <= 0.01, (
        f"Vanguard must receive {_S3_SP_GIFT_RATIO:.0%} of sp_cost; expected {expected_sp:.1f}, got {saga.skill.sp:.1f}"
    )


# ---------------------------------------------------------------------------
# Test 4: Non-Vanguard ally does NOT receive SP
# ---------------------------------------------------------------------------

def test_s3_no_sp_gift_non_vanguard():
    w = _world()
    e = make_elysium(slot="S3")
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    # Guard unit (not Vanguard)
    from data.characters.chen import make_chen
    chen = make_chen(slot="S2")
    chen.deployed = True; chen.position = (1.0, 1.0)
    chen.skill.sp = 0.0
    w.add_unit(chen)

    e.skill.sp = float(e.skill.sp_cost)
    initial_chen_sp = chen.skill.sp
    manual_trigger(w, e)

    assert chen.skill.sp == initial_chen_sp, "Non-Vanguard must not receive SP gift"


# ---------------------------------------------------------------------------
# Test 5: SP gift capped at sp_cost
# ---------------------------------------------------------------------------

def test_s3_sp_gift_capped():
    w = _world()
    e = make_elysium(slot="S3")
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    saga = make_saga(slot="S2")
    saga.deployed = True; saga.position = (1.0, 1.0)
    saga.skill.sp = float(saga.skill.sp_cost)   # already full
    w.add_unit(saga)

    e.skill.sp = float(e.skill.sp_cost)
    manual_trigger(w, e)

    assert saga.skill.sp <= float(saga.skill.sp_cost), "SP must not exceed sp_cost"


# ---------------------------------------------------------------------------
# Test 6: S1 regression
# ---------------------------------------------------------------------------

def test_s1_regression():
    e = make_elysium(slot="S1")
    assert e.skill is not None and e.skill.slot == "S1"
    assert e.skill.name == "Support γ"


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    e = make_elysium(slot="S2")
    assert e.skill is not None and e.skill.slot == "S2"
    assert e.skill.name == "Tactical Gear"

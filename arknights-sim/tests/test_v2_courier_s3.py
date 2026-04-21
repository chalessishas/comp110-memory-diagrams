"""Courier S3 "Combat Deployment" — instant 20 DP + ATK+100% for 30s, MANUAL.

Tests cover:
  - S3 skill configured correctly (slot, sp_cost, MANUAL trigger)
  - Instantly grants 20 DP on activation
  - ATK+100% buff applied to Courier on activation
  - ATK buff cleared on S3 end
  - Ally does NOT receive ATK buff (self-only)
  - S2 regression (DP drip still works)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.courier import (
    make_courier,
    _S3_TAG, _S3_DP, _S3_ATK_RATIO, _S3_DURATION, _S3_BUFF_TAG,
)
from data.characters.fang import make_fang


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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    c = make_courier(slot="S3")
    assert c.skill is not None
    assert c.skill.slot == "S3"
    assert c.skill.name == "Combat Deployment"
    assert c.skill.sp_cost == 50
    assert c.skill.trigger == SkillTrigger.MANUAL
    assert c.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: S3 grants 20 DP instantly on activation
# ---------------------------------------------------------------------------

def test_s3_grants_dp():
    w = _world()
    c = make_courier(slot="S3")
    c.deployed = True
    c.position = (0.0, 1.0)
    c.atk_cd = 999.0
    w.add_unit(c)
    w.global_state.dp = 10
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    assert w.global_state.dp == 10 + _S3_DP


# ---------------------------------------------------------------------------
# Test 3: ATK+100% buff applied to Courier on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    c = make_courier(slot="S3")
    c.deployed = True
    c.position = (0.0, 1.0)
    c.atk_cd = 999.0
    w.add_unit(c)
    base_atk = c.effective_atk
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert c.effective_atk == expected


# ---------------------------------------------------------------------------
# Test 4: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    w = _world()
    c = make_courier(slot="S3")
    c.deployed = True
    c.position = (0.0, 1.0)
    c.atk_cd = 999.0
    w.add_unit(c)
    base_atk = c.effective_atk
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    _ticks(w, _S3_DURATION + 0.1)
    assert c.effective_atk == base_atk
    assert not any(b.source_tag == _S3_BUFF_TAG for b in c.buffs)


# ---------------------------------------------------------------------------
# Test 5: Ally does NOT receive ATK buff (self-only)
# ---------------------------------------------------------------------------

def test_s3_does_not_buff_allies():
    w = _world()
    c = make_courier(slot="S3")
    c.deployed = True
    c.position = (0.0, 1.0)
    c.atk_cd = 999.0
    w.add_unit(c)
    ally = make_fang(slot="S1")
    ally.deployed = True
    ally.position = (1.0, 1.0)
    w.add_unit(ally)
    ally_base_atk = ally.effective_atk
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    assert ally.effective_atk == ally_base_atk
    assert not any(b.source_tag == _S3_BUFF_TAG for b in ally.buffs)


# ---------------------------------------------------------------------------
# Test 6: S2 regression — DP drip still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    w = _world()
    c = make_courier(slot="S2")
    c.deployed = True
    c.position = (0.0, 1.0)
    c.atk_cd = 999.0
    w.add_unit(c)
    c.skill.sp = float(c.skill.sp_cost)
    w.tick()  # AUTO trigger fires
    _ticks(w, 15.0)
    assert w.global_state.dp >= 10  # 12 DP over 15s

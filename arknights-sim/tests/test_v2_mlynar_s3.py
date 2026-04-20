"""Mlynar S3 "Father's Teachings" — ASPD+90, block→3, ramp ATK used for 25s.

Tests cover:
  - S3 configured correctly (slot, sp_cost, AUTO trigger, AUTO_ATTACK SP gain)
  - block set to 3 on S3 start (from 0 while inactive)
  - ASPD +90 during S3
  - Liberator ramp ATK buff present during S3 (carries over from inactive period)
  - ASPD buff and ramp cleared on S3 end; block returns to 0
  - S2 regression (Blood of Iron unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from data.characters.mlynar import (
    make_mlynar,
    _S3_TAG, _S3_ASPD_FLAT, _S3_ASPD_BUFF_TAG, _S3_DURATION, _S3_BLOCK,
    _RAMP_BUFF_TAG, _RAMP_ATTR,
)
from data.enemies import make_originium_slug


def _world(w: int = 6, h: int = 3) -> World:
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
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    m = make_mlynar(slot="S3")
    sk = m.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Father's Teachings"
    assert sk.sp_cost == 55
    assert sk.initial_sp == 30
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: block set to 3 on S3 start (Liberator trait)
# ---------------------------------------------------------------------------

def test_s3_block_restored():
    w = _world()
    m = make_mlynar(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    # While inactive, talent sets block=0 each tick
    _ticks(w, 0.5)
    assert m.block == 0, "Mlynar block must be 0 when skill inactive"

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0, "S3 must be active"
    assert m.block == _S3_BLOCK, f"block must be {_S3_BLOCK} during S3, got {m.block}"


# ---------------------------------------------------------------------------
# Test 3: ASPD +90 during S3
# ---------------------------------------------------------------------------

def test_s3_aspd_buff():
    w = _world()
    m = make_mlynar(slot="S3")
    base_aspd = m.effective_aspd
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0
    assert abs(m.effective_aspd - (base_aspd + _S3_ASPD_FLAT)) <= 0.01, (
        f"ASPD must be +{_S3_ASPD_FLAT}; expected {base_aspd + _S3_ASPD_FLAT}, got {m.effective_aspd}"
    )


# ---------------------------------------------------------------------------
# Test 4: Ramp ATK buff carried into S3 from inactive period
# ---------------------------------------------------------------------------

def test_s3_ramp_atk_during_skill():
    w = _world()
    m = make_mlynar(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    # Let ramp accumulate for 5 seconds while inactive
    _ticks(w, 5.0)
    ramp_before = getattr(m, _RAMP_ATTR, 0.0)
    assert ramp_before > 0.0, "Ramp must have accumulated during inactive period"

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0, "S3 must be active"
    ramp_buffs = [b for b in m.buffs if b.source_tag == _RAMP_BUFF_TAG]
    assert len(ramp_buffs) >= 1, "Ramp ATK buff must persist during S3"


# ---------------------------------------------------------------------------
# Test 5: ASPD buff and ramp cleared on S3 end; block returns to 0
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    m = make_mlynar(slot="S3")
    base_aspd = m.effective_aspd
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    _ticks(w, 5.0)  # build ramp

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()
    assert m.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1.0)

    assert m.skill.active_remaining == 0.0, "S3 must have ended"
    aspd_buffs = [b for b in m.buffs if b.source_tag == _S3_ASPD_BUFF_TAG]
    assert len(aspd_buffs) == 0, "ASPD buff must be cleared on S3 end"
    # Ramp resets on S3 end but the talent immediately re-accumulates it.
    # Verify it was reset by checking the value is tiny (< 2s of accumulation).
    ramp_val = getattr(m, _RAMP_ATTR, 0.0)
    assert ramp_val < 0.15, f"Ramp must have been reset on S3 end; found {ramp_val:.4f} (expect < 2s re-accum)"
    assert m.block == 0, "block must be 0 after S3 ends (Liberator suspension)"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    m = make_mlynar(slot="S2")
    assert m.skill is not None
    assert m.skill.slot == "S2"
    assert m.skill.name == "Blood of Iron"
    assert m.skill.sp_cost == 35

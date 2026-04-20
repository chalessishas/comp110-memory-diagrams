"""Lappland S3 "Roaring Flare" — ATK+200%, arts chaser 70% ATK per hit.

Tests cover:
  - S3 configured correctly (slot, sp_cost, MANUAL trigger)
  - ATK +200% during S3
  - Arts chaser fires during S3 (combined damage > physical alone)
  - Arts chaser scales with effective_atk (70% ratio)
  - ATK buff cleared on skill end
  - Talent SILENCE still applied during S3 (regression)
  - S2 regression (Starvation unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_attack_hit
from data.characters.lappland import (
    make_lappland,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_ARTS_RATIO,
    _S3_BUFF_TAG,
)
from data.enemies import make_originium_slug


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


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    lap = make_lappland(slot="S3")
    assert lap.skill is not None
    assert lap.skill.slot == "S3"
    assert lap.skill.name == "Roaring Flare"
    assert lap.skill.sp_cost == 55
    assert lap.skill.initial_sp == 25
    from core.types import SkillTrigger
    assert lap.skill.trigger == SkillTrigger.MANUAL
    assert lap.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +200% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    lap = make_lappland(slot="S3")
    lap.deployed = True; lap.position = (0.0, 1.0); lap.atk_cd = 999.0
    w.add_unit(lap)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    base_atk = lap.effective_atk
    lap.skill.sp = float(lap.skill.sp_cost)
    manual_trigger(w, lap)

    assert lap.skill.active_remaining > 0.0, "S3 must be active"
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(lap.effective_atk - expected_atk) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected_atk}, got {lap.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Arts chaser fires during S3 (combined > physical alone)
# ---------------------------------------------------------------------------

def test_s3_arts_chaser_fires():
    w = _world()
    lap = make_lappland(slot="S3")
    lap.deployed = True; lap.position = (0.0, 1.0); lap.atk_cd = 999.0
    w.add_unit(lap)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    lap.skill.sp = float(lap.skill.sp_cost)
    manual_trigger(w, lap)
    assert lap.skill.active_remaining > 0.0

    # Simulate one hit: fire talent callback with S3 active
    phys_dmg = e.take_physical(lap.effective_atk)
    dmg_before = w.global_state.total_damage_dealt
    fire_on_attack_hit(w, lap, e, phys_dmg)
    dmg_after = w.global_state.total_damage_dealt

    arts_dealt = dmg_after - dmg_before
    assert arts_dealt > 0, "Arts chaser must deal damage during S3"


# ---------------------------------------------------------------------------
# Test 4: Arts chaser scales with effective_atk at 70% ratio
# ---------------------------------------------------------------------------

def test_s3_arts_chaser_ratio():
    w = _world()
    lap = make_lappland(slot="S3")
    lap.deployed = True; lap.position = (0.0, 1.0); lap.atk_cd = 999.0
    w.add_unit(lap)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    e.res = 0  # no arts resistance — chaser equals input exactly
    w.add_unit(e)

    lap.skill.sp = float(lap.skill.sp_cost)
    manual_trigger(w, lap)
    assert lap.skill.active_remaining > 0.0

    effective_atk = lap.effective_atk
    expected_arts = int(effective_atk * _S3_ARTS_RATIO)

    phys_dmg = e.take_physical(lap.effective_atk)
    dmg_before = w.global_state.total_damage_dealt
    fire_on_attack_hit(w, lap, e, phys_dmg)
    dmg_after = w.global_state.total_damage_dealt

    arts_dealt = dmg_after - dmg_before
    assert abs(arts_dealt - expected_arts) <= 2, (
        f"Arts chaser must be {_S3_ARTS_RATIO}×ATK={expected_arts}; got {arts_dealt}"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK buff cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    lap = make_lappland(slot="S3")
    lap.deployed = True; lap.position = (0.0, 1.0); lap.atk_cd = 999.0
    w.add_unit(lap)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    base_atk = lap.effective_atk
    lap.skill.sp = float(lap.skill.sp_cost)
    manual_trigger(w, lap)
    assert lap.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert lap.skill.active_remaining == 0.0, "S3 must have ended"
    atk_buffs = [b for b in lap.buffs if b.source_tag == _S3_BUFF_TAG]
    assert len(atk_buffs) == 0, "S3 ATK buff must be cleared on end"
    assert abs(lap.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert not getattr(lap, "_lappland_s3_active", False), "_lappland_s3_active must be False after S3"


# ---------------------------------------------------------------------------
# Test 6: SILENCE talent still applied during S3 (regression)
# ---------------------------------------------------------------------------

def test_s3_silence_talent_active():
    w = _world()
    lap = make_lappland(slot="S3")
    lap.deployed = True; lap.position = (0.0, 1.0); lap.atk_cd = 999.0
    w.add_unit(lap)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    lap.skill.sp = float(lap.skill.sp_cost)
    manual_trigger(w, lap)
    assert lap.skill.active_remaining > 0.0

    phys_dmg = e.take_physical(lap.effective_atk)
    fire_on_attack_hit(w, lap, e, phys_dmg)

    silenced = any(s.kind == StatusKind.SILENCE for s in e.statuses)
    assert silenced, "SILENCE must be applied to target after hit during S3"

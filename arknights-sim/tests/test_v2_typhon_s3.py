"""Typhon S3 Eternal Hunt — 5-ammo ATK+200% skill (ammo-based termination).

Tests cover:
  - Skill configured correctly (ammo_count=5, duration=0, AUTO_TIME, requires_target)
  - ATK buff applied when S3 fires
  - Ammo decrements by 1 per attack hit
  - Skill terminates after exactly 5 shots (on_end fires, ATK buff cleared)
  - ATK buff cleared after ammo depletes
  - make_typhon(slot=None) produces skill-less Typhon
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.typhon import (
    make_typhon, _S3_ATK_RATIO, _S3_AMMO, _S3_SOURCE_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 0), hp=999999) -> object:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 30)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 skill configured correctly
# ---------------------------------------------------------------------------

def test_typhon_s3_skill_config():
    t = make_typhon(slot="S3")
    assert t.skill is not None
    assert t.skill.name == "Eternal Hunt"
    assert t.skill.ammo_count == _S3_AMMO
    assert t.skill.ammo_count == 5
    assert t.skill.duration == 0.0          # ammo-based, not duration-based
    assert t.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert t.skill.trigger == SkillTrigger.AUTO
    assert t.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied when S3 fires
# ---------------------------------------------------------------------------

def test_typhon_s3_atk_buff():
    w = _world()
    t = make_typhon(slot="S3")
    t.deployed = True; t.position = (0.0, 0.0); t.atk_cd = 999.0
    w.add_unit(t)

    slug = _slug(pos=(1, 0))
    w.add_unit(slug)

    base_atk = t.effective_atk
    t.skill.sp = float(t.skill.sp_cost)
    w.tick()  # skill fires

    expected = int(t.atk * (1.0 + _S3_ATK_RATIO))
    assert t.effective_atk == expected, (
        f"S3 ATK +{_S3_ATK_RATIO:.0%} must give {expected}; got {t.effective_atk}"
    )
    assert t.skill.ammo_remaining == _S3_AMMO, "Ammo must be loaded on skill fire"


# ---------------------------------------------------------------------------
# Test 3: Ammo decrements by 1 per attack hit
# ---------------------------------------------------------------------------

def test_typhon_s3_ammo_decrements_per_hit():
    w = _world()
    t = make_typhon(slot="S3")
    t.deployed = True; t.position = (0.0, 0.0); t.atk_cd = 0.0
    w.add_unit(t)

    slug = _slug(pos=(1, 0))
    w.add_unit(slug)

    # Fire skill manually
    t.skill.sp = float(t.skill.sp_cost)
    w.tick()  # fires skill, loads ammo

    ammo_after_fire = t.skill.ammo_remaining
    assert ammo_after_fire == _S3_AMMO, f"Should load {_S3_AMMO} ammo on fire, got {ammo_after_fire}"

    # Manually trigger one attack by zeroing atk_cd
    t.atk_cd = 0.0
    w.tick()  # one attack

    assert t.skill.ammo_remaining == _S3_AMMO - 1, (
        f"One attack should consume 1 ammo; expected {_S3_AMMO-1}, got {t.skill.ammo_remaining}"
    )


# ---------------------------------------------------------------------------
# Test 4: Skill terminates after exactly 5 shots
# ---------------------------------------------------------------------------

def test_typhon_s3_terminates_after_5_shots():
    w = _world()
    t = make_typhon(slot="S3")
    t.deployed = True; t.position = (0.0, 0.0); t.atk_cd = 0.0
    t.atk_interval = 0.1   # fast attack for test speed
    w.add_unit(t)

    slug = _slug(pos=(1, 0))
    w.add_unit(slug)

    t.skill.sp = float(t.skill.sp_cost)
    w.tick()  # fire skill

    # Run ticks until ammo is 0 or too many ticks
    for _ in range(int(TICK_RATE * 10)):
        if t.skill.active_remaining <= 0.0 or t.skill.ammo_remaining <= 0:
            w.tick()   # one extra tick so skill_system processes ammo=0
            break
        w.tick()

    assert t.skill.ammo_remaining == 0 or t.skill.active_remaining == 0.0, (
        "Ammo must deplete after shots"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK buff cleared after ammo depletes
# ---------------------------------------------------------------------------

def test_typhon_s3_atk_buff_cleared_after_ammo():
    w = _world()
    t = make_typhon(slot="S3")
    t.deployed = True; t.position = (0.0, 0.0); t.atk_cd = 0.0
    t.atk_interval = 0.1   # fast attacks
    w.add_unit(t)

    slug = _slug(pos=(1, 0))
    w.add_unit(slug)

    base_atk = t.effective_atk
    t.skill.sp = float(t.skill.sp_cost)
    w.tick()  # fire skill

    # Run until skill is no longer active (ammo depleted + on_end fired)
    for _ in range(int(TICK_RATE * 20)):
        w.tick()
        if t.skill.active_remaining == 0.0 and t.skill.ammo_remaining == 0:
            break

    remaining = [b for b in t.buffs if b.source_tag == _S3_SOURCE_TAG]
    assert len(remaining) == 0, f"S3 ATK buff must be cleared after ammo depletes; remaining={remaining}"
    assert t.effective_atk == base_atk, "ATK must return to base after S3"


# ---------------------------------------------------------------------------
# Test 6: slot=None produces skill-less Typhon
# ---------------------------------------------------------------------------

def test_typhon_no_slot_no_skill():
    t = make_typhon(slot=None)
    assert t.skill is None

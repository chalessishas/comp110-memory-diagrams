"""Hoshiguma S3 "Shield Bash" — ATK+100%, DEF+200, 25s, MANUAL.
Counter-attack all currently-blocked enemies on each hit received.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL trigger)
  - ATK +100% buff applied on start
  - DEF +200 buff applied on start
  - Buffs cleared on skill end
  - Counter-attack fires against all blocked enemies when Hoshiguma is hit during S3
  - Counter-attack does NOT fire when S3 is inactive
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_hit_received
from data.characters.hoshiguma import (
    make_hoshiguma,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_DEF_FLAT,
    _S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG,
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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    h = make_hoshiguma(slot="S3")
    assert h.skill is not None
    assert h.skill.slot == "S3"
    assert h.skill.name == "Shield Bash"
    assert h.skill.sp_cost == 60
    from core.types import SkillTrigger
    assert h.skill.trigger == SkillTrigger.MANUAL
    assert h.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +100% buff applied
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    h = make_hoshiguma(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    base_atk = h.effective_atk
    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    assert h.skill.active_remaining > 0.0, "S3 must be active"
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(h.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {h.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF +200 buff applied
# ---------------------------------------------------------------------------

def test_s3_def_buff():
    w = _world()
    h = make_hoshiguma(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    base_def = h.effective_def
    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    assert h.skill.active_remaining > 0.0
    assert abs(h.effective_def - (base_def + _S3_DEF_FLAT)) <= 1, (
        f"S3 DEF must be +{_S3_DEF_FLAT}; expected {base_def + _S3_DEF_FLAT}, got {h.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: Buffs cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    w = _world()
    h = make_hoshiguma(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    base_atk = h.effective_atk
    base_def = h.effective_def

    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)
    assert h.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert h.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in h.buffs), "ATK buff must clear"
    assert not any(b.source_tag == _S3_DEF_BUFF_TAG for b in h.buffs), "DEF buff must clear"
    assert abs(h.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert abs(h.effective_def - base_def) <= 1, "DEF must revert to base"


# ---------------------------------------------------------------------------
# Test 5: Counter-attack fires against blocked enemies during S3
# ---------------------------------------------------------------------------

def test_s3_counter_attack_hits_blocked_enemy():
    w = _world()
    h = make_hoshiguma(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    slug = make_originium_slug(path=[(0, 1)] * 20)
    slug.deployed = True; slug.position = (0.0, 1.0); slug.move_speed = 0.0
    slug.defence = 0; slug.res = 0.0
    slug.blocked_by_unit_ids = [h.unit_id]   # simulates blocking
    w.add_unit(slug)

    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)
    assert h.skill.active_remaining > 0.0

    hp_before = slug.hp
    # Simulate Hoshiguma taking a hit — triggers counter-attack
    fake_attacker = slug
    fire_on_hit_received(w, h, fake_attacker, 50)

    assert slug.hp < hp_before, "Blocked enemy must take counter-attack damage during S3"


# ---------------------------------------------------------------------------
# Test 6: Counter-attack does NOT fire when S3 inactive
# ---------------------------------------------------------------------------

def test_s3_counter_does_not_fire_when_inactive():
    w = _world()
    h = make_hoshiguma(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    slug = make_originium_slug(path=[(0, 1)] * 20)
    slug.deployed = True; slug.position = (0.0, 1.0); slug.move_speed = 0.0
    slug.defence = 0; slug.res = 0.0
    slug.blocked_by_unit_ids = [h.unit_id]
    w.add_unit(slug)

    # S3 NOT active
    hp_before = slug.hp
    fire_on_hit_received(w, h, slug, 50)

    assert slug.hp == hp_before, "Counter-attack must not fire when S3 is not active"


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    h = make_hoshiguma(slot="S2")
    assert h.skill is not None and h.skill.slot == "S2"
    assert h.skill.name == "Unshakeable"

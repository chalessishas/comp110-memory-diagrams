"""Ch'en S3 "Tiger Stance" — ATK+200%, ASPD+30, 40s, MANUAL.
  Heartless Act (talent summon) gains ATK+100% while S3 is active.

Tests cover:
  - S3 configured correctly (slot, sp_cost, MANUAL trigger)
  - ATK +200% during S3
  - ASPD +30 during S3
  - ATK and ASPD buffs cleared on skill end
  - Heartless Act receives ATK+100% when S3 starts (if deployed)
  - Heartless Act buff cleared on skill end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.chen import (
    make_chen,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_ASPD_BONUS,
    _S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG, _S3_SWORD_ATK_BUFF_TAG,
    _SWORD_NAME, _make_sword,
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
    c = make_chen(slot="S3")
    assert c.skill is not None
    assert c.skill.slot == "S3"
    assert c.skill.name == "Tiger Stance"
    assert c.skill.sp_cost == 70
    assert c.skill.initial_sp == 35
    from core.types import SkillTrigger
    assert c.skill.trigger == SkillTrigger.MANUAL
    assert c.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +200% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    c = make_chen(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    slug = make_originium_slug(path=[(2, 1)] * 20)
    slug.deployed = True; slug.position = (2.0, 1.0); slug.move_speed = 0.0
    w.add_unit(slug)

    base_atk = c.effective_atk
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    assert c.skill.active_remaining > 0.0, "S3 must be active"
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(c.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {c.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ASPD +30 during S3
# ---------------------------------------------------------------------------

def test_s3_aspd_buff():
    w = _world()
    c = make_chen(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    slug = make_originium_slug(path=[(2, 1)] * 20)
    slug.deployed = True; slug.position = (2.0, 1.0); slug.move_speed = 0.0
    w.add_unit(slug)

    base_aspd = c.effective_aspd
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    assert c.skill.active_remaining > 0.0
    assert abs(c.effective_aspd - (base_aspd + _S3_ASPD_BONUS)) <= 0.01, (
        f"S3 ASPD must be +{_S3_ASPD_BONUS}; expected {base_aspd + _S3_ASPD_BONUS}, got {c.effective_aspd}"
    )


# ---------------------------------------------------------------------------
# Test 4: ATK and ASPD buffs cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    w = _world()
    c = make_chen(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    slug = make_originium_slug(path=[(2, 1)] * 20)
    slug.deployed = True; slug.position = (2.0, 1.0); slug.move_speed = 0.0
    w.add_unit(slug)

    base_atk = c.effective_atk
    base_aspd = c.effective_aspd

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    assert c.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert c.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in c.buffs), "ATK buff must clear on end"
    assert not any(b.source_tag == _S3_ASPD_BUFF_TAG for b in c.buffs), "ASPD buff must clear on end"
    assert abs(c.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert abs(c.effective_aspd - base_aspd) <= 0.01, "ASPD must revert to base"


# ---------------------------------------------------------------------------
# Test 5: Heartless Act gains ATK+100% on S3 start, clears on end
# ---------------------------------------------------------------------------

def test_s3_heartless_act_buff():
    w = _world()
    c = make_chen(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    slug = make_originium_slug(path=[(2, 1)] * 20)
    slug.deployed = True; slug.position = (2.0, 1.0); slug.move_speed = 0.0
    w.add_unit(slug)

    # Manually spawn Heartless Act (normally spawns on kill)
    sword = _make_sword((1.0, 1.0))
    w.add_unit(sword)

    sword_base_atk = sword.effective_atk

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    assert c.skill.active_remaining > 0.0

    sword_buff = next((b for b in sword.buffs if b.source_tag == _S3_SWORD_ATK_BUFF_TAG), None)
    assert sword_buff is not None, f"{_SWORD_NAME} must receive ATK buff from S3"
    assert abs(sword.effective_atk - int(sword_base_atk * 2)) <= 2, (
        f"{_SWORD_NAME} ATK must be ×2 during S3; got {sword.effective_atk}"
    )

    _ticks(w, _S3_DURATION + 1)

    assert c.skill.active_remaining == 0.0, "S3 must end"
    assert not any(b.source_tag == _S3_SWORD_ATK_BUFF_TAG for b in sword.buffs), (
        f"{_SWORD_NAME} ATK buff must clear when S3 ends"
    )
    assert abs(sword.effective_atk - sword_base_atk) <= 2, (
        f"{_SWORD_NAME} ATK must revert to base after S3"
    )

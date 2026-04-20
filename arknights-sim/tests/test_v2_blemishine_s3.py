"""Blemishine S3 "Holy Flash" — ATK+300%, True damage, ally heal on attack.

Tests cover:
  - S3 configured correctly (slot, sp_cost, MANUAL trigger)
  - ATK +300% during S3
  - attack_type converts to TRUE during S3 (bypasses DEF)
  - Ally within range healed for 100% ATK after each attack
  - Out-of-range ally not healed
  - Buffs cleared and attack_type restored on S3 end
  - S2 regression (Iron Aegis unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import AttackType, TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_attack_hit
from data.characters.blemishine import (
    make_blemishine,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_BUFF_TAG,
    _S3_HEAL_RATIO,
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
    b = make_blemishine(slot="S3")
    assert b.skill is not None
    assert b.skill.slot == "S3"
    assert b.skill.name == "Holy Flash"
    assert b.skill.sp_cost == 35
    assert b.skill.initial_sp == 15
    assert b.skill.trigger == SkillTrigger.MANUAL
    assert b.skill.behavior_tag == _S3_TAG
    assert abs(b.skill.duration - _S3_DURATION) < 0.01


# ---------------------------------------------------------------------------
# Test 2: ATK +300% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    b = make_blemishine(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)

    assert b.skill.active_remaining > 0.0, "S3 must be active"
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(b.effective_atk - expected_atk) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected_atk}, got {b.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: attack_type converts to TRUE during S3 (bypasses DEF)
# ---------------------------------------------------------------------------

def test_s3_true_damage_conversion():
    w = _world()
    b = make_blemishine(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    assert b.attack_type == AttackType.PHYSICAL, "Must start as PHYSICAL"

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)

    assert b.skill.active_remaining > 0.0
    assert b.attack_type == AttackType.TRUE, "S3 must convert attack_type to TRUE"

    # Verify True damage ignores high-DEF enemy: take_true == raw, take_physical << raw
    e = make_originium_slug(path=[(2, 1)] * 5)
    e.deployed = True; e.position = (2.0, 1.0)
    e.defence = 9999   # near-impenetrable physically
    raw = b.effective_atk
    phys_dealt = e.take_physical(raw)
    true_dealt = e.take_true(raw)
    assert true_dealt > phys_dealt * 3, (
        f"True damage ({true_dealt}) should far exceed physical ({phys_dealt}) against high-DEF target"
    )


# ---------------------------------------------------------------------------
# Test 4: Ally (including self) within 1 tile is healed for 100% ATK
# ---------------------------------------------------------------------------

def test_s3_ally_heal_on_attack():
    w = _world()
    b = make_blemishine(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    # Set HP low so self-heal has full room (max_hp=3242, heal=ATK×4≈2324)
    b.hp = 1
    w.add_unit(b)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    assert b.skill.active_remaining > 0.0

    expected_heal = int(b.effective_atk * _S3_HEAL_RATIO)
    heal_before = w.global_state.total_healing_done
    fire_on_attack_hit(w, b, e, b.effective_atk)
    heal_after = w.global_state.total_healing_done

    # Blemishine heals herself (Chebyshev distance 0 ≤ 1)
    actual_heal = heal_after - heal_before
    assert actual_heal > 0, "Blemishine must heal herself during S3"
    assert abs(actual_heal - expected_heal) <= 2, (
        f"Heal must be {_S3_HEAL_RATIO}×ATK={expected_heal}; got {actual_heal}"
    )


# ---------------------------------------------------------------------------
# Test 5: Out-of-range ally (Chebyshev > 1) is NOT healed
# ---------------------------------------------------------------------------

def test_s3_out_of_range_ally_not_healed():
    w = _world()
    b = make_blemishine(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    from data.characters.fang import make_fang
    distant_ally = make_fang(slot="S1")
    distant_ally.deployed = True; distant_ally.position = (3.0, 1.0)  # Chebyshev = 3
    distant_ally.hp = distant_ally.max_hp // 2
    w.add_unit(distant_ally)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    assert b.skill.active_remaining > 0.0

    heal_before = w.global_state.total_healing_done
    fire_on_attack_hit(w, b, e, b.effective_atk)
    heal_after = w.global_state.total_healing_done

    assert heal_after == heal_before, "Distant ally must NOT be healed by Holy Flash"


# ---------------------------------------------------------------------------
# Test 6: Buffs cleared and attack_type restored on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    b = make_blemishine(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    manual_trigger(w, b)
    assert b.attack_type == AttackType.TRUE

    _ticks(w, _S3_DURATION + 1)

    assert b.skill.active_remaining == 0.0, "S3 must have ended"
    atk_buffs = [buf for buf in b.buffs if buf.source_tag == _S3_BUFF_TAG]
    assert len(atk_buffs) == 0, "S3 ATK buff must be cleared on end"
    assert b.attack_type == AttackType.PHYSICAL, "attack_type must revert to PHYSICAL"
    assert abs(b.effective_atk - base_atk) <= 2, "ATK must revert to base"
    from data.characters.blemishine import _S3_ACTIVE_ATTR
    assert not getattr(b, _S3_ACTIVE_ATTR, False), "_S3_ACTIVE_ATTR must be False after S3 ends"


# ---------------------------------------------------------------------------
# Test 7: S2 regression (Iron Aegis unchanged)
# ---------------------------------------------------------------------------

def test_s2_regression():
    b = make_blemishine(slot="S2")
    assert b.skill is not None
    assert b.skill.slot == "S2"
    assert b.skill.name == "Iron Aegis"
    assert b.skill.sp_cost == 45
    assert b.attack_type == AttackType.PHYSICAL, "S2 must not change attack_type"

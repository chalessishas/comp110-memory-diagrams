"""Penance S3 "Purgation" — ATK+100%, Arts attack mode, enhanced counter-strike ×0.65, 40s MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost, MANUAL trigger, AUTO_ATTACK SP)
  - ATK +100% during S3
  - attack_type becomes ARTS during S3
  - ATK buff and attack_type cleared on skill end
  - Counter-strike ratio is enhanced (×0.65) during S3
  - Counter-strike reverts to base (×0.35) after S3
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, AttackType, Faction, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_hit_received
from data.characters.penance import (
    make_penance,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG,
    _S3_COUNTER_RATIO, _COUNTER_RATIO,
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


def _dummy_attacker(world: World) -> UnitState:
    e = UnitState(name="Dummy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (1.0, 1.0)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    p = make_penance(slot="S3")
    assert p.skill is not None
    assert p.skill.slot == "S3"
    assert p.skill.name == "Purgation"
    assert p.skill.sp_cost == 40
    assert p.skill.initial_sp == 20
    from core.types import SkillTrigger
    assert p.skill.trigger == SkillTrigger.MANUAL
    assert p.skill.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert p.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +100% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)

    assert p.skill.active_remaining > 0.0, "S3 must be active after manual_trigger"
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(p.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: attack_type becomes ARTS during S3
# ---------------------------------------------------------------------------

def test_s3_arts_mode():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    assert p.attack_type == AttackType.PHYSICAL, "Penance must be Physical before S3"

    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)

    assert p.attack_type == AttackType.ARTS, "Penance must be Arts during S3"


# ---------------------------------------------------------------------------
# Test 4: ATK buff and attack_type cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_cleared_on_end():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    assert p.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert p.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in p.buffs), "ATK buff must clear"
    assert abs(p.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert p.attack_type == AttackType.PHYSICAL, "attack_type must revert to Physical"


# ---------------------------------------------------------------------------
# Test 5: Counter-strike is enhanced (×0.65) during S3
# ---------------------------------------------------------------------------

def test_s3_enhanced_counter():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    attacker = _dummy_attacker(w)

    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    assert p.skill.active_remaining > 0.0

    hp_before = attacker.hp
    fire_on_hit_received(w, p, attacker, damage=100)
    dmg = hp_before - attacker.hp

    expected = int(p.effective_atk * _S3_COUNTER_RATIO)
    assert abs(dmg - expected) <= 2, (
        f"Enhanced counter must be ×{_S3_COUNTER_RATIO}; expected {expected}, got {dmg}"
    )


# ---------------------------------------------------------------------------
# Test 6: Counter-strike reverts to base (×0.35) after S3
# ---------------------------------------------------------------------------

def test_s3_counter_reverts_after_end():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    attacker = _dummy_attacker(w)

    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    _ticks(w, _S3_DURATION + 1)
    assert p.skill.active_remaining == 0.0, "S3 must have ended"

    hp_before = attacker.hp
    fire_on_hit_received(w, p, attacker, damage=100)
    dmg = hp_before - attacker.hp

    expected = int(p.effective_atk * _COUNTER_RATIO)
    assert abs(dmg - expected) <= 2, (
        f"Counter must revert to ×{_COUNTER_RATIO} after S3; expected {expected}, got {dmg}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    p = make_penance(slot="S2")
    assert p.skill is not None
    assert p.skill.slot == "S2"
    assert p.skill.name == "Verdict"
    assert p.skill.sp_cost == 25

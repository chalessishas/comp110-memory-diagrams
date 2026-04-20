"""Ceylon — MEDIC_MULTI: heals 3 allies + passive flat DEF aura + S3 ASPD buff.

Talent "Calm Waters": all allies within 3 tiles gain DEF +30 (flat, not ratio).
S3 "Quiet Recovery": Ceylon ATK+20%, nearby allies ATK_INTERVAL -0.30s, heal
  targets 3 → 5 for 30s duration.

Tests cover:
  - Archetype MEDIC_MULTI, heal_targets=3
  - Talent: nearby ally gains DEF +30 flat
  - Talent: far ally (>3 tiles) gets no buff
  - Talent: flat DEF stacks on top of existing DEF (not ratio)
  - S3: Ceylon ATK +20%
  - S3: in-range ally gets ATK_INTERVAL -0.30s (faster attacks)
  - S3: heal_targets increases to 5
  - S3: all buffs cleared on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import TileType, TICK_RATE, RoleArchetype, Faction, AttackType
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.ceylon import (
    make_ceylon,
    _TALENT_TAG, _TALENT_DEF_TAG, _TALENT_DEF_FLAT, _TALENT_RANGE,
    _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_HEAL_TARGETS, _S2_DURATION,
    _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_INTERVAL_OFFSET, _S3_INTERVAL_BUFF_TAG,
    _S3_HEAL_TARGETS, _S3_DURATION,
)
from data.characters.bena import make_bena


def _world(width=8, height=3) -> World:
    grid = TileGrid(width=width, height=height)
    for x in range(width):
        for y in range(height):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(pos=(1.0, 1.0)) -> UnitState:
    a = make_bena(slot="S2")
    a.deployed = True; a.position = pos; a.atk_cd = 999.0
    return a


# ---------------------------------------------------------------------------
# Test 1: Archetype
# ---------------------------------------------------------------------------

def test_ceylon_archetype():
    c = make_ceylon()
    assert c.archetype == RoleArchetype.MEDIC_MULTI
    assert c.heal_targets == 3
    assert c.block == 1
    assert len(c.talents) == 1
    assert c.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Talent grants DEF +30 flat to nearby ally
# ---------------------------------------------------------------------------

def test_talent_def_flat_nearby_ally():
    """Nearby ally (within _TALENT_RANGE) must receive DEF +30 flat."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    ally = _ally(pos=(1.0, 1.0))  # 1 tile — in range
    base_def = ally.effective_def
    w.add_unit(ally)

    w.tick()

    talent_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_DEF_TAG]
    assert len(talent_buffs) == 1, "Talent must apply DEF buff to nearby ally"
    assert abs(talent_buffs[0].value - _TALENT_DEF_FLAT) < 0.01
    assert ally.effective_def == base_def + _TALENT_DEF_FLAT, (
        f"Effective DEF must increase by {_TALENT_DEF_FLAT} flat; "
        f"base={base_def}, got={ally.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 3: Talent does NOT buff far ally
# ---------------------------------------------------------------------------

def test_talent_no_buff_far_ally():
    """Ally > _TALENT_RANGE tiles away must not get talent DEF buff."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    far_ally = _ally(pos=(7.0, 1.0))  # 7 tiles away
    w.add_unit(far_ally)

    w.tick()

    talent_buffs = [b for b in far_ally.buffs if b.source_tag == _TALENT_DEF_TAG]
    assert len(talent_buffs) == 0, "Talent must NOT buff ally outside range"


# ---------------------------------------------------------------------------
# Test 4: Flat DEF stacks correctly on top of existing DEF
# ---------------------------------------------------------------------------

def test_talent_flat_def_stacks_additively():
    """Flat +30 DEF must add AFTER ratio/mult calculation (not compound with ratios)."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    ally = _ally(pos=(1.0, 1.0))
    base_def = ally.effective_def
    w.add_unit(ally)

    w.tick()
    assert ally.effective_def == base_def + _TALENT_DEF_FLAT, (
        f"Flat DEF must stack additively; expected {base_def + _TALENT_DEF_FLAT}, got {ally.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 5: S3 applies ATK +20% to Ceylon
# ---------------------------------------------------------------------------

def test_s3_atk_buff_on_ceylon():
    """S3 must apply ATK +20% to Ceylon herself."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    base_atk = c.effective_atk
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    assert c.skill.active_remaining > 0.0
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(c.effective_atk - expected_atk) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected={expected_atk}, got={c.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 applies ATK_INTERVAL -0.30s to nearby allies
# ---------------------------------------------------------------------------

def test_s3_attack_interval_buff_nearby_ally():
    """S3 must apply ATK_INTERVAL -0.30s to allies within S3 range."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    ally = _ally(pos=(1.0, 1.0))
    base_interval = ally.current_atk_interval
    w.add_unit(ally)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    interval_buffs = [b for b in ally.buffs if b.source_tag == _S3_INTERVAL_BUFF_TAG]
    assert len(interval_buffs) == 1, "S3 must apply ATK_INTERVAL buff to nearby ally"
    assert abs(interval_buffs[0].value - _S3_INTERVAL_OFFSET) < 0.01
    expected_interval = max(0.067, ally.atk_interval + _S3_INTERVAL_OFFSET)
    assert abs(ally.current_atk_interval - expected_interval) < 0.01, (
        f"current_atk_interval must decrease by {abs(_S3_INTERVAL_OFFSET)}s; "
        f"expected≈{expected_interval:.3f}, got={ally.current_atk_interval:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 7: S3 increases heal targets 3 → 5
# ---------------------------------------------------------------------------

def test_s3_increases_heal_targets():
    """S3 must raise Ceylon's heal_targets from 3 to 5."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    assert c.heal_targets == 3, "Base heal targets must be 3"
    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    assert c.heal_targets == _S3_HEAL_TARGETS, (
        f"S3 must raise heal_targets to {_S3_HEAL_TARGETS}; got {c.heal_targets}"
    )


# ---------------------------------------------------------------------------
# Test 8: S3 buffs cleared on end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    """After S3 ends, all S3 buffs must be removed."""
    w = _world()
    c = make_ceylon()
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)
    ally = _ally(pos=(1.0, 1.0))
    w.add_unit(ally)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert c.skill.active_remaining == 0.0, "S3 must have ended"
    assert c.heal_targets == 3, "heal_targets must return to 3"
    atk_buffs = [b for b in c.buffs if b.source_tag == _S3_ATK_BUFF_TAG]
    assert len(atk_buffs) == 0, "S3 ATK buff must be cleared"
    interval_buffs = [b for b in ally.buffs if b.source_tag == _S3_INTERVAL_BUFF_TAG]
    assert len(interval_buffs) == 0, "S3 ATK_INTERVAL buff must be cleared from ally"


# ---------------------------------------------------------------------------
# S2: Soothing Waves — ATK+30%, heal_targets 3→4
# ---------------------------------------------------------------------------

def test_s2_atk_buff_and_heal_targets():
    """S2 raises ATK by 30% and heal_targets from 3 to 4."""
    w = _world()
    c = make_ceylon(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    assert c.heal_targets == 3

    base_atk = c.effective_atk
    c.skill.sp = c.skill.sp_cost
    w.tick()

    assert c.skill.active_remaining > 0.0
    assert c.heal_targets == _S2_HEAL_TARGETS == 4, (
        f"S2 must raise heal_targets to 4; got {c.heal_targets}"
    )
    expected_atk = int(base_atk * (1.0 + _S2_ATK_RATIO))
    assert c.effective_atk == expected_atk, (
        f"S2 ATK should be {expected_atk}; got {c.effective_atk}"
    )


def test_s2_reverts_on_end():
    """After S2 expires, heal_targets returns to 3 and ATK buff is removed."""
    w = _world()
    c = make_ceylon(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    base_atk = c.effective_atk
    c.skill.sp = c.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert c.skill.active_remaining == 0.0
    assert c.heal_targets == 3, f"heal_targets must revert to 3; got {c.heal_targets}"
    assert abs(c.effective_atk - base_atk) <= 1, (
        f"ATK must revert to {base_atk}; got {c.effective_atk}"
    )

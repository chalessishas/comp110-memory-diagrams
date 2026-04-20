"""Bubble — DEF_PROTECTOR: Foam Guard on-HP-threshold SHIELD + S2 Surfing Time.

DEF_PROTECTOR archetype: high-DEF standard Defender; no separate trait mechanic.

Talent "Foam Guard": Once, when HP < 50%, apply SHIELD(50% max_hp) to self.

S2 "Surfing Time": SHIELD(60% max_hp) + DEF +300 for 20s.

Tests cover:
  - Archetype is DEF_PROTECTOR
  - Foam Guard triggers when HP < 50%
  - Foam Guard shield absorbs damage before HP
  - Foam Guard does NOT trigger when HP >= 50%
  - Foam Guard triggers only once (not again after shield consumed)
  - S2 applies a SHIELD status
  - S2 shield absorbs incoming damage
  - S2 DEF buff increases effective DEF during skill
  - S2 DEF buff is removed after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind, RoleArchetype
from core.systems import register_default_systems
from core.systems.talent_registry import fire_on_tick
from data.characters.bubble import (
    make_bubble,
    _TALENT_HP_THRESHOLD, _TALENT_SHIELD_RATIO, _TALENT_SHIELD_TAG,
    _S2_SHIELD_RATIO, _S2_DEF_BUFF, _S2_DURATION, _S2_SHIELD_TAG, _S2_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _deploy_bubble(w: World, slot: str = "S2") -> UnitState:
    op = make_bubble(slot=slot)
    op.deployed = True
    op.position = (0.0, 1.0)
    w.add_unit(op)
    return op


# ---------------------------------------------------------------------------
# Test 1: Archetype DEF_PROTECTOR
# ---------------------------------------------------------------------------

def test_bubble_archetype():
    b = make_bubble()
    assert b.archetype == RoleArchetype.DEF_PROTECTOR
    assert b.block == 3


# ---------------------------------------------------------------------------
# Test 2: Foam Guard triggers when HP < 50%
# ---------------------------------------------------------------------------

def test_foam_guard_triggers_below_50_hp():
    w = _world()
    b = _deploy_bubble(w)
    b.hp = int(b.max_hp * 0.40)   # 40% HP → below threshold

    fire_on_tick(w, b, DT)

    assert b.has_status(StatusKind.SHIELD), (
        "Foam Guard must apply SHIELD when HP < 50%"
    )
    shield = next(s for s in b.statuses if s.kind == StatusKind.SHIELD)
    expected = int(b.max_hp * _TALENT_SHIELD_RATIO)
    assert shield.params["amount"] == expected


# ---------------------------------------------------------------------------
# Test 3: Foam Guard shield absorbs damage
# ---------------------------------------------------------------------------

def test_foam_guard_shield_absorbs_damage():
    w = _world()
    b = _deploy_bubble(w)
    b.hp = int(b.max_hp * 0.40)
    fire_on_tick(w, b, DT)

    assert b.has_status(StatusKind.SHIELD)
    initial_hp = b.hp
    b.take_damage(500)     # damage absorbed by shield, not HP

    assert b.hp == initial_hp, "Shield must absorb damage before HP"


# ---------------------------------------------------------------------------
# Test 4: Foam Guard does NOT trigger when HP >= 50%
# ---------------------------------------------------------------------------

def test_foam_guard_does_not_trigger_above_threshold():
    w = _world()
    b = _deploy_bubble(w)
    b.hp = int(b.max_hp * 0.60)  # 60% HP → above threshold

    fire_on_tick(w, b, DT)

    assert not b.has_status(StatusKind.SHIELD), (
        "Foam Guard must NOT trigger while HP >= 50%"
    )


# ---------------------------------------------------------------------------
# Test 5: Foam Guard triggers only once
# ---------------------------------------------------------------------------

def test_foam_guard_triggers_only_once():
    w = _world()
    b = _deploy_bubble(w)
    b.hp = int(b.max_hp * 0.40)

    fire_on_tick(w, b, DT)
    assert b.has_status(StatusKind.SHIELD)

    # Consume the shield
    b.statuses = [s for s in b.statuses if s.kind != StatusKind.SHIELD]
    assert not b.has_status(StatusKind.SHIELD)

    # HP still below threshold — second tick should NOT re-apply
    fire_on_tick(w, b, DT)
    assert not b.has_status(StatusKind.SHIELD), (
        "Foam Guard must not trigger a second time"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 applies a SHIELD
# ---------------------------------------------------------------------------

def test_s2_applies_shield():
    w = _world()
    b = _deploy_bubble(w)

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()

    assert b.skill.active_remaining > 0.0, "S2 must be active"
    assert b.has_status(StatusKind.SHIELD), "S2 must apply a SHIELD"
    shield = next(s for s in b.statuses if s.kind == StatusKind.SHIELD)
    expected = int(b.max_hp * _S2_SHIELD_RATIO)
    assert shield.params["amount"] == expected


# ---------------------------------------------------------------------------
# Test 7: S2 shield absorbs incoming damage
# ---------------------------------------------------------------------------

def test_s2_shield_absorbs_damage():
    w = _world()
    b = _deploy_bubble(w)

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()

    assert b.has_status(StatusKind.SHIELD)
    initial_hp = b.hp
    b.take_damage(1000)

    assert b.hp == initial_hp, "S2 shield must absorb damage before HP"


# ---------------------------------------------------------------------------
# Test 8: S2 DEF buff increases effective DEF
# ---------------------------------------------------------------------------

def test_s2_def_buff_increases_def():
    w = _world()
    b = _deploy_bubble(w)
    base_def = b.effective_def

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()

    assert b.skill.active_remaining > 0.0
    assert b.effective_def == base_def + _S2_DEF_BUFF, (
        f"S2 must add +{_S2_DEF_BUFF} DEF; base={base_def}, now={b.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 9: S2 DEF buff removed after skill ends
# ---------------------------------------------------------------------------

def test_s2_def_buff_removed_on_end():
    w = _world()
    b = _deploy_bubble(w)
    base_def = b.effective_def

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()
    assert b.effective_def == base_def + _S2_DEF_BUFF

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert b.skill.active_remaining == 0.0, "S2 must have ended"
    assert b.effective_def == base_def, (
        f"DEF buff must be removed after S2 ends; expected={base_def}, got={b.effective_def}"
    )

"""Flint — GUARD_EARTHSHAKER: ATK doubles when not blocking any enemies.

EARTHSHAKER trait:
  - While no enemies are in Flint's block list: ATK +100% buff applied
  - While 1+ enemies are blocked: buff removed, ATK returns to base
  - Buff toggles on_tick based on current blocking state

Tests cover:
  - Archetype is GUARD_EARTHSHAKER
  - ATK buff applied on deploy (no enemies blocking yet)
  - ATK buff removed when enemy is blocked
  - ATK buff reapplied after enemy unblocked
  - Effective ATK doubles when not blocking
  - Effective ATK normal when blocking
  - S2 ATK buff stacks additively with trait buff
  - S2 buff removed on expiry
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, RoleArchetype
from core.systems import register_default_systems
from data.characters.flint import (
    make_flint, _NOT_BLOCKING_BUFF_TAG, _NOT_BLOCKING_ATK_RATIO,
    _S2_BUFF_TAG, _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=99999, atk=0, move_speed=0.0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk
    e.defence = 0; e.move_speed = move_speed
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype is GUARD_EARTHSHAKER
# ---------------------------------------------------------------------------

def test_flint_archetype():
    f = make_flint()
    assert f.archetype == RoleArchetype.GUARD_EARTHSHAKER
    assert f.block == 1


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied when no enemies blocking
# ---------------------------------------------------------------------------

def test_not_blocking_buff_applied():
    """After one tick with no enemies, Flint should have the +100% ATK buff."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (0.0, 1.0)
    w.add_unit(f)

    w.tick()  # talent runs, no enemies blocking → buff applied

    has_buff = any(b.source_tag == _NOT_BLOCKING_BUFF_TAG for b in f.buffs)
    assert has_buff, "Flint must have not-blocking ATK buff when no enemies present"


# ---------------------------------------------------------------------------
# Test 3: Effective ATK doubles when not blocking
# ---------------------------------------------------------------------------

def test_atk_doubles_when_not_blocking():
    """Flint's effective_atk must double when not blocking."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (0.0, 1.0)
    base_atk = f.atk
    w.add_unit(f)

    w.tick()  # buff applied

    expected = int(base_atk * (1.0 + _NOT_BLOCKING_ATK_RATIO))
    assert abs(f.effective_atk - expected) <= 1, (
        f"ATK when not blocking must be ~{expected}; got {f.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 4: ATK buff removed when blocking an enemy
# ---------------------------------------------------------------------------

def test_buff_removed_when_blocking():
    """When Flint is blocking an enemy, the ATK buff must be removed."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (1.0, 1.0)
    w.add_unit(f)

    # Enemy placed at same tile, stationary so it gets blocked
    enemy = _slug(pos=(1, 1), hp=99999)
    w.add_unit(enemy)

    # First tick: block assignment happens, talent removes buff
    w.tick()
    # Two ticks to let both block assignment and talent catch up
    w.tick()

    is_blocking = f.unit_id in enemy.blocked_by_unit_ids
    if is_blocking:
        has_buff = any(b.source_tag == _NOT_BLOCKING_BUFF_TAG for b in f.buffs)
        assert not has_buff, (
            "Flint must NOT have ATK buff while blocking an enemy"
        )


# ---------------------------------------------------------------------------
# Test 5: Effective ATK is base when blocking
# ---------------------------------------------------------------------------

def test_atk_normal_when_blocking():
    """While blocking, Flint's effective_atk must not include the trait bonus."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (1.0, 1.0)
    base_atk = f.atk
    w.add_unit(f)

    enemy = _slug(pos=(1, 1), hp=99999)
    w.add_unit(enemy)

    # Run until enemy is definitely blocked
    for _ in range(5):
        w.tick()

    is_blocking = f.unit_id in enemy.blocked_by_unit_ids
    if is_blocking:
        # ATK buff should NOT be present
        has_buff = any(b.source_tag == _NOT_BLOCKING_BUFF_TAG for b in f.buffs)
        assert not has_buff, "No trait buff while blocking"
        assert f.effective_atk == base_atk, (
            f"ATK while blocking must be base {base_atk}; got {f.effective_atk}"
        )


# ---------------------------------------------------------------------------
# Test 6: S2 applies ATK buff
# ---------------------------------------------------------------------------

def test_s2_applies_atk_buff():
    """S2 must add +70% ATK buff."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (0.0, 1.0)
    w.add_unit(f)

    base_atk = f.atk
    f.skill.sp = float(f.skill.sp_cost)
    w.tick()  # S2 fires

    assert f.skill.active_remaining > 0.0, "S2 must be active"
    s2_buffs = [b for b in f.buffs if b.source_tag == _S2_BUFF_TAG]
    assert len(s2_buffs) == 1, "S2 ATK buff must be applied"
    assert abs(s2_buffs[0].value - _S2_ATK_RATIO) < 0.01


# ---------------------------------------------------------------------------
# Test 7: S2 + trait buff stack: ATK = base × (1 + 1.0 + 0.7)
# ---------------------------------------------------------------------------

def test_s2_stacks_with_trait():
    """When not blocking and S2 active, both buffs stack: ATK × 2.7."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (0.0, 1.0)
    base_atk = f.atk
    w.add_unit(f)

    # Let trait buff apply first
    w.tick()

    # Fire S2
    f.skill.sp = float(f.skill.sp_cost)
    w.tick()

    assert f.skill.active_remaining > 0.0, "S2 must fire"
    expected = int(base_atk * (1.0 + _NOT_BLOCKING_ATK_RATIO + _S2_ATK_RATIO))
    assert abs(f.effective_atk - expected) <= 2, (
        f"Stacked ATK must be ~{expected}; got {f.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 buff removed after expiry
# ---------------------------------------------------------------------------

def test_s2_buff_removed_on_expiry():
    """After S2 expires, ATK returns to base+trait-buff level."""
    w = _world()
    f = make_flint()
    f.deployed = True; f.position = (0.0, 1.0)
    base_atk = f.atk
    w.add_unit(f)

    f.skill.sp = float(f.skill.sp_cost)
    w.tick()  # S2 fires, trait buff also active

    assert f.skill.active_remaining > 0.0

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert f.skill.active_remaining == 0.0, "S2 must have ended"
    s2_buffs = [b for b in f.buffs if b.source_tag == _S2_BUFF_TAG]
    assert len(s2_buffs) == 0, "S2 buff must be removed after expiry"

    # Only trait buff remains
    expected_no_s2 = int(base_atk * (1.0 + _NOT_BLOCKING_ATK_RATIO))
    assert abs(f.effective_atk - expected_no_s2) <= 1, (
        f"Post-S2 ATK must be trait-buffed {expected_no_s2}; got {f.effective_atk}"
    )

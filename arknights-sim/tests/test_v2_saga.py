"""Saga — Tengu's Edge SP-full ATK buff + S2 Tsurugi burst."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType
from core.systems import register_default_systems
from data.characters.saga import (
    make_saga, _TALENT_TAG, _TALENT_ATK_RATIO,
    _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=9999, atk=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = atk
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_saga_talent_registered():
    saga = make_saga()
    assert len(saga.talents) == 1
    assert saga.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Tengu's Edge activates when SP is full
# ---------------------------------------------------------------------------

def test_tengus_edge_activates_at_full_sp():
    """ATK buff appears when SP reaches sp_cost while skill is not active."""
    w = _world()
    saga = make_saga()
    saga.deployed = True
    saga.position = (0.0, 1.0)
    saga.atk_cd = 999.0
    w.add_unit(saga)

    atk_base = saga.effective_atk

    # Manually fill SP to sp_cost
    saga.skill.sp = float(saga.skill.sp_cost)
    w.tick()   # passive_talent_system fires on_tick

    atk_after = saga.effective_atk
    assert atk_after > atk_base, "Tengu's Edge must increase ATK at full SP"
    expected = int(atk_base * (1.0 + _TALENT_ATK_RATIO))
    assert atk_after == expected, f"Expected ATK={expected}, got {atk_after}"


# ---------------------------------------------------------------------------
# Test 3: Tengu's Edge not active below max SP
# ---------------------------------------------------------------------------

def test_tengus_edge_inactive_below_full_sp():
    """No ATK buff when SP is partially charged."""
    w = _world()
    saga = make_saga()
    saga.deployed = True
    saga.position = (0.0, 1.0)
    saga.atk_cd = 999.0
    w.add_unit(saga)

    atk_base = saga.effective_atk
    saga.skill.sp = float(saga.skill.sp_cost) * 0.80

    for _ in range(5):
        w.tick()

    assert saga.effective_atk == atk_base, "No buff when SP is not full"


# ---------------------------------------------------------------------------
# Test 4: Tengu's Edge buff disappears when skill fires (SP resets)
# ---------------------------------------------------------------------------

def test_tengus_edge_removed_when_skill_active():
    """Once S2 is active (active_remaining > 0), talent buff is removed next on_tick."""
    w = _world()
    saga = make_saga()
    saga.deployed = True
    saga.position = (0.0, 1.0)
    saga.atk_cd = 999.0
    w.add_unit(saga)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    atk_base = saga.effective_atk

    # Tick 1: passive_talent_system adds talent buff (sp=35, active=0)
    saga.skill.sp = float(saga.skill.sp_cost)
    w.tick()
    assert saga.effective_atk > atk_base, "Talent buff must be active at full SP"

    # Tick 2: skill_system fires S2 (active_remaining=30), then passive_talent_system
    # removes talent buff because active_remaining != 0
    w.tick()

    assert saga.skill.active_remaining > 0.0, "S2 must have fired"
    talent_buff_active = any(
        b.source_tag == "saga_tengus_edge_atk" for b in saga.buffs
    )
    assert not talent_buff_active, "Talent ATK buff must be removed when S2 is active"


# ---------------------------------------------------------------------------
# Test 5: S2 Tsurugi activates ATK buff
# ---------------------------------------------------------------------------

def test_saga_s2_atk_buff():
    """S2 fires: ATK increases by +120%."""
    w = _world()
    saga = make_saga()
    saga.deployed = True
    saga.position = (0.0, 1.0)
    saga.atk_cd = 999.0
    w.add_unit(saga)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    atk_base = saga.effective_atk
    saga.skill.sp = saga.skill.sp_cost
    w.tick()  # skill fires
    # Next tick: talent buff should be gone, S2 buff active
    w.tick()

    assert saga.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert saga.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {saga.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_saga_s2_buff_removed_on_end():
    """ATK reverts to base after S2 expires."""
    w = _world()
    saga = make_saga()
    saga.deployed = True
    saga.position = (0.0, 1.0)
    saga.atk_cd = 999.0
    w.add_unit(saga)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    atk_base = saga.effective_atk
    saga.skill.sp = saga.skill.sp_cost
    w.tick()  # fires

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert saga.skill.active_remaining == 0.0, "S2 must have expired"
    assert saga.effective_atk == atk_base, "ATK must revert to base after S2 ends"


# ---------------------------------------------------------------------------
# Test 7: Tengu's Edge re-activates after S2 expires and SP refills
# ---------------------------------------------------------------------------

def test_tengus_edge_active_during_lockout():
    """Talent buff is observable when SP is full but skill is locked out (no target)."""
    w = _world()
    saga = make_saga()
    saga.deployed = True
    saga.position = (0.0, 1.0)
    saga.atk_cd = 999.0
    w.add_unit(saga)
    # No slug in world — skill will lock out when SP is full

    atk_base = saga.effective_atk

    # Fill SP: skill_system locks out (no target), passive_talent_system adds buff
    saga.skill.sp = float(saga.skill.sp_cost)
    w.tick()

    assert saga.skill.locked_out, "Skill must be locked out with no target"
    expected = int(atk_base * (1.0 + _TALENT_ATK_RATIO))
    assert saga.effective_atk == expected, (
        f"Tengu's Edge must apply during lockout, expected ATK={expected}"
    )

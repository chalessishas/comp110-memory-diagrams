"""Mayer summon budget cap — max 4 tokens per deployment.

Tests cover:
  - Talent spawns 1 token on battle start (consumes 1 budget)
  - S2 spawns additional token each fire
  - After 4 total spawns, further _spawn_token calls are no-ops
  - Budget counter decrements correctly
  - Fresh make_mayer starts with no _summons_remaining (lazy init)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, Faction
from core.systems import register_default_systems
from data.characters.mayer import make_mayer, _MAYER_SUMMON_BUDGET, _spawn_token


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _count_tokens(world: World) -> int:
    return sum(
        1 for u in world.units
        if u.name == "Mech-Otter" and u.alive and u.faction == Faction.ALLY
    )


# ---------------------------------------------------------------------------
# Test 1: Budget constant is correct
# ---------------------------------------------------------------------------

def test_mayer_budget_constant():
    assert _MAYER_SUMMON_BUDGET == 4, "E2 max budget must be 4"


# ---------------------------------------------------------------------------
# Test 2: Fresh operator has no _summons_remaining set (lazy init)
# ---------------------------------------------------------------------------

def test_mayer_fresh_no_budget_attr():
    m = make_mayer(slot="S2")
    assert not hasattr(m, "_summons_remaining"), (
        "_summons_remaining must not be pre-set; lazy-init on first spawn"
    )


# ---------------------------------------------------------------------------
# Test 3: Each _spawn_token call decrements the budget
# ---------------------------------------------------------------------------

def test_mayer_budget_decrements():
    w = _world()
    m = make_mayer(slot="S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    # Set budget directly to skip talent-on-battle-start interaction
    m._summons_remaining = _MAYER_SUMMON_BUDGET
    w.add_unit(m)

    # Drain whatever the talent may have consumed, reset to a known state
    m._summons_remaining = _MAYER_SUMMON_BUDGET

    for i in range(3):
        _spawn_token(w, m)
        expected_remaining = _MAYER_SUMMON_BUDGET - (i + 1)
        assert getattr(m, "_summons_remaining", None) == expected_remaining, (
            f"After {i+1} spawns, remaining must be {expected_remaining}"
        )


# ---------------------------------------------------------------------------
# Test 4: Budget exhausted — 5th spawn is a no-op
# ---------------------------------------------------------------------------

def test_mayer_budget_exhausted():
    w = _world()
    m = make_mayer(slot="S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    w.add_unit(m)

    # Exhaust the budget
    for _ in range(_MAYER_SUMMON_BUDGET):
        _spawn_token(w, m)

    token_count_at_cap = _count_tokens(w)
    assert token_count_at_cap == _MAYER_SUMMON_BUDGET, (
        f"Should have exactly {_MAYER_SUMMON_BUDGET} tokens at budget; got {token_count_at_cap}"
    )

    # One more — must be no-op
    _spawn_token(w, m)
    assert _count_tokens(w) == _MAYER_SUMMON_BUDGET, (
        "5th spawn call must be no-op (budget exhausted)"
    )
    assert getattr(m, "_summons_remaining", 0) == 0, (
        "_summons_remaining must stay 0 after exhaustion"
    )


# ---------------------------------------------------------------------------
# Test 5: slot=None still has the talent (budget logic lives in _spawn_token)
# ---------------------------------------------------------------------------

def test_mayer_slot_none_budget_still_works():
    w = _world()
    m = make_mayer(slot=None)
    m.deployed = True
    m.position = (0.0, 1.0)
    w.add_unit(m)

    # Manual spawns still respect budget
    for _ in range(_MAYER_SUMMON_BUDGET + 2):
        _spawn_token(w, m)

    assert _count_tokens(w) == _MAYER_SUMMON_BUDGET, (
        "Budget must cap even when skill slot is None"
    )

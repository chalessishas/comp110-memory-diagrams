"""Ling summon budget cap — max 3 Long Xian per deployment.

Tests cover:
  - Budget constant is correct (3)
  - Fresh operator has no _summons_remaining (lazy init)
  - Each S3 fire decrements budget
  - After 3 S3 fires, 4th on_start is a no-op (no dragon spawned)
  - Budget exhausted: _summons_remaining stays 0
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, Faction, TICK_RATE
from core.systems import register_default_systems
from data.characters.ling import make_ling, _LING_SUMMON_BUDGET, _s3_on_start, _s3_on_end


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _count_dragons(world: World) -> int:
    return sum(
        1 for u in world.units
        if u.name == "Long Xian" and u.alive and u.faction == Faction.ALLY
    )


# ---------------------------------------------------------------------------
# Test 1: Budget constant is correct
# ---------------------------------------------------------------------------

def test_ling_budget_constant():
    assert _LING_SUMMON_BUDGET == 3, "Ling E2 max budget must be 3"


# ---------------------------------------------------------------------------
# Test 2: Fresh operator has no _summons_remaining (lazy init)
# ---------------------------------------------------------------------------

def test_ling_fresh_no_budget_attr():
    l = make_ling(slot="S3")
    assert not hasattr(l, "_summons_remaining"), (
        "_summons_remaining must not be pre-set; lazy-init on first S3 fire"
    )


# ---------------------------------------------------------------------------
# Test 3: Each S3 fire decrements budget
# ---------------------------------------------------------------------------

def test_ling_budget_decrements():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True
    l.position = (0.0, 1.0)
    w.add_unit(l)

    for i in range(_LING_SUMMON_BUDGET):
        _s3_on_start(w, l)
        _s3_on_end(w, l)   # recall dragon so next cast is clean
        expected_remaining = _LING_SUMMON_BUDGET - (i + 1)
        assert getattr(l, "_summons_remaining", None) == expected_remaining, (
            f"After {i+1} S3 fires, remaining must be {expected_remaining}"
        )


# ---------------------------------------------------------------------------
# Test 4: 4th S3 on_start is a no-op — no dragon spawned
# ---------------------------------------------------------------------------

def test_ling_budget_exhausted():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True
    l.position = (0.0, 1.0)
    w.add_unit(l)

    # Use up budget
    for _ in range(_LING_SUMMON_BUDGET):
        _s3_on_start(w, l)
        _s3_on_end(w, l)

    assert getattr(l, "_summons_remaining", 0) == 0

    # 4th fire — must not spawn a new dragon
    _s3_on_start(w, l)
    assert _count_dragons(w) == 0, (
        "After budget exhausted, S3 on_start must not spawn a Long Xian"
    )


# ---------------------------------------------------------------------------
# Test 5: Dragons spawned within budget are live during S3
# ---------------------------------------------------------------------------

def test_ling_dragon_alive_during_s3():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True
    l.position = (0.0, 1.0)
    w.add_unit(l)

    _s3_on_start(w, l)
    assert _count_dragons(w) == 1, "One dragon must be alive during S3"
    assert getattr(l, "_summons_remaining", None) == _LING_SUMMON_BUDGET - 1


# ---------------------------------------------------------------------------
# Test 6: _ling_summon_id is None after budget-exhausted on_start
# ---------------------------------------------------------------------------

def test_ling_summon_id_none_on_budget_exhausted():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True
    l.position = (0.0, 1.0)
    w.add_unit(l)

    for _ in range(_LING_SUMMON_BUDGET):
        _s3_on_start(w, l)
        _s3_on_end(w, l)

    # Budget exhausted — on_start returns early; _ling_summon_id must not be set
    _s3_on_start(w, l)
    assert getattr(l, "_ling_summon_id", None) is None, (
        "_ling_summon_id must remain None when budget exhausted"
    )

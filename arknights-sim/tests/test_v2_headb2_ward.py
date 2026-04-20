"""headb2 (怒潮凛冬) talent "Ward of the Fertile Soil".

Mechanic: Every 9s gains 1 Shield (max 3). Each shield absorbs one complete hit
(regardless of damage amount). When a shield breaks: restore 25% max HP and gain 2 SP.

Tests cover:
  - Shield accumulates after 9s
  - Shield does NOT accumulate before 9s
  - Shield caps at 3 (does not exceed max)
  - Shield absorbs a hit completely (0 damage to HP when shield present)
  - On shield break: HP restored by 25% max HP
  - On shield break: 2 SP granted (capped at sp_cost)
  - Multiple consecutive hits break multiple shields
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind
from core.systems import register_default_systems
from data.characters.headb2 import (
    make_headb2,
    _WARD_TAG, _WARD_SHIELD_INTERVAL, _WARD_MAX_SHIELDS,
    _WARD_HEAL_RATIO, _WARD_SP_GRANT,
)


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ward_shields(h: UnitState) -> int:
    from core.types import StatusKind
    return sum(1 for s in h.statuses if s.kind == StatusKind.SHIELD and s.source_tag == _WARD_TAG)


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _hit(w: World, defender: UnitState, raw_atk: int = 5000) -> int:
    """Simulate one physical hit: take_physical then fire_on_hit_received."""
    from core.systems.talent_registry import fire_on_hit_received
    attacker = make_headb2()  # dummy attacker for callback signature
    dealt = defender.take_physical(raw_atk)
    fire_on_hit_received(w, defender, attacker, dealt)
    return dealt


# ---------------------------------------------------------------------------
# Test 1: Shield does NOT accumulate before 9s
# ---------------------------------------------------------------------------

def test_ward_no_shield_before_interval():
    w = _world()
    h = make_headb2()
    h.deployed = True; h.position = (0.0, 1.0)
    w.add_unit(h)

    _ticks(w, _WARD_SHIELD_INTERVAL - DT)  # just under 9s

    assert _ward_shields(h) == 0, "No Ward shield should accumulate before 9s"


# ---------------------------------------------------------------------------
# Test 2: Shield accumulates after 9s
# ---------------------------------------------------------------------------

def test_ward_shield_accumulates_after_interval():
    w = _world()
    h = make_headb2()
    h.deployed = True; h.position = (0.0, 1.0)
    w.add_unit(h)

    _ticks(w, _WARD_SHIELD_INTERVAL + DT)  # just past 9s

    assert _ward_shields(h) == 1, f"Ward should grant 1 shield after {_WARD_SHIELD_INTERVAL}s"


# ---------------------------------------------------------------------------
# Test 3: Shield caps at _WARD_MAX_SHIELDS
# ---------------------------------------------------------------------------

def test_ward_shield_cap():
    w = _world()
    h = make_headb2()
    h.deployed = True; h.position = (0.0, 1.0)
    w.add_unit(h)

    # Wait long enough for more than 3 shield intervals
    _ticks(w, _WARD_SHIELD_INTERVAL * (_WARD_MAX_SHIELDS + 2) + DT)

    count = _ward_shields(h)
    assert count == _WARD_MAX_SHIELDS, (
        f"Ward shield must cap at {_WARD_MAX_SHIELDS}; got {count}"
    )


# ---------------------------------------------------------------------------
# Test 4: Shield absorbs a hit completely (0 HP lost when shield present)
# ---------------------------------------------------------------------------

def test_ward_shield_absorbs_hit():
    w = _world()
    h = make_headb2()
    h.deployed = True; h.position = (0.0, 1.0)
    h.defence = 0
    w.add_unit(h)

    # Grant 1 shield directly via talent tick
    _ticks(w, _WARD_SHIELD_INTERVAL + DT)
    assert _ward_shields(h) == 1, "Prerequisite: 1 Ward shield"

    hp_before = h.hp
    h.take_physical(5000)

    assert h.hp == hp_before, f"Shield must absorb hit; HP should not change (was {hp_before}, now {h.hp})"


# ---------------------------------------------------------------------------
# Test 5: On shield break — HP restored by 25% max HP
# ---------------------------------------------------------------------------

def test_ward_shield_break_heals():
    w = _world()
    h = make_headb2()
    h.deployed = True; h.position = (0.0, 1.0)
    h.defence = 0
    w.add_unit(h)

    # Reduce HP first so heal is measurable
    h.hp = int(h.max_hp * 0.5)

    # Grant 1 shield
    _ticks(w, _WARD_SHIELD_INTERVAL + DT)
    assert _ward_shields(h) == 1

    hp_before_hit = h.hp
    _hit(w, h, raw_atk=5000)  # breaks the shield

    assert _ward_shields(h) == 0, "Shield should be broken after hit"

    expected_heal = int(h.max_hp * _WARD_HEAL_RATIO)
    # HP after = hp_before_hit + heal (shield absorbed hit so 0 phys damage)
    assert h.hp >= hp_before_hit, "HP must not decrease when shield absorbs hit"
    assert h.hp <= h.max_hp, "HP must not exceed max"
    assert abs(h.hp - (hp_before_hit + expected_heal)) <= 1, (
        f"Ward heal should be {expected_heal}; "
        f"hp went from {hp_before_hit} to {h.hp} (expected {hp_before_hit + expected_heal})"
    )


# ---------------------------------------------------------------------------
# Test 6: On shield break — 2 SP granted (capped at sp_cost)
# ---------------------------------------------------------------------------

def test_ward_shield_break_grants_sp():
    w = _world()
    h = make_headb2(slot="S3")  # has a skill to accumulate SP into
    h.deployed = True; h.position = (0.0, 1.0)
    h.defence = 0
    h.skill.sp = 0.0
    w.add_unit(h)

    # Grant 1 shield
    _ticks(w, _WARD_SHIELD_INTERVAL + DT)
    assert _ward_shields(h) == 1

    sp_before = h.skill.sp
    _hit(w, h, raw_atk=5000)

    assert _ward_shields(h) == 0, "Shield must be broken"
    expected_sp = min(sp_before + _WARD_SP_GRANT, float(h.skill.sp_cost))
    assert abs(h.skill.sp - expected_sp) <= 0.01, (
        f"Ward break must grant {_WARD_SP_GRANT} SP; "
        f"sp went from {sp_before} to {h.skill.sp} (expected {expected_sp})"
    )


# ---------------------------------------------------------------------------
# Test 7: Multiple consecutive hits break multiple shields
# ---------------------------------------------------------------------------

def test_ward_multiple_shields_break_sequentially():
    w = _world()
    h = make_headb2(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0)
    h.defence = 0
    h.skill.sp = 0.0
    h.hp = int(h.max_hp * 0.4)
    w.add_unit(h)

    # Accumulate 2 shields (18s)
    _ticks(w, _WARD_SHIELD_INTERVAL * 2 + DT)
    assert _ward_shields(h) == 2, "Prerequisite: 2 Ward shields"

    sp_before = h.skill.sp
    hp_before = h.hp

    # Two separate hits, each breaking one shield
    _hit(w, h, raw_atk=5000)
    assert _ward_shields(h) == 1, "First hit must break one shield"
    _hit(w, h, raw_atk=5000)
    assert _ward_shields(h) == 0, "Second hit must break second shield"

    # HP should have increased from heals (shield absorbed hits → no phys damage)
    assert h.hp > hp_before, "HP must have increased from Ward heals"
    # 2 shield breaks → 4 SP total
    expected_sp = min(sp_before + _WARD_SP_GRANT * 2, float(h.skill.sp_cost))
    assert abs(h.skill.sp - expected_sp) <= 0.01, (
        f"Two Ward breaks must grant {_WARD_SP_GRANT * 2} SP total; got {h.skill.sp}"
    )

"""Vigna — Fierce Stabbing crit mechanic.

Tests use world.rng = random.Random(seed) for determinism,
or force crit_chance to 0.0 / 1.0 for exact boundary assertions.
"""
from __future__ import annotations
import random
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.vigna import make_vigna, _CRIT_BASE, _CRIT_SKILL
from data.enemies import make_originium_slug


def _world(seed: int = 0) -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    w.rng = random.Random(seed)
    register_default_systems(w)
    return w


def _slug(pos=(0, 1), hp=99999, atk=0):
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_vigna_talent_registered():
    v = make_vigna()
    names = [t.name for t in v.talents]
    assert "Fierce Stabbing" in names
    assert "Charger (DP on kill)" in names


# ---------------------------------------------------------------------------
# Test 2: crit_chance starts at 0 (before any tick)
# ---------------------------------------------------------------------------

def test_crit_chance_zero_before_first_tick():
    v = make_vigna()
    assert v.crit_chance == 0.0


# ---------------------------------------------------------------------------
# Test 3: crit_chance = 10% after tick with no skill
# ---------------------------------------------------------------------------

def test_fierce_stabbing_base_crit_chance():
    """Fierce Stabbing sets crit_chance = 10% when skill is not active."""
    w = _world()
    v = make_vigna()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 999.0
    w.add_unit(v)

    w.tick()

    assert v.crit_chance == _CRIT_BASE, (
        f"Base crit must be {_CRIT_BASE}; got {v.crit_chance}"
    )


# ---------------------------------------------------------------------------
# Test 4: Guaranteed crit deals 1.5× damage (force crit_chance=1.0)
# ---------------------------------------------------------------------------

def test_guaranteed_crit_multiplier():
    """With crit_chance=1.0, every hit deals floor(atk * 1.5 - def) damage."""
    w = _world()
    v = make_vigna()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 0.0
    v.crit_chance = 1.0   # force guaranteed crit every attack
    w.add_unit(v)

    slug = _slug((0, 1), hp=99999)
    w.add_unit(slug)

    hp_before = slug.hp
    # One tick → atk_cd=0 so one attack fires immediately
    w.tick()

    # Expected: floor(v.atk * 1.5) - slug.defence  (min 1)
    crit_raw = int(v.atk * v.crit_multiplier)
    expected_dmg = max(1, crit_raw - slug.defence)
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected_dmg, (
        f"Crit damage must be {expected_dmg}; got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 5: No crit when crit_chance=0.0 — damage equals base physical formula
# ---------------------------------------------------------------------------

def test_zero_crit_chance_deals_base_damage():
    """When crit_chance=0.0, damage = atk - defence (no multiplier)."""
    w = _world()
    v = make_vigna()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 0.0
    v.crit_chance = 0.0
    w.add_unit(v)

    slug = _slug((0, 1), hp=99999)
    w.add_unit(slug)

    hp_before = slug.hp
    w.tick()

    base_dmg = max(1, v.atk - slug.defence)
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == base_dmg, (
        f"Base damage (no crit) must be {base_dmg}; got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 6: Crit probability within expected bounds (100 attacks, seeded RNG)
# ---------------------------------------------------------------------------

def test_fierce_stabbing_crit_rate_statistical():
    """Over 100 attacks with crit_chance=0.10, expect 5–20 crits (seeded rng=42)."""
    w = _world(seed=42)
    v = make_vigna()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 0.0
    v.crit_chance = _CRIT_BASE   # 10%
    w.add_unit(v)

    base_dmg = max(1, v.atk - 0)   # slug.defence=0 for this test
    crit_dmg = int(v.atk * v.crit_multiplier)

    crits = 0
    for _ in range(100):
        slug = _slug((0, 1), hp=99999, atk=0)
        slug.defence = 0   # zero defence for clean measurement
        w.add_unit(slug)
        v.atk_cd = 0.0
        # target must be re-selected — trigger targeting manually
        setattr(v, "__target__", slug)
        setattr(v, "__targets__", [])
        hp_before = slug.hp
        # Fire one attack tick via combat_system directly
        from core.systems.combat_system import combat_system
        combat_system(w, 0.1)
        dmg = hp_before - slug.hp
        if dmg == crit_dmg:
            crits += 1
        w.units.remove(slug)

    # With seed=42 and 10% rate: expected ~10 crits; 5-20 is a safe statistical range
    assert 5 <= crits <= 20, f"Expected 5–20 crits out of 100 with seed=42; got {crits}"

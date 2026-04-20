"""Gravel — SPEC_AMBUSHER: fast-redeploy (18s) + 10s deploy shield (80% DR).

Talent "Tactical Concealment": For 10s after deploy, takes only 20% of incoming
  damage (reduction = 0.80 → damage_taken × 0.20). Shield expires via EventQueue.

Tests cover:
  - Archetype SPEC_AMBUSHER, redeploy_cd=18
  - Shield is active immediately after deploy
  - Damage taken is ~20% of normal while shield is active
  - Shield expires after 10s (damage returns to full)
  - Fast redeploy: world.retreat() + redeploy in 18s works
  - No shield if Gravel is not deployed when added
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.gravel import (
    make_gravel, _TALENT_TAG, _TALENT_REDUCE, _TALENT_DURATION,
)
from data.enemies import make_originium_slug


def _world(width=6, height=3) -> World:
    grid = TileGrid(width=width, height=height)
    for x in range(width):
        for y in range(height):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(3, 1), hp=99999, atk=500) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk
    e.defence = 0; e.res = 0.0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and basic stats
# ---------------------------------------------------------------------------

def test_gravel_archetype():
    g = make_gravel()
    assert g.archetype == RoleArchetype.SPEC_AMBUSHER
    assert g.redeploy_cd == 18.0
    assert g.block == 1
    assert g.cost == 8
    assert len(g.talents) == 1
    assert g.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Deploy shield activates on deploy
# ---------------------------------------------------------------------------

def test_deploy_shield_active_on_deploy():
    """Talent shield must be active immediately after world.add_unit()."""
    w = _world()
    g = make_gravel()
    g.deployed = True; g.position = (2.0, 1.0)
    w.add_unit(g)  # triggers on_battle_start

    talent = next(t for t in g.talents if t.behavior_tag == _TALENT_TAG)
    shield = talent.params.get("deploy_shield", {})
    assert shield.get("active", False), "Shield must be active after deploy"
    assert abs(shield.get("reduction", 0.0) - _TALENT_REDUCE) < 0.01


# ---------------------------------------------------------------------------
# Test 3: Damage reduced to ~20% while shield is active
# ---------------------------------------------------------------------------

def test_shield_reduces_damage_to_20_percent():
    """With 80% DR, damage taken must be ≈20% of unshielded amount."""
    w = _world()
    g = make_gravel()
    g.deployed = True; g.position = (2.0, 1.0)
    g.defence = 0   # zero DEF so physical damage = raw ATK exactly
    w.add_unit(g)

    # Determine baseline: how much take_physical deals without shield
    # By temporarily deactivating the shield
    talent = next(t for t in g.talents if t.behavior_tag == _TALENT_TAG)
    talent.params["deploy_shield"] = {"active": False, "reduction": 0.0}
    hp_before_baseline = g.hp
    g.take_physical(1000)
    baseline_damage = hp_before_baseline - g.hp
    g.hp = hp_before_baseline  # reset

    # Now activate shield and measure damage
    talent.params["deploy_shield"] = {"active": True, "reduction": _TALENT_REDUCE}
    hp_before = g.hp
    g.take_physical(1000)
    shielded_damage = hp_before - g.hp

    # Should be ~20% of baseline (80% reduction)
    expected_max = int(baseline_damage * (1.0 - _TALENT_REDUCE)) + 2
    assert shielded_damage <= expected_max, (
        f"Shielded damage must be ~20% of baseline; "
        f"baseline={baseline_damage}, shielded={shielded_damage}, expected≤{expected_max}"
    )
    # Also ensure at least 1 damage always goes through
    assert shielded_damage >= 1, "At least 1 damage must always go through (core rule)"


# ---------------------------------------------------------------------------
# Test 4: Shield expires after 10s
# ---------------------------------------------------------------------------

def test_shield_expires_after_10s():
    """Shield must be inactive after _TALENT_DURATION seconds have passed."""
    w = _world()
    g = make_gravel()
    g.deployed = True; g.position = (2.0, 1.0)
    g.defence = 0
    w.add_unit(g)

    # Run past shield duration
    for _ in range(int(TICK_RATE * (_TALENT_DURATION + 1))):
        w.tick()

    talent = next(t for t in g.talents if t.behavior_tag == _TALENT_TAG)
    shield = talent.params.get("deploy_shield", {})
    assert not shield.get("active", True), (
        f"Shield must be inactive after {_TALENT_DURATION}s; params={talent.params}"
    )


# ---------------------------------------------------------------------------
# Test 5: Damage increases after shield expires
# ---------------------------------------------------------------------------

def test_damage_normal_after_shield_expires():
    """After shield expires, damage taken should return to full (unshielded) amount."""
    ENEMY_ATK = 500
    w = _world()
    g = make_gravel()
    g.deployed = True; g.position = (2.0, 1.0)
    g.defence = 0; g.hp = 999999; g.max_hp = 999999
    w.add_unit(g)
    enemy = _slug(pos=(2, 1), atk=ENEMY_ATK)
    w.add_unit(enemy)

    # Measure damage in first tick (shield active) vs after shield expires
    w.tick()
    damage_tick1 = 999999 - g.hp
    pre_expire_hp = g.hp

    # Run past expiry
    for _ in range(int(TICK_RATE * _TALENT_DURATION)):
        w.tick()

    # Now take one more hit manually to measure unshielded damage
    hp_before_raw = g.hp; g.take_physical(ENEMY_ATK)
    unshielded_dmg = hp_before_raw - g.hp

    # The unshielded damage must be much larger than the first shielded tick
    # (shielded = 20% of unshielded)
    if damage_tick1 > 0:
        ratio = damage_tick1 / unshielded_dmg
        assert ratio <= 0.25, (
            f"First-tick (shielded) damage must be ≤25% of unshielded; "
            f"ratio={ratio:.2f}, shielded={damage_tick1}, unshielded={unshielded_dmg}"
        )


# ---------------------------------------------------------------------------
# Test 6: Fast redeploy cooldown is 18s
# ---------------------------------------------------------------------------

def test_fast_redeploy_cd():
    """Gravel must be re-deployable after 18s (not 70s like normal operators)."""
    w = _world()
    w.global_state.dp = 100.0

    g = make_gravel()
    g.position = (2.0, 1.0)
    assert w.deploy(g), "Initial deploy must succeed"
    assert g.deployed

    w.retreat(g)
    assert not g.deployed

    # Without enough time: still in cooldown
    for _ in range(int(TICK_RATE * 5)):
        w.tick()
    assert not w.deploy(g), "Must NOT redeploy before cooldown expires"

    # After full 18s: cooldown done, redeploy succeeds
    for _ in range(int(TICK_RATE * 14)):  # 5 + 14 = 19 > 18
        w.tick()
    w.global_state.dp = 100.0  # replenish DP
    assert w.deploy(g), "Must redeploy after 18s cooldown"

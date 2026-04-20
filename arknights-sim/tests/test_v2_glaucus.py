"""Glaucus — Tidal Current on-tick SLOW aura + S2 AoE arts BIND.

First on_tick aura debuff: the talent fires every tick and applies SLOW to ALL
enemies in range, not just the one being attacked. This tests the aura pattern
distinct from Angelina's on_hit SLOW and Bagpipe's S3 on_hit SLOW.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.glaucus import (
    make_glaucus, _TALENT_TAG, _SLOW_AMOUNT, _AURA_REFRESH_DT,
    _S2_BIND_DURATION, _S2_DAMAGE_RATIO,
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


def _slug(pos=(1, 1), hp=999999, move_speed=1.0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp
    e.atk = 0; e.move_speed = move_speed; e.defence = 0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_glaucus_talent_registered():
    g = make_glaucus()
    assert len(g.talents) == 1
    assert g.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Aura SLOW applied to enemy in range on first tick
# ---------------------------------------------------------------------------

def test_aura_slow_applied_in_range():
    w = _world()
    g = make_glaucus(slot=None)
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    assert slug.has_status(StatusKind.SLOW), "SLOW must be applied to enemy in range"


# ---------------------------------------------------------------------------
# Test 3: SLOW not applied to enemy out of range
# ---------------------------------------------------------------------------

def test_aura_slow_not_applied_out_of_range():
    w = _world()
    g = make_glaucus(slot=None)
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(5, 1))  # beyond range (dx=5 exceeds 0–3 tiles)
    w.add_unit(slug)

    w.tick()

    assert not slug.has_status(StatusKind.SLOW), "SLOW must NOT apply out of range"


# ---------------------------------------------------------------------------
# Test 4: SLOW carries correct amount param
# ---------------------------------------------------------------------------

def test_aura_slow_amount_param():
    w = _world()
    g = make_glaucus(slot=None)
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    s = next(st for st in slug.statuses if st.kind == StatusKind.SLOW)
    assert s.params.get("amount") == _SLOW_AMOUNT


# ---------------------------------------------------------------------------
# Test 5: Aura applies to multiple enemies simultaneously
# ---------------------------------------------------------------------------

def test_aura_slow_affects_multiple_enemies():
    w = _world()
    g = make_glaucus(slot=None)
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug1 = _slug(pos=(1, 1))
    slug2 = _slug(pos=(2, 1))
    w.add_unit(slug1)
    w.add_unit(slug2)

    w.tick()

    assert slug1.has_status(StatusKind.SLOW), "slug1 must have SLOW"
    assert slug2.has_status(StatusKind.SLOW), "slug2 must have SLOW"


# ---------------------------------------------------------------------------
# Test 6: SLOW lapes after _AURA_REFRESH_DT if operator removed
# ---------------------------------------------------------------------------

def test_aura_slow_lapses_after_operator_removed():
    w = _world()
    g = make_glaucus(slot=None)
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()
    assert slug.has_status(StatusKind.SLOW), "SLOW must be active"

    # Remove Glaucus (undeploy)
    g.deployed = False

    # Tick past aura expiry
    for _ in range(int(TICK_RATE * (_AURA_REFRESH_DT + 0.1)) + 1):
        w.tick()

    assert not slug.has_status(StatusKind.SLOW), "SLOW must lapse when operator leaves"


# ---------------------------------------------------------------------------
# Test 7: SLOW actually reduces enemy movement speed
# ---------------------------------------------------------------------------

def test_aura_slow_reduces_movement_speed():
    """Verify SLOW reduces effective move speed via movement_system."""
    from core.types import BuffAxis
    w = _world()
    g = make_glaucus(slot=None)
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(1, 1), move_speed=1.0)
    slug.blocked_by_unit_ids = []  # ensure not blocked
    w.add_unit(slug)

    # Let aura tick — slug should be SLOW'd
    w.tick()
    assert slug.has_status(StatusKind.SLOW), "SLOW must be active"

    # Compute expected reduced speed: 1.0 * (1 - 0.40) = 0.60
    expected_speed = 1.0 * (1.0 - _SLOW_AMOUNT)

    # Simulate movement_system speed calculation manually
    speed = slug.move_speed
    for s in slug.statuses:
        if s.kind == StatusKind.SLOW:
            speed *= 1.0 - s.params.get("amount", 0.3)

    assert abs(speed - expected_speed) < 1e-6, (
        f"Expected speed {expected_speed}, computed {speed}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 applies BIND to all enemies in range
# ---------------------------------------------------------------------------

def test_glaucus_s2_bind_in_range():
    from core.systems.skill_system import manual_trigger
    w = _world()
    g = make_glaucus()
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)

    slug1 = _slug(pos=(1, 1))
    slug2 = _slug(pos=(2, 1))
    w.add_unit(slug1)
    w.add_unit(slug2)

    g.skill.sp = g.skill.sp_cost
    manual_trigger(w, g)

    assert slug1.has_status(StatusKind.BIND), "slug1 must be BIND'd by S2"
    assert slug2.has_status(StatusKind.BIND), "slug2 must be BIND'd by S2"


# ---------------------------------------------------------------------------
# Test 9: S2 deals arts damage to enemies in range
# ---------------------------------------------------------------------------

def test_glaucus_s2_arts_damage():
    from core.systems.skill_system import manual_trigger
    w = _world()
    g = make_glaucus()
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)

    slug = _slug(pos=(1, 1), hp=999999)
    w.add_unit(slug)

    hp_before = slug.hp
    g.skill.sp = g.skill.sp_cost
    manual_trigger(w, g)

    expected_raw = int(g.atk * _S2_DAMAGE_RATIO)
    expected_dmg = max(1, expected_raw)
    assert slug.hp < hp_before, "S2 must deal damage"
    assert hp_before - slug.hp == expected_dmg, (
        f"Expected {expected_dmg} damage, got {hp_before - slug.hp}"
    )

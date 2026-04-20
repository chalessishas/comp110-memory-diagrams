"""Meteorite — SNIPER_ARTILLERY: physical splash trait + Landing Blast DEF_DOWN + S2.

SNIPER_ARTILLERY trait: Each attack deals physical splash to enemies within 1.1 tiles
  of the primary target.

Talent "Landing Blast": Primary target gets DEF -10% for 6s on each hit.

S2 "Shock Zone": ATK +50%, splash radius increases from 1.1 to 1.8 tiles.

Tests cover:
  - Archetype is SNIPER_ARTILLERY
  - Normal attack hits primary target
  - Splash hits adjacent enemy (within 1.1 tiles of primary)
  - Splash does NOT hit enemy far from primary target
  - Talent DEF_DOWN applied on hit to primary target
  - DEF_DOWN reduces effective DEF
  - DEF_DOWN expires after duration
  - S2 increases ATK by 50%
  - S2 increases splash radius to 1.8
  - S2 splash_radius restored on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind, RoleArchetype
from core.systems import register_default_systems
from data.characters.meteo import (
    make_meteo,
    _TALENT_TAG, _TALENT_DEF_DOWN_RATIO, _TALENT_DEF_DOWN_DURATION, _TALENT_DEF_DOWN_TAG,
    _BASE_SPLASH_RADIUS, _S2_ATK_RATIO, _S2_SPLASH_RADIUS, _S2_DURATION,
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


def _slug(pos=(3, 1), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = 0.0
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype SNIPER_ARTILLERY
# ---------------------------------------------------------------------------

def test_meteo_archetype():
    m = make_meteo()
    assert m.archetype == RoleArchetype.SNIPER_ARTILLERY
    assert m.splash_radius == _BASE_SPLASH_RADIUS, "Must have base splash radius"
    assert m.splash_atk_multiplier == 1.0


# ---------------------------------------------------------------------------
# Test 2: Normal attack hits primary target
# ---------------------------------------------------------------------------

def test_attack_hits_primary():
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    primary = _slug(pos=(3, 1), hp=99999, defence=0)
    initial_hp = primary.hp
    w.add_unit(primary)

    w.tick()

    assert primary.hp < initial_hp, "Meteorite must hit primary target"


# ---------------------------------------------------------------------------
# Test 3: Splash hits adjacent enemy
# ---------------------------------------------------------------------------

def test_splash_hits_adjacent():
    """Enemy within 1.1 tiles of primary must take splash damage."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    primary = _slug(pos=(3, 1), hp=99999, defence=0)
    splash_target = _slug(pos=(3, 2), hp=99999, defence=0)   # 1 tile from primary (y+1)
    w.add_unit(primary)
    w.add_unit(splash_target)

    w.tick()

    assert primary.hp < primary.max_hp, "Primary must take damage"
    assert splash_target.hp < splash_target.max_hp, (
        "Enemy adjacent to primary must take splash damage (SNIPER_ARTILLERY trait)"
    )


# ---------------------------------------------------------------------------
# Test 4: Splash does NOT hit enemy far from primary
# ---------------------------------------------------------------------------

def test_splash_no_damage_far_enemy():
    """Enemy well outside splash radius must not take damage."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    primary = _slug(pos=(3, 1), hp=99999, defence=0)
    far = _slug(pos=(7, 1), hp=99999, defence=0)    # 4 tiles from primary
    w.add_unit(primary)
    w.add_unit(far)

    w.tick()

    assert primary.hp < primary.max_hp
    assert far.hp == far.max_hp, "Far enemy must NOT take splash damage"


# ---------------------------------------------------------------------------
# Test 5: Talent applies DEF_DOWN on hit
# ---------------------------------------------------------------------------

def test_talent_def_down_on_hit():
    """Landing Blast must apply DEF_DOWN status to the primary target on each hit."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    enemy = _slug(pos=(3, 1), hp=99999, defence=200)
    w.add_unit(enemy)

    w.tick()

    assert enemy.has_status(StatusKind.DEF_DOWN), (
        "Landing Blast must apply DEF_DOWN to primary target on hit"
    )
    dd = next(s for s in enemy.statuses if s.kind == StatusKind.DEF_DOWN)
    assert dd.source_tag == _TALENT_DEF_DOWN_TAG


# ---------------------------------------------------------------------------
# Test 6: DEF_DOWN reduces effective DEF
# ---------------------------------------------------------------------------

def test_talent_def_down_reduces_def():
    """DEF_DOWN must reduce the target's effective DEF."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    enemy = _slug(pos=(3, 1), hp=99999, defence=500)
    base_def = enemy.effective_def
    w.add_unit(enemy)

    w.tick()

    assert enemy.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must be applied"
    assert enemy.effective_def < base_def, (
        f"DEF must be reduced; base={base_def}, now={enemy.effective_def}"
    )
    expected_def = int(base_def * (1 - _TALENT_DEF_DOWN_RATIO))
    assert abs(enemy.effective_def - expected_def) <= 2


# ---------------------------------------------------------------------------
# Test 7: DEF_DOWN expires after duration
# ---------------------------------------------------------------------------

def test_talent_def_down_expires():
    """DEF_DOWN must expire after _TALENT_DEF_DOWN_DURATION."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    enemy = _slug(pos=(3, 1), hp=99999, defence=200)
    w.add_unit(enemy)

    w.tick()
    assert enemy.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must be active initially"

    m.atk_cd = 999.0  # prevent re-application during expiry window
    for _ in range(int(TICK_RATE * (_TALENT_DEF_DOWN_DURATION + 1))):
        w.tick()

    assert not enemy.has_status(StatusKind.DEF_DOWN), (
        f"DEF_DOWN must expire after {_TALENT_DEF_DOWN_DURATION}s"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 increases ATK by 50%
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 Shock Zone must increase ATK by _S2_ATK_RATIO."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(3, 1))
    w.add_unit(enemy)

    base_atk = m.effective_atk
    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(m.effective_atk - expected_atk) <= 2, (
        f"S2 ATK must be ×{1+_S2_ATK_RATIO}; expected={expected_atk}, got={m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 9: S2 increases splash radius
# ---------------------------------------------------------------------------

def test_s2_increases_splash_radius():
    """During S2, splash_radius must increase to _S2_SPLASH_RADIUS."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(3, 1))
    w.add_unit(enemy)

    assert m.splash_radius == _BASE_SPLASH_RADIUS, "Base splash radius must be set"

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0
    assert m.splash_radius == _S2_SPLASH_RADIUS, (
        f"S2 must increase splash radius to {_S2_SPLASH_RADIUS}; got {m.splash_radius}"
    )


# ---------------------------------------------------------------------------
# Test 10: S2 splash_radius restored on end
# ---------------------------------------------------------------------------

def test_s2_splash_radius_restored():
    """After S2 ends, splash_radius must return to _BASE_SPLASH_RADIUS."""
    w = _world()
    m = make_meteo()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(3, 1))
    w.add_unit(enemy)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()
    assert m.splash_radius == _S2_SPLASH_RADIUS

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert m.skill.active_remaining == 0.0, "S2 must have ended"
    assert m.splash_radius == _BASE_SPLASH_RADIUS, (
        f"splash_radius must return to {_BASE_SPLASH_RADIUS} after S2"
    )

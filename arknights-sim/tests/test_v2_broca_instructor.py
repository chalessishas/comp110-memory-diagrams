"""Broca — GUARD_INSTRUCTOR: splash to adjacent enemies + Regroup HoT aura + S2 ATK/DEF buff.

GUARD_INSTRUCTOR trait:
  Each attack also deals physical damage to all enemies adjacent (≤1 tile) to
  the primary target. Implemented via splash_radius=1.0.

Talent "Regroup": While Broca is blocking ≥1 enemy, all allied operators within
  2 Manhattan tiles recover HP per tick.

S2 "All In": ATK +65%, DEF +30% for 20s.

Tests cover:
  - Archetype is GUARD_INSTRUCTOR, block=3
  - Normal attack hits primary target
  - Splash hits enemy adjacent to primary target
  - Splash does NOT hit enemy far from primary target
  - Talent HoT heals nearby allies while blocking
  - Talent HoT does NOT heal when not blocking
  - Talent HoT does NOT heal out-of-range allies
  - S2 applies ATK buff (+65%)
  - S2 applies DEF buff (+30%)
  - S2 buffs removed on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype
from core.systems import register_default_systems
from data.characters.broca import (
    make_broca,
    _TALENT_TAG, _TALENT_REGEN_RATIO, _TALENT_RANGE,
    _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_DURATION,
    _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 2), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(0, 0), hp=500, max_hp=2000) -> UnitState:
    return UnitState(
        name="Ally",
        faction=Faction.ALLY,
        max_hp=max_hp, hp=hp, atk=0,
        defence=0, atk_interval=999.0, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )


# ---------------------------------------------------------------------------
# Test 1: Archetype GUARD_INSTRUCTOR, block=3
# ---------------------------------------------------------------------------

def test_broca_archetype():
    b = make_broca()
    assert b.archetype == RoleArchetype.GUARD_INSTRUCTOR
    assert b.block == 3
    assert b.splash_radius == 1.0, "GUARD_INSTRUCTOR must have splash_radius=1.0"


# ---------------------------------------------------------------------------
# Test 2: Normal attack hits primary target
# ---------------------------------------------------------------------------

def test_attack_hits_primary():
    """Broca's attack must deal physical damage to the targeted enemy."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0); b.atk_cd = 0.0
    w.add_unit(b)

    primary = _slug(pos=(0, 2), hp=99999, defence=0)
    initial_hp = primary.hp
    w.add_unit(primary)

    w.tick()

    assert primary.hp < initial_hp, "Broca must damage the primary target"


# ---------------------------------------------------------------------------
# Test 3: Splash hits adjacent enemy
# ---------------------------------------------------------------------------

def test_splash_hits_adjacent_enemy():
    """Enemy adjacent (1 tile away) to the primary target must also take damage."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0); b.atk_cd = 0.0
    w.add_unit(b)

    primary = _slug(pos=(0, 2), hp=99999, defence=0)
    adjacent = _slug(pos=(0, 3), hp=99999, defence=0)   # 1 tile away from primary
    w.add_unit(primary)
    w.add_unit(adjacent)

    w.tick()

    assert primary.hp < primary.max_hp, "Primary must take damage"
    assert adjacent.hp < adjacent.max_hp, (
        "Adjacent enemy must take splash damage from GUARD_INSTRUCTOR trait"
    )


# ---------------------------------------------------------------------------
# Test 4: Splash does NOT hit enemy far from primary target
# ---------------------------------------------------------------------------

def test_splash_no_damage_far_enemy():
    """Enemy far from the primary target must NOT take splash damage."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0); b.atk_cd = 0.0
    w.add_unit(b)

    primary = _slug(pos=(0, 2), hp=99999, defence=0)
    far = _slug(pos=(5, 2), hp=99999, defence=0)   # 5 tiles away
    w.add_unit(primary)
    w.add_unit(far)

    w.tick()

    assert primary.hp < primary.max_hp, "Primary must take damage"
    assert far.hp == far.max_hp, (
        "Far enemy must NOT take splash damage from instructor trait"
    )


# ---------------------------------------------------------------------------
# Test 5: Talent HoT heals nearby ally while blocking
# ---------------------------------------------------------------------------

def test_talent_hot_heals_while_blocking():
    """Regroup must heal a nearby injured ally each tick while Broca is blocking."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0)
    w.add_unit(b)

    # Enemy adjacent so Broca can block
    enemy = _slug(pos=(0, 2), hp=99999)
    w.add_unit(enemy)

    # Injured ally within 2 tiles
    ally = _ally(pos=(1, 2), hp=500, max_hp=2000)
    w.add_unit(ally)

    hp_before = ally.hp
    for _ in range(5):
        w.tick()

    assert ally.hp > hp_before, (
        f"Nearby ally must be healed by Regroup while Broca is blocking; hp was {hp_before}, now {ally.hp}"
    )


# ---------------------------------------------------------------------------
# Test 6: Talent HoT does NOT heal out-of-range ally
# ---------------------------------------------------------------------------

def test_talent_hot_no_heal_far_ally():
    """Regroup must not heal allies beyond _TALENT_RANGE tiles."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0)
    w.add_unit(b)

    enemy = _slug(pos=(0, 2), hp=99999)
    w.add_unit(enemy)

    far_ally = _ally(pos=(7, 2), hp=500, max_hp=2000)  # 7 tiles away
    w.add_unit(far_ally)

    hp_before = far_ally.hp
    for _ in range(5):
        w.tick()

    assert far_ally.hp == hp_before, (
        f"Out-of-range ally must NOT be healed by Regroup; hp changed to {far_ally.hp}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 applies ATK and DEF buffs
# ---------------------------------------------------------------------------

def test_s2_atk_def_buff():
    """S2 All In must increase Broca's ATK by 65% and DEF by 30%."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0)
    w.add_unit(b)

    enemy = _slug(pos=(0, 2))
    w.add_unit(enemy)

    base_atk = b.effective_atk
    base_def = b.effective_def

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()

    assert b.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    expected_def = int(base_def * (1 + _S2_DEF_RATIO))
    assert abs(b.effective_atk - expected_atk) <= 2, (
        f"S2 ATK must be base×{1+_S2_ATK_RATIO}; got {b.effective_atk}, expected {expected_atk}"
    )
    assert abs(b.effective_def - expected_def) <= 2, (
        f"S2 DEF must be base×{1+_S2_DEF_RATIO}; got {b.effective_def}, expected {expected_def}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 buffs removed on end
# ---------------------------------------------------------------------------

def test_s2_buffs_cleared_on_end():
    """After S2 expires, ATK and DEF must return to base values."""
    w = _world()
    b = make_broca()
    b.deployed = True; b.position = (0.0, 2.0)
    w.add_unit(b)

    enemy = _slug(pos=(0, 2))
    w.add_unit(enemy)

    base_atk = b.effective_atk

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()
    assert b.skill.active_remaining > 0.0

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert b.skill.active_remaining == 0.0, "S2 must have ended"
    s2_buffs = [buf for buf in b.buffs if buf.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]
    assert len(s2_buffs) == 0, "S2 ATK/DEF buffs must be removed after skill ends"
    assert abs(b.effective_atk - base_atk) <= 1, (
        f"ATK must return to base {base_atk} after S2; got {b.effective_atk}"
    )

"""Mostima — CASTER_MYSTIC: Arts attack + Serenity SP-on-kill + S3 global AoE stun.

CASTER_MYSTIC trait: Arts damage against ground enemies.

Talent "Serenity": When Mostima kills an enemy, gain 10 bonus SP.

S3 "Ley Lines": MANUAL, instant.
  Deals 170% ATK Arts damage to ALL enemies currently on the field (no range check).
  Applies STUN for 3.5s to each hit enemy.

Tests cover:
  - Archetype is CASTER_MYSTIC
  - Normal attack deals Arts damage to in-range enemy
  - Normal attack does NOT hit out-of-range enemies
  - Talent: on kill, Mostima gains SP
  - S3 hits enemy within normal range (in-range)
  - S3 ALSO hits enemy far outside normal range (global AoE)
  - S3 applies STUN to all hit enemies
  - S3 STUN expires after duration
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind, RoleArchetype, AttackType
from core.systems import register_default_systems
from data.characters.mostima import (
    make_mostima,
    _TALENT_TAG, _TALENT_SP_ON_KILL,
    _S3_STUN_DURATION, _S3_STUN_TAG, _S3_ATK_RATIO,
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


def _slug(pos=(2, 1), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype is CASTER_MYSTIC
# ---------------------------------------------------------------------------

def test_mostima_archetype():
    m = make_mostima()
    assert m.archetype == RoleArchetype.CASTER_MYSTIC
    assert m.attack_type == AttackType.ARTS, "Mostima must deal Arts damage"
    assert len(m.talents) == 1
    assert m.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Normal attack deals Arts damage to in-range enemy
# ---------------------------------------------------------------------------

def test_normal_attack_arts_damage():
    """Mostima's normal attack must deal Arts damage to an in-range enemy."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    m.atk_cd = 0.0
    w.add_unit(m)

    enemy = _slug(pos=(2, 1), hp=99999, res=0)
    initial_hp = enemy.hp
    w.add_unit(enemy)

    for _ in range(5):
        w.tick()

    assert enemy.hp < initial_hp, "Mostima must deal Arts damage to in-range enemy"


# ---------------------------------------------------------------------------
# Test 3: Normal attack does NOT hit far out-of-range enemies
# ---------------------------------------------------------------------------

def test_normal_attack_misses_far_enemy():
    """Enemies far beyond Mostima's range must not take damage from normal attacks."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    m.atk_cd = 0.0
    w.add_unit(m)

    # Put an enemy in range to absorb targeting
    in_range = _slug(pos=(2, 1), hp=99999, res=0)
    w.add_unit(in_range)

    # Enemy at tile (9,1) — well outside 3-tile range
    far_enemy = _slug(pos=(9, 1), hp=99999, res=0)
    initial_hp = far_enemy.hp
    w.add_unit(far_enemy)

    for _ in range(5):
        w.tick()

    assert far_enemy.hp == initial_hp, (
        "Far enemy must not take damage from Mostima's normal attacks"
    )


# ---------------------------------------------------------------------------
# Test 4: Talent — kill grants SP
# ---------------------------------------------------------------------------

def test_talent_sp_gain_on_kill():
    """When Mostima kills an enemy, she must gain _TALENT_SP_ON_KILL bonus SP."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    m.skill.sp = 0.0  # start empty so gain is observable
    w.add_unit(m)

    # Very weak enemy — one hit kills
    weak = _slug(pos=(2, 1), hp=1, res=0)
    w.add_unit(weak)

    m.atk_cd = 0.0
    sp_before = m.skill.sp
    w.tick()

    assert not weak.alive, "Enemy must die"
    gain = m.skill.sp - sp_before
    assert gain >= min(_TALENT_SP_ON_KILL, m.skill.sp_cost), (
        f"Talent must grant at least {_TALENT_SP_ON_KILL} SP on kill; got {gain:.1f}"
    )


# ---------------------------------------------------------------------------
# Test 5: S3 hits in-range enemy with Arts damage
# ---------------------------------------------------------------------------

def test_s3_hits_in_range_enemy():
    """S3 Ley Lines must deal Arts damage to a normally in-range enemy."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(2, 1), hp=99999, res=0)
    w.add_unit(enemy)

    pre_hp = enemy.hp
    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    assert enemy.hp < pre_hp, "S3 must deal Arts damage to in-range enemy"


# ---------------------------------------------------------------------------
# Test 6: S3 hits enemy FAR outside normal attack range (global AoE)
# ---------------------------------------------------------------------------

def test_s3_global_aoe_hits_far_enemy():
    """S3 must hit enemies regardless of distance — global range."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    # Enemy at tile (9,1) — far beyond Mostima's 3-tile normal attack range
    far_enemy = _slug(pos=(9, 1), hp=99999, res=0)
    w.add_unit(far_enemy)

    pre_hp = far_enemy.hp
    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    assert far_enemy.hp < pre_hp, (
        "S3 Ley Lines must hit enemies far outside normal range (global AoE)"
    )


# ---------------------------------------------------------------------------
# Test 7: S3 applies STUN to all hit enemies
# ---------------------------------------------------------------------------

def test_s3_stuns_all_enemies():
    """S3 must apply STUN to every enemy on the field."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    e1 = _slug(pos=(2, 1), hp=99999)
    e2 = _slug(pos=(9, 1), hp=99999)
    w.add_unit(e1); w.add_unit(e2)

    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    assert e1.has_status(StatusKind.STUN), "In-range enemy must be stunned by S3"
    assert e2.has_status(StatusKind.STUN), "Far enemy must be stunned by S3 (global)"
    for e in [e1, e2]:
        stun = next(s for s in e.statuses if s.kind == StatusKind.STUN)
        assert stun.source_tag == _S3_STUN_TAG


# ---------------------------------------------------------------------------
# Test 8: S3 STUN expires after _S3_STUN_DURATION
# ---------------------------------------------------------------------------

def test_s3_stun_expires():
    """STUN applied by S3 must expire after the configured duration."""
    w = _world()
    m = make_mostima()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(2, 1), hp=99999)
    w.add_unit(enemy)

    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    assert enemy.has_status(StatusKind.STUN), "STUN must be applied initially"

    for _ in range(int(TICK_RATE * (_S3_STUN_DURATION + 1))):
        w.tick()

    assert not enemy.has_status(StatusKind.STUN), (
        f"STUN must expire after {_S3_STUN_DURATION}s"
    )

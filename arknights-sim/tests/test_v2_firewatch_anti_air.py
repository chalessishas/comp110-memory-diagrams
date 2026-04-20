"""Firewatch — SNIPER_ANTI_AIR targeting priority + S2 Flash Arrow STUN."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Mobility, StatusKind, TICK_RATE, Faction, AttackType
from core.systems import register_default_systems
from data.characters.firewatch import make_firewatch
from data.enemies import make_originium_slug, make_drone


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileGrid(width=1, height=1) and TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _make_world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(progress=3.0, hp=9999):
    path = [(x, 1) for x in range(10)]
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.deployed = True; e.path_progress = progress
    e.position = (float(path[int(progress)][0]), float(path[int(progress)][1]))
    return e


def _drone(progress=3.0, hp=9999):
    path = [(x, 1) for x in range(10)]
    e = make_drone(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.deployed = True; e.path_progress = progress
    e.position = (float(path[int(progress)][0]), float(path[int(progress)][1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype
# ---------------------------------------------------------------------------

def test_firewatch_archetype():
    from core.types import RoleArchetype
    fw = make_firewatch()
    assert fw.archetype == RoleArchetype.SNIPER_ANTI_AIR
    assert fw.attack_range_melee is False


# ---------------------------------------------------------------------------
# Test 2: Melee operator CANNOT target airborne enemy
# ---------------------------------------------------------------------------

def test_melee_cannot_target_airborne():
    """A melee operator must not attack a drone even when it is in range."""
    from data.characters import make_liskarm
    w = _make_world()
    lk = make_liskarm()
    lk.deployed = True; lk.position = (1.0, 1.0); lk.atk_cd = 0.0
    w.add_unit(lk)

    d = _drone(progress=1.0, hp=9999)
    w.add_unit(d)

    hp_before = d.hp
    for _ in range(10):
        w.tick()

    assert d.hp == hp_before, (
        f"Melee operator must not damage aerial drone; hp={d.hp}/{hp_before}"
    )


# ---------------------------------------------------------------------------
# Test 3: Ranged operator CAN target airborne enemy
# ---------------------------------------------------------------------------

def test_ranged_can_target_airborne():
    """Firewatch (ranged) must damage a drone in range."""
    w = _make_world()
    fw = make_firewatch()
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 0.0
    w.add_unit(fw)

    d = _drone(progress=2.0, hp=9999)
    w.add_unit(d)

    hp_before = d.hp
    for _ in range(10):
        w.tick()

    assert d.hp < hp_before, "Firewatch must damage airborne drone"


# ---------------------------------------------------------------------------
# Test 4: SNIPER_ANTI_AIR prefers airborne over ground when both in range
# ---------------------------------------------------------------------------

def test_anti_air_prefers_airborne_target():
    """When both a slug and a drone are in range, Firewatch attacks the drone first."""
    w = _make_world()
    fw = make_firewatch()
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 0.0
    w.add_unit(fw)

    slug = _slug(progress=2.0, hp=9999)   # lower path progress (closer to start)
    drone = _drone(progress=3.0, hp=9999)   # farther along path
    w.add_unit(slug)
    w.add_unit(drone)

    hp_slug_before = slug.hp
    hp_drone_before = drone.hp
    w.tick()  # one tick: Firewatch fires once

    # Drone should be damaged; slug should not (Anti-Air prefers aerial)
    assert drone.hp < hp_drone_before, "Anti-Air must target drone preferentially"
    assert slug.hp == hp_slug_before, "Anti-Air must NOT target slug when drone is present"


# ---------------------------------------------------------------------------
# Test 5: SNIPER_ANTI_AIR falls back to ground when no aerial in range
# ---------------------------------------------------------------------------

def test_anti_air_fallback_to_ground():
    """When no drone is in range, Firewatch targets the ground slug."""
    w = _make_world()
    fw = make_firewatch()
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 0.0
    w.add_unit(fw)

    slug = _slug(progress=2.0, hp=9999)
    w.add_unit(slug)

    hp_before = slug.hp
    w.tick()

    assert slug.hp < hp_before, "Anti-Air must fall back to ground targets when no aerial"


# ---------------------------------------------------------------------------
# Test 6: First Target talent — ATK buff active while targeting aerial
# ---------------------------------------------------------------------------

def test_first_target_talent_registered():
    from core.systems.talent_registry import _REGISTRY
    fw = make_firewatch()
    tag = fw.talents[0].behavior_tag
    assert tag in _REGISTRY, f"First Target talent not registered: {tag}"


def test_first_target_buff_active_vs_aerial():
    """ATK+30% buff is present while Firewatch targets an aerial enemy."""
    from core.types import BuffAxis
    w = _make_world()
    fw = make_firewatch()
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 999.0
    w.add_unit(fw)

    drone = _drone(progress=2.0, hp=9999999)
    w.add_unit(drone)

    w.tick()  # talent on_tick fires

    atk_buffs = [b for b in fw.buffs if b.axis == BuffAxis.ATK]
    assert any(abs(b.value - 0.30) < 0.01 for b in atk_buffs), (
        f"First Target +30% ATK buff missing when targeting aerial; buffs={fw.buffs}"
    )


def test_first_target_buff_absent_vs_ground():
    """ATK buff must NOT be present when Firewatch is targeting a ground enemy."""
    from core.types import BuffAxis
    w = _make_world()
    fw = make_firewatch()
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 999.0
    w.add_unit(fw)

    slug = _slug(progress=2.0, hp=9999999)
    w.add_unit(slug)

    w.tick()

    from data.characters.firewatch import _FIRST_TARGET_BUFF_TAG
    atk_buffs = [b for b in fw.buffs if b.source_tag == _FIRST_TARGET_BUFF_TAG]
    assert len(atk_buffs) == 0, "First Target buff must not apply when targeting ground enemy"


# ---------------------------------------------------------------------------
# Test 9: S2 applies STUN to aerial targets
# ---------------------------------------------------------------------------

def test_s2_stuns_aerial_target():
    """S2 Flash Arrow applies STUN to airborne targets when an attack lands during S2.

    Tick order: COMBAT → SKILL. First tick: attack fires before S2 (no stun yet).
    S2 activates in SKILL phase of tick 1. Attack 2 fires ~21 ticks later with S2 active.
    """
    w = _make_world()
    fw = make_firewatch(slot="S2")
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 0.0   # allow attack
    w.add_unit(fw)

    drone = _drone(progress=2.0, hp=9999999)
    w.add_unit(drone)

    fw.skill.sp = fw.skill.sp_cost
    for _ in range(35):   # tick 1: attack(no S2) + S2 fires; tick ~30: attack with S2 active
        w.tick()
        if drone.has_status(StatusKind.STUN):
            break

    assert drone.has_status(StatusKind.STUN), "S2 must STUN aerial target on second attack"


# ---------------------------------------------------------------------------
# Test 10: S2 does NOT stun ground targets
# ---------------------------------------------------------------------------

def test_s2_no_stun_on_ground_target():
    """S2 Flash Arrow must NOT apply STUN to ground enemies."""
    w = _make_world()
    fw = make_firewatch(slot="S2")
    fw.deployed = True; fw.position = (0.0, 1.0); fw.atk_cd = 0.0
    w.add_unit(fw)

    slug = _slug(progress=2.0, hp=9999999)
    w.add_unit(slug)

    fw.skill.sp = fw.skill.sp_cost
    for _ in range(35):
        w.tick()

    assert not slug.has_status(StatusKind.STUN), "S2 must NOT stun ground enemy"

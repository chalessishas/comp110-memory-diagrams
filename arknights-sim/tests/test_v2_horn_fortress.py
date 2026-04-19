"""Horn — Fortress Defender class trait: ranged AoE ↔ melee mode toggle.

Fortress Defender trait (ArknightsGameData):
  - NOT blocking: attacks all enemies in range (ranged physical, AoE simultaneous)
  - Blocking:     attacks single enemy (melee physical, standard priority)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.horn import make_horn
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(path, move_speed=0.0, hp=9999):
    s = make_originium_slug(path=path)
    s.max_hp = hp
    s.hp = hp
    s.move_speed = move_speed
    s.deployed = True
    return s


# ---------------------------------------------------------------------------
# Test 1: Fortress archetype is set correctly
# ---------------------------------------------------------------------------

def test_horn_archetype():
    from core.types import RoleArchetype
    horn = make_horn()
    assert horn.archetype == RoleArchetype.DEF_FORTRESS, "Horn must have DEF_FORTRESS archetype"


# ---------------------------------------------------------------------------
# Test 2: NOT blocking → hits ALL enemies in range simultaneously
# ---------------------------------------------------------------------------

def test_fortress_ranged_hits_all_enemies():
    """When Horn is not blocking, she attacks every enemy in her ranged range in one swing."""
    w = _world()
    horn = make_horn()
    horn.deployed = True
    horn.position = (0.0, 1.0)
    horn.atk_cd = 0.0
    w.add_unit(horn)

    # Place 3 slugs at (1,1), (2,1), (3,1) — all in Horn's ranged range (1,0),(2,0),(3,0)
    # Horn at (0,1), enemy at (1,1): dx=1, dy=0 → in ranged range ✓
    slug_a = _slug(path=[(1, 1)], hp=9999)
    slug_b = _slug(path=[(2, 1)], hp=9999)
    slug_c = _slug(path=[(3, 1)], hp=9999)
    w.add_unit(slug_a)
    w.add_unit(slug_b)
    w.add_unit(slug_c)

    hp_before_a = slug_a.hp
    hp_before_b = slug_b.hp
    hp_before_c = slug_c.hp

    # One tick to trigger ranged attack (no blocking — slugs not on horn's tile)
    w.tick()
    w.tick()  # Two ticks to ensure atk_cd fires

    assert slug_a.hp < hp_before_a, "slug_a must take damage from Horn's ranged AoE"
    assert slug_b.hp < hp_before_b, "slug_b must take damage from Horn's ranged AoE"
    assert slug_c.hp < hp_before_c, "slug_c must take damage from Horn's ranged AoE"


# ---------------------------------------------------------------------------
# Test 3: NOT blocking → single enemy also gets hit
# ---------------------------------------------------------------------------

def test_fortress_ranged_single_enemy():
    """With only one enemy in range and not blocking, Horn still attacks it."""
    w = _world()
    horn = make_horn()
    horn.deployed = True
    horn.position = (0.0, 1.0)
    horn.atk_cd = 0.0
    w.add_unit(horn)

    slug = _slug(path=[(2, 1)], hp=9999)
    w.add_unit(slug)

    hp_before = slug.hp
    for _ in range(TICK_RATE * 4):
        w.tick()
        if slug.hp < hp_before:
            break

    assert slug.hp < hp_before, "Horn must attack the lone slug in ranged mode"


# ---------------------------------------------------------------------------
# Test 4: Blocking → switches to melee single target
# ---------------------------------------------------------------------------

def test_fortress_melee_when_blocking():
    """When Horn is blocking, she attacks only the blocked enemy (melee mode)."""
    w = _world()
    horn = make_horn()
    horn.deployed = True
    horn.position = (0.0, 1.0)
    horn.atk_cd = 0.0
    w.add_unit(horn)

    # Place blocked slug ON Horn's tile (0,1) — _update_block_assignments assigns it
    # Also place a ranged-range slug at (2,1) — should NOT be hit (melee mode)
    slug_blocked = _slug(path=[(0, 1), (1, 1), (2, 1)], hp=9999)
    slug_blocked.position = (0.0, 1.0)  # on Horn's tile → gets blocked
    slug_blocked.path_progress = 0.0
    slug_ranged = _slug(path=[(2, 1)], hp=9999)
    w.add_unit(slug_blocked)
    w.add_unit(slug_ranged)

    hp_before_blocked = slug_blocked.hp
    hp_before_ranged  = slug_ranged.hp

    # Tick until Horn attacks once
    for _ in range(TICK_RATE * 4):
        w.tick()
        if slug_blocked.hp < hp_before_blocked:
            break

    assert slug_blocked.hp < hp_before_blocked, "Blocked slug must take melee damage"
    assert slug_ranged.hp == hp_before_ranged, (
        "Ranged-zone slug must NOT be hit when Horn is in melee mode (blocking)"
    )


# ---------------------------------------------------------------------------
# Test 5: Mode switches as blocking state changes
# ---------------------------------------------------------------------------

def test_fortress_mode_switches_on_block_change():
    """Horn starts in ranged mode, switches to melee when a slug enters her tile.

    Horn at (0,1) facing +x. Ranged range: (1,0),(2,0),(3,0) → abs (1,1),(2,1),(3,1).
    Slug walks from (5,1) toward (0,1) — enters Horn's ranged zone at (3,1),
    then eventually reaches Horn's tile (0,1) and gets blocked.
    """
    w = _world()
    horn = make_horn()
    horn.deployed = True
    horn.position = (0.0, 1.0)
    horn.atk = 100
    horn.atk_cd = 0.0
    w.add_unit(horn)

    # Slug walks from x=5 toward x=0 (right to left, into Horn's ranged range first)
    path = [(5 - i, 1) for i in range(6)]
    slug = _slug(path=path, move_speed=0.5, hp=50000)
    w.add_unit(slug)

    ranged_hit_before_block = False
    switched_to_melee = False

    for _ in range(TICK_RATE * 20):
        w.tick()
        is_blocking = any(horn.unit_id in e.blocked_by_unit_ids for e in w.enemies())
        if not is_blocking and slug.hp < 50000:
            ranged_hit_before_block = True
        if is_blocking:
            switched_to_melee = True
            break

    assert ranged_hit_before_block, "Horn must deal damage in ranged mode before slug reaches her"
    assert switched_to_melee, "Slug must eventually reach Horn's tile and trigger melee mode"


# ---------------------------------------------------------------------------
# Test 6: Enemy outside ranged range is NOT hit in ranged mode
# ---------------------------------------------------------------------------

def test_fortress_ranged_does_not_hit_out_of_range():
    """Enemies outside Horn's ranged range are NOT affected even without blocking."""
    w = _world()
    horn = make_horn()
    horn.deployed = True
    horn.position = (0.0, 1.0)
    horn.atk_cd = 0.0
    w.add_unit(horn)

    # Horn's ranged range from (0,1): in range tiles are (1,0),(2,0),(3,0),(1,-1),(1,1)
    # → absolute: (1,1),(2,1),(3,1),(1,0),(1,2)
    # Slug at (5,1): dx=5 → outside ranged range
    slug_out = _slug(path=[(5, 1)], hp=9999)
    w.add_unit(slug_out)

    for _ in range(TICK_RATE * 4):
        w.tick()

    assert slug_out.hp == 9999, "Enemy outside ranged range must not be hit"

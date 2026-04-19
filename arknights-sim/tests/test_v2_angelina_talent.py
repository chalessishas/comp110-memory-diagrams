"""Angelina talent: Thoughtful — slow enemies on basic attack."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.angelina import make_angelina
from data.enemies import make_originium_slug


# Angelina at (0,0); slug path starts at (1,0) → dx=+1, in DECEL_RANGE
ANG_POS = (0.0, 0.0)
SLUG_PATH = [(1 + i, 0) for i in range(5)]   # starts at (1,0), goes right


def _world() -> World:
    grid = TileGrid(width=6, height=1)
    for i in range(6):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _make_slug() -> object:
    slug = make_originium_slug(path=SLUG_PATH)
    # path[0] = (1, 0) so movement_system sets position=(1,0) immediately
    slug.deployed = True
    return slug


def test_thoughtful_applies_slow_on_attack():
    """Angelina's basic attack must apply SLOW status to the target."""
    w = _world()
    ang = make_angelina()
    ang.deployed = True
    ang.position = ANG_POS
    ang.atk_cd = 0.0
    w.add_unit(ang)

    slug = _make_slug()
    w.add_unit(slug)

    for _ in range(TICK_RATE * 3):   # 3 seconds — enough for Angelina to attack
        w.tick()
        if slug.has_status(StatusKind.SLOW):
            break

    assert slug.has_status(StatusKind.SLOW), \
        "Thoughtful talent must apply SLOW status to attacked enemy"


def test_thoughtful_slow_expires():
    """SLOW applied by Thoughtful must expire after its duration."""
    w = _world()
    ang = make_angelina()
    ang.deployed = True
    ang.position = ANG_POS
    ang.atk_cd = 0.0
    w.add_unit(ang)

    slug = _make_slug()
    w.add_unit(slug)

    # Trigger one attack
    for _ in range(TICK_RATE * 3):
        w.tick()
        if slug.has_status(StatusKind.SLOW):
            break

    assert slug.has_status(StatusKind.SLOW), "Slow must be applied first"

    # Prevent further attacks
    ang.atk_cd = 999.0

    # Run past slow duration (0.8s = 8 ticks + margin)
    for _ in range(TICK_RATE * 2):   # 2 seconds >> 0.8s
        w.tick()

    assert not slug.has_status(StatusKind.SLOW), \
        "SLOW must expire after its duration"

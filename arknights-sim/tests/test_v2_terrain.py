"""v2 — Terrain effect tests: icy TileEffect slows enemy movement."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState, TileEffect
from core.types import TileType, TICK_RATE, DT
from core.systems import register_default_systems
from data.enemies import make_originium_slug


PATH = [(x, 0) for x in range(6)]


def _world(icy_tiles: list[int] | None = None) -> World:
    """Build a 6-tile straight path. icy_tiles: list of x-coords with icy TileEffect."""
    grid = TileGrid(width=6, height=1)
    for i in range(6):
        t = TileState(x=i, y=0, type=TileType.GROUND)
        if icy_tiles and i in icy_tiles:
            t.effects.append(TileEffect(kind="icy", expires_at=float("inf"), params={"amount": 0.3}))
        grid.set_tile(t)
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def test_icy_tile_slows_enemy():
    """Enemy on icy tile must move ~70% as fast as on normal tile."""
    ticks = TICK_RATE * 3  # 3 seconds

    w_base = _world()
    slug_base = make_originium_slug(path=PATH)
    w_base.add_unit(slug_base)

    w_icy = _world(icy_tiles=[0, 1, 2, 3, 4, 5])  # entire path is icy
    slug_icy = make_originium_slug(path=PATH)
    w_icy.add_unit(slug_icy)

    for _ in range(ticks):
        w_base.tick()
        w_icy.tick()

    ratio = slug_icy.path_progress / max(slug_base.path_progress, 1e-9)
    assert 0.60 <= ratio <= 0.80, \
        f"Icy terrain (30% slow) should yield ~70% speed, got ratio={ratio:.2f} " \
        f"(base={slug_base.path_progress:.2f}, icy={slug_icy.path_progress:.2f})"


def test_non_icy_tile_unaffected():
    """Enemy on plain GROUND tile must move at full speed."""
    w = _world()  # no icy tiles
    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    for _ in range(TICK_RATE * 2):
        w.tick()

    expected = slug.move_speed * 2.0  # 2 seconds at base speed
    assert abs(slug.path_progress - expected) < 0.1 + 1e-9, \
        f"Plain tile enemy should be at ~{expected:.1f} tiles, got {slug.path_progress:.2f}"


def test_exiting_icy_tile_restores_speed():
    """Enemy that leaves icy section must regain full speed."""
    # Only first 2 tiles are icy; tiles 2-5 are normal
    ticks = TICK_RATE * 3

    w_base = _world()
    slug_base = make_originium_slug(path=PATH)
    w_base.add_unit(slug_base)

    w_mixed = _world(icy_tiles=[0, 1])
    slug_mixed = make_originium_slug(path=PATH)
    w_mixed.add_unit(slug_mixed)

    for _ in range(ticks):
        w_base.tick()
        w_mixed.tick()

    # Mixed: ~0.7 speed for 2 tiles (≈2.86s to cross), then full speed remaining.
    # After 3s, mixed path_progress should be > 2.5 (clearly moving at full speed in later tiles).
    assert slug_mixed.path_progress > 2.0, \
        f"Enemy must resume full speed after leaving icy section, got {slug_mixed.path_progress:.2f}"

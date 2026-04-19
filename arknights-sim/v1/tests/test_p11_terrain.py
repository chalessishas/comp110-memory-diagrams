"""P11 — Terrain effect tests (icy surface → Cold slow)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.battle import Battle, DT, TICK_RATE
from core.map import Map, Tile
from data.enemies import make_originium_slug


_PATH = [(0, 0), (1, 0), (2, 0), (3, 0)]


def _battle_with_map(*tiles):
    m = Map(width=4, height=1, tiles=list(tiles))
    return m


def test_icy_tile_applies_slow():
    enemy = make_originium_slug(path=_PATH)
    tiles = [Tile(x=i, y=0, type="ground") for i in range(4)]
    tiles[0] = Tile(x=0, y=0, type="ground", terrain_effect="icy")
    m = Map(width=4, height=1, tiles=tiles)

    battle = Battle(operators=[], enemies=[enemy], map=m)
    # Enemy starts at progress=0.0 → tile (0,0) which is icy
    battle._tick()
    battle._apply_terrain_effects()

    assert enemy.slow_factor > 1.0, "Enemy on icy tile must be slowed"
    assert abs(enemy.slow_factor - 1.43) < 0.01


def test_icy_slow_expires_after_leaving_tile():
    enemy = make_originium_slug(path=_PATH)
    tiles = [Tile(x=i, y=0, type="ground") for i in range(4)]
    tiles[0] = Tile(x=0, y=0, type="ground", terrain_effect="icy")
    m = Map(width=4, height=1, tiles=tiles)

    battle = Battle(operators=[], enemies=[enemy], map=m)
    # Apply terrain effect while on icy tile
    battle._apply_terrain_effects()
    assert enemy.slow_factor > 1.0

    # Move enemy to non-icy tile (progress=2.0 → tile (2,0))
    enemy._path_progress = 2.0
    # Let terrain not refresh (enemy is on non-icy tile) and tick status to expire
    for _ in range(5):   # DT*2 duration = 2 ticks; 5 ensures expiry
        enemy.tick_status(DT)

    assert enemy.slow_factor == 1.0, "Cold slow must expire after leaving icy tile"


def test_non_icy_tile_no_effect():
    enemy = make_originium_slug(path=_PATH)
    tiles = [Tile(x=i, y=0, type="ground") for i in range(4)]
    m = Map(width=4, height=1, tiles=tiles)

    battle = Battle(operators=[], enemies=[enemy], map=m)
    battle._apply_terrain_effects()

    assert enemy.slow_factor == 1.0
    assert not enemy.status_effects


def test_battle_without_map_no_terrain():
    enemy = make_originium_slug(path=_PATH)
    battle = Battle(operators=[], enemies=[enemy])  # no map

    for _ in range(10):
        battle._tick()

    assert enemy.slow_factor == 1.0, "No terrain effects without a map attached"

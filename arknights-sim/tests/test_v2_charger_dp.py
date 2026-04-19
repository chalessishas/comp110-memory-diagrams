"""Vanguard Charger class trait: Fang gains 1 DP on every enemy kill."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.fang import make_fang
from data.enemies import make_originium_slug


def _world(starting_dp: int = 0) -> World:
    grid = TileGrid(width=6, height=1)
    for i in range(6):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = starting_dp
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _weak_slug():
    slug = make_originium_slug(path=[(1 + i, 0) for i in range(5)])
    slug.deployed = True
    slug.max_hp = 1
    slug.hp = 1
    slug.move_speed = 0.0
    return slug


def test_fang_no_battle_start_dp():
    """Charger does NOT grant battle-start DP (unlike Texas Pioneer)."""
    w = _world(starting_dp=5)
    fang = make_fang()
    w.add_unit(fang)
    assert w.global_state.dp == 5, f"Charger must not grant battle-start DP, got {w.global_state.dp}"


def test_fang_gains_dp_on_kill():
    """Fang gains exactly 1 DP when she kills an enemy."""
    w = _world(starting_dp=0)
    fang = make_fang()
    fang.deployed = True
    fang.position = (0.0, 0.0)
    fang.atk_cd = 0.0
    w.add_unit(fang)

    slug = _weak_slug()
    w.add_unit(slug)

    for _ in range(TICK_RATE * 3):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die"
    assert w.global_state.dp == 1, f"Expected 1 DP from Charger kill, got {w.global_state.dp}"


def test_fang_gains_dp_per_kill_multiple():
    """Fang gains 1 DP per kill — three kills = 3 DP."""
    w = _world(starting_dp=0)
    fang = make_fang()
    fang.deployed = True
    fang.position = (0.0, 0.0)
    fang.atk_cd = 0.0
    w.add_unit(fang)

    for _ in range(3):
        w.add_unit(_weak_slug())

    for _ in range(TICK_RATE * 15):
        w.tick()

    dead = [u for u in w.units if not u.alive and u.faction.value == "enemy"]
    assert len(dead) == 3, f"All 3 slugs must die, got {len(dead)} dead"
    assert w.global_state.dp == 3, f"Expected 3 DP from 3 kills, got {w.global_state.dp}"

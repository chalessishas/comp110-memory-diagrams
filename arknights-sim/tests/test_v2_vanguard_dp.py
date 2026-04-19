"""Vanguard Pioneer DP-on-kill: Texas generates 1 DP per enemy killed."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.texas import make_texas
from data.enemies import make_originium_slug


def _world(starting_dp: int = 0) -> World:
    grid = TileGrid(width=6, height=1)
    for i in range(6):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = starting_dp
    register_default_systems(w)
    return w


def _weak_slug() -> object:
    """1 HP slug — dies in one hit."""
    slug = make_originium_slug(path=[(1 + i, 0) for i in range(5)])
    slug.deployed = True
    slug.max_hp = 1
    slug.hp = 1
    return slug


def test_texas_gains_dp_on_kill():
    """Texas generates exactly 1 DP when she kills an enemy."""
    w = _world(starting_dp=5)
    tex = make_texas()
    tex.deployed = True
    tex.position = (0.0, 0.0)
    tex.atk_cd = 0.0
    w.add_unit(tex)

    slug = _weak_slug()
    w.add_unit(slug)

    dp_before = w.global_state.dp
    for _ in range(TICK_RATE * 3):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die for DP test to be valid"
    assert w.global_state.dp == dp_before + 1, \
        f"Expected {dp_before + 1} DP after kill, got {w.global_state.dp}"


def test_texas_gains_dp_per_kill_multiple():
    """Texas gains 1 DP per kill — two kills yields +2 DP."""
    w = _world(starting_dp=0)
    # Disable natural DP gain for isolation
    w.global_state.dp_gain_rate = 0.0

    tex = make_texas()
    tex.deployed = True
    tex.position = (0.0, 0.0)
    tex.atk_cd = 0.0
    w.add_unit(tex)

    for _ in range(2):
        slug = _weak_slug()
        slug.move_speed = 0.0  # stay in Texas's range so she can hit both
        w.add_unit(slug)

    for _ in range(TICK_RATE * 10):
        w.tick()

    dead = [u for u in w.units if not u.alive and u.faction.value == "enemy"]
    assert len(dead) == 2, f"Both slugs must die, got {len(dead)} dead"
    assert w.global_state.dp == 2, \
        f"Expected 2 DP from 2 kills (no natural gain), got {w.global_state.dp}"


def test_non_vanguard_no_dp_on_kill():
    """Non-Vanguard operators do NOT generate DP on kill."""
    from data.characters.silverash import make_silverash
    w = _world(starting_dp=5)
    w.global_state.dp_gain_rate = 0.0

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (0.0, 0.0)
    sa.atk_cd = 0.0
    if sa.skill:
        sa.skill.sp = 0.0  # disable S3
    w.add_unit(sa)

    slug = _weak_slug()
    w.add_unit(slug)

    for _ in range(TICK_RATE * 3):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive
    assert w.global_state.dp == 5, \
        f"Non-Vanguard must not grant DP on kill, got {w.global_state.dp}"

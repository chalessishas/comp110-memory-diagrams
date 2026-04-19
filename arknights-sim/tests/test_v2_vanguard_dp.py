"""Vanguard Pioneer Tactical Delivery: Texas grants +2 DP at operation start.

Correction from research: Texas's talent fires at battle start (add_unit),
NOT on kill. The Charger class trait (Fang/Vigna/Bagpipe) gives DP on kill.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.texas import make_texas


def _world(starting_dp: int = 0) -> World:
    grid = TileGrid(width=6, height=1)
    for i in range(6):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = starting_dp
    w.global_state.dp_gain_rate = 0.0  # isolate natural DP gain
    register_default_systems(w)
    return w


def test_texas_grants_dp_on_add_to_world():
    """Texas Tactical Delivery grants +2 DP the moment she is added to the world."""
    w = _world(starting_dp=5)
    dp_before = w.global_state.dp
    tex = make_texas()
    w.add_unit(tex)
    assert w.global_state.dp == dp_before + 2, (
        f"Expected {dp_before + 2} DP after Texas add_unit, got {w.global_state.dp}"
    )


def test_texas_dp_bonus_fires_once():
    """The +2 DP fires exactly once per Texas instance added."""
    w = _world(starting_dp=0)
    tex = make_texas()
    w.add_unit(tex)
    # Tick for a while — no more DP gain from Texas
    for _ in range(TICK_RATE * 5):
        w.tick()
    assert w.global_state.dp == 2, (
        f"Expected exactly 2 DP from Texas (no ticks of gain), got {w.global_state.dp}"
    )


def test_two_texas_double_dp():
    """Two Texas instances each grant +2 DP = +4 total."""
    w = _world(starting_dp=0)
    w.add_unit(make_texas())
    w.add_unit(make_texas())
    assert w.global_state.dp == 4, (
        f"Two Texas instances should grant 4 DP, got {w.global_state.dp}"
    )


def test_non_pioneer_no_battle_start_dp():
    """Non-Vanguard operators do NOT grant battle-start DP."""
    from data.characters.silverash import make_silverash
    w = _world(starting_dp=5)
    sa = make_silverash("S3")
    w.add_unit(sa)
    assert w.global_state.dp == 5, (
        f"SilverAsh must not grant DP on add_unit, got {w.global_state.dp}"
    )


def test_texas_no_dp_on_kill():
    """Texas Pioneer does NOT generate DP when she kills an enemy (Charger does, not Pioneer)."""
    from data.enemies import make_originium_slug
    w = _world(starting_dp=0)
    tex = make_texas()
    tex.deployed = True
    tex.position = (0.0, 0.0)
    tex.atk_cd = 0.0
    w.add_unit(tex)

    dp_after_deploy = w.global_state.dp  # should be 2 from Tactical Delivery
    slug = make_originium_slug(path=[(1 + i, 0) for i in range(5)])
    slug.deployed = True
    slug.max_hp = 1
    slug.hp = 1
    slug.move_speed = 0.0
    w.add_unit(slug)

    for _ in range(TICK_RATE * 3):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die for the no-kill-DP assertion to be valid"
    assert w.global_state.dp == dp_after_deploy, (
        f"Texas Pioneer must not grant DP on kill; expected {dp_after_deploy}, "
        f"got {w.global_state.dp}"
    )

"""Ashlock (Fortress Defender) and Vigna (Charger Vanguard) smoke tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, RoleArchetype, TICK_RATE
from core.systems import register_default_systems
from data.characters.ashlock import make_ashlock
from data.characters.vigna import make_vigna
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


def _weak_slug(path):
    s = make_originium_slug(path=path)
    s.max_hp = 1; s.hp = 1; s.move_speed = 0.0
    return s


# ---------------------------------------------------------------------------
# Ashlock — Fortress archetype identical to Horn
# ---------------------------------------------------------------------------

def test_ashlock_fortress_archetype():
    assert make_ashlock().archetype == RoleArchetype.DEF_FORTRESS


def test_ashlock_ranged_hits_all():
    """Ashlock not blocking → ranged AoE hits multiple enemies."""
    w = _world()
    ashlock = make_ashlock()
    ashlock.deployed = True
    ashlock.position = (0.0, 1.0)
    ashlock.atk_cd = 0.0
    w.add_unit(ashlock)

    slug_a = _weak_slug([(1, 1)])
    slug_b = _weak_slug([(2, 1)])
    w.add_unit(slug_a)
    w.add_unit(slug_b)

    for _ in range(TICK_RATE * 4):
        w.tick()

    assert not slug_a.alive, "slug_a must be killed by Ashlock ranged AoE"
    assert not slug_b.alive, "slug_b must be killed by Ashlock ranged AoE"


def test_ashlock_block_count():
    """Ashlock has block=3 (same as Horn)."""
    assert make_ashlock().block == 3


# ---------------------------------------------------------------------------
# Vigna — Charger archetype (same as Fang)
# ---------------------------------------------------------------------------

def test_vigna_charger_archetype():
    assert make_vigna().archetype == RoleArchetype.VAN_CHARGER


def test_vigna_no_battle_start_dp():
    """Charger does NOT grant battle-start DP."""
    w = _world()
    w.global_state.dp = 5
    w.add_unit(make_vigna())
    assert w.global_state.dp == 5


def test_vigna_gains_dp_on_kill():
    """Vigna gains 1 DP when she kills an enemy (Charger class trait)."""
    w = _world()
    vigna = make_vigna()
    vigna.deployed = True
    vigna.position = (0.0, 1.0)
    vigna.atk_cd = 0.0
    w.add_unit(vigna)

    slug = _weak_slug([(0, 1), (5, 1)])
    w.add_unit(slug)

    for _ in range(TICK_RATE * 3):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die"
    assert w.global_state.dp == 1, f"Expected 1 DP from Vigna kill, got {w.global_state.dp}"


def test_vigna_multiple_kills():
    """Vigna gains 1 DP per kill — two kills = 2 DP."""
    w = _world()
    vigna = make_vigna()
    vigna.deployed = True
    vigna.position = (0.0, 1.0)
    vigna.atk_cd = 0.0
    w.add_unit(vigna)

    # Path: start at Vigna's tile, goal far away — move_speed=0 keeps them stationary
    for _ in range(2):
        w.add_unit(_weak_slug([(0, 1), (5, 1)]))

    for _ in range(TICK_RATE * 10):
        w.tick()

    dead = [u for u in w.units if not u.alive and u.faction.value == "enemy"]
    assert len(dead) == 2
    assert w.global_state.dp == 2, f"Expected 2 DP from 2 kills, got {w.global_state.dp}"

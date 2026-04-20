"""Courier talent "Karlan Patrol" — DEF+60 when blocking ≥2 enemies.

Tests cover:
  - Talent configured correctly (name + behavior_tag)
  - No DEF buff when not blocking (0 enemies at same tile)
  - DEF buff applied when blocking exactly 2 enemies (block=2 cap)
  - DEF buff removed when one enemy dies (blocking drops to 1)
  - slot=None still has talent (talent independent of skill slot)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, Profession, TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.courier import (
    make_courier, _TALENT_TAG, _TALENT_BUFF_TAG, _DEF_BONUS, _BLOCK_THRESHOLD,
)
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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _slug_on_tile(w: World, x: float, y: float) -> UnitState:
    """Add a stationary slug at (x, y) — targeting_system will handle blocking."""
    slug = make_originium_slug(path=[(int(x), int(y))] * 5)
    slug.deployed = True; slug.position = (x, y); slug.move_speed = 0.0
    slug.atk_cd = 999.0
    w.add_unit(slug)
    return slug


def test_courier_talent_configured():
    c = make_courier(slot="S1")
    assert len(c.talents) == 1
    assert c.talents[0].name == "Karlan Patrol"
    assert c.talents[0].behavior_tag == _TALENT_TAG


def test_no_def_buff_when_not_blocking():
    """No DEF buff when no enemies are on Courier's tile."""
    w = _world()
    c = make_courier(slot=None)
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    # Enemy far away — not on Courier's tile
    _slug_on_tile(w, 4.0, 1.0)

    w.tick()

    buff_tags = [b.source_tag for b in c.buffs]
    assert _TALENT_BUFF_TAG not in buff_tags, (
        "Karlan Patrol DEF buff must NOT be active when not blocking"
    )


def test_def_buff_applied_when_blocking_two():
    """DEF buff applies when Courier blocks 2 enemies on same tile."""
    w = _world()
    c = make_courier(slot=None)
    # Courier block=2, placed at (2, 1)
    c.deployed = True; c.position = (2.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    # Two slugs on Courier's tile — targeting_system will assign both as blocked
    _slug_on_tile(w, 2.0, 1.0)
    _slug_on_tile(w, 2.0, 1.0)

    w.tick()

    # Verify blocking was established
    blocking_count = sum(1 for e in w.enemies() if c.unit_id in e.blocked_by_unit_ids)
    assert blocking_count == 2, f"Expected Courier to block 2 enemies; got {blocking_count}"

    buff_tags = [b.source_tag for b in c.buffs]
    assert _TALENT_BUFF_TAG in buff_tags, (
        "Karlan Patrol DEF buff must be active when blocking ≥2 enemies"
    )

    def_buff = next(b for b in c.buffs if b.source_tag == _TALENT_BUFF_TAG)
    assert def_buff.value == _DEF_BONUS, (
        f"DEF buff must be {_DEF_BONUS}; got {def_buff.value}"
    )


def test_def_buff_removed_when_blocking_drops():
    """DEF buff is removed when blocking count drops below 2."""
    w = _world()
    c = make_courier(slot=None)
    c.deployed = True; c.position = (2.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    slug1 = _slug_on_tile(w, 2.0, 1.0)
    slug2 = _slug_on_tile(w, 2.0, 1.0)

    w.tick()
    assert _TALENT_BUFF_TAG in [b.source_tag for b in c.buffs], "DEF buff must be present after tick with 2 blocked"

    # Kill one slug — next tick only 1 enemy remains, blocking drops to ≤1
    slug2.alive = False; slug2.hp = 0

    w.tick()

    buff_tags = [b.source_tag for b in c.buffs]
    assert _TALENT_BUFF_TAG not in buff_tags, (
        "Karlan Patrol DEF buff must be removed when blocking drops below 2"
    )


def test_talent_present_without_skill():
    c = make_courier(slot=None)
    assert len(c.talents) == 1
    assert c.talents[0].behavior_tag == _TALENT_TAG

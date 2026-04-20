"""Weedy S2 Water Jet — ATK+80% for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.weedy import (
    make_weedy, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)
from data.enemies import make_originium_slug


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(0, 1)):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True; e.position = (float(px), float(py))
    e.atk = 0; e.move_speed = 0.0
    return e


def test_weedy_s2_config():
    w = make_weedy(slot="S2")
    sk = w.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Water Jet"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+80% buff."""
    world = _world()
    w = make_weedy(slot="S2")
    base_atk = w.effective_atk
    w.deployed = True; w.position = (0.0, 1.0); w.atk_cd = 999.0
    world.add_unit(w)

    slug = _slug(pos=(0, 1))
    world.add_unit(slug)

    w.skill.sp = float(w.skill.sp_cost)
    world.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert w.effective_atk == expected, f"ATK: expected {expected}, got {w.effective_atk}"


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    world = _world()
    w = make_weedy(slot="S2")
    base_atk = w.effective_atk
    w.deployed = True; w.position = (0.0, 1.0); w.atk_cd = 999.0
    w.skill.sp = float(w.skill.sp_cost)
    world.add_unit(w)

    slug = _slug(pos=(0, 1))
    world.add_unit(slug)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        world.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in w.buffs)
    assert w.effective_atk == base_atk


def test_s3_regression():
    w = make_weedy(slot="S3")
    assert w.skill is not None and w.skill.slot == "S3"
    assert w.skill.name == "Torrential Stream"

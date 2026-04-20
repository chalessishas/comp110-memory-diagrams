"""Typhon S2 Charged Arrow — ATK+100%, 3 ammo."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.typhon import (
    make_typhon, _S2_TAG, _S2_ATK_RATIO, _S2_AMMO, _S2_SOURCE_TAG,
)
from data.enemies import make_originium_slug


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(1, 1)):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True; e.position = (float(px), float(py))
    e.atk = 0; e.move_speed = 0.0; e.max_hp = 999999; e.hp = 999999
    return e


def test_typhon_s2_config():
    t = make_typhon(slot="S2")
    sk = t.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Charged Arrow"
    assert sk.sp_cost == 25
    assert sk.ammo_count == _S2_AMMO
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+100% buff."""
    from core.types import BuffAxis, BuffStack
    world = _world()
    t = make_typhon(slot="S2")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    world.add_unit(t)

    slug = _slug(pos=(1, 1))
    world.add_unit(slug)

    t.skill.sp = float(t.skill.sp_cost)
    world.tick()

    atk_buff = next((b for b in t.buffs if b.source_tag == _S2_SOURCE_TAG), None)
    assert atk_buff is not None, "S2 ATK buff must be applied"
    assert atk_buff.axis == BuffAxis.ATK
    assert atk_buff.stack == BuffStack.RATIO
    assert atk_buff.value == _S2_ATK_RATIO


def test_s2_ammo_initialized():
    """S2 skill starts with ammo loaded (ammo_count set)."""
    t = make_typhon(slot="S2")
    assert t.skill.ammo_count == _S2_AMMO


def test_s3_regression():
    t = make_typhon(slot="S3")
    assert t.skill is not None and t.skill.slot == "S3"
    assert t.skill.name == "Eternal Hunt"
    assert t.skill.ammo_count == 5

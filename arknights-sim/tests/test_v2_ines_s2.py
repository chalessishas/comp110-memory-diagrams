"""Ines S2 Shadow Strike — ATK+100% for 15s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.ines import (
    make_ines, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_ines_s2_config():
    i = make_ines(slot="S2")
    sk = i.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Shadow Strike"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+100% buff."""
    from core.types import BuffAxis, BuffStack
    w = _world()
    i = make_ines(slot="S2")
    i.deployed = True; i.position = (0.0, 1.0); i.atk_cd = 999.0
    w.add_unit(i)

    i.skill.sp = float(i.skill.sp_cost)
    w.tick()

    buff = next((b for b in i.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S2_ATK_RATIO


def test_s2_buff_removed_on_end():
    """Buff cleared when S2 expires."""
    w = _world()
    i = make_ines(slot="S2")
    i.deployed = True; i.position = (0.0, 1.0); i.atk_cd = 999.0
    i.skill.sp = float(i.skill.sp_cost)
    w.add_unit(i)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in i.buffs)


def test_s3_regression():
    i = make_ines(slot="S3")
    assert i.skill is not None and i.skill.slot == "S3"
    assert i.skill.name == "Obedient Strings"

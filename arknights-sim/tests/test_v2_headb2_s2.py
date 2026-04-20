"""headb2 S2 Shockwave Burst — ATK+80% for 15s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.headb2 import (
    make_headb2, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_headb2_s2_config():
    h = make_headb2(slot="S2")
    sk = h.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Shockwave Burst"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+80% buff."""
    from core.types import BuffAxis, BuffStack
    w = _world()
    h = make_headb2(slot="S2")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    h.skill.sp = float(h.skill.sp_cost)
    w.tick()

    buff = next((b for b in h.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S2_ATK_RATIO


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    w = _world()
    h = make_headb2(slot="S2")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    h.skill.sp = float(h.skill.sp_cost)
    w.add_unit(h)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in h.buffs)


def test_s3_regression():
    h = make_headb2(slot="S3")
    assert h.skill is not None and h.skill.slot == "S3"
    assert h.skill.name == "Storm Strike"

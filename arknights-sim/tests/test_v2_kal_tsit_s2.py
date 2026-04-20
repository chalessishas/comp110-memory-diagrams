"""Kal'tsit S2 Guiding Light — ATK+60% for 30s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.kal_tsit import (
    make_kal_tsit, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)


def _world(w=5, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_kal_tsit_s2_config():
    k = make_kal_tsit(slot="S2")
    sk = k.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Guiding Light"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+60% buff."""
    from core.types import BuffAxis, BuffStack
    w = _world()
    k = make_kal_tsit(slot="S2")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    w.add_unit(k)

    k.skill.sp = float(k.skill.sp_cost)
    w.tick()

    buff = next((b for b in k.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S2_ATK_RATIO


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    w = _world()
    k = make_kal_tsit(slot="S2")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    k.skill.sp = float(k.skill.sp_cost)
    w.add_unit(k)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in k.buffs)


def test_s3_regression():
    k = make_kal_tsit(slot="S3")
    assert k.skill is not None and k.skill.slot == "S3"
    assert k.skill.name == "All-Out"

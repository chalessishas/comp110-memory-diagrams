"""Fartth S2 Aimed Shot — ATK+50% for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.fartth import (
    make_fartth, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def test_fartth_s2_config():
    f = make_fartth(slot="S2")
    sk = f.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Aimed Shot"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+50% buff."""
    from core.types import BuffAxis
    w = _world()
    f = make_fartth(slot="S2")
    f.deployed = True; f.position = (0.0, 1.0); f.atk_cd = 999.0
    w.add_unit(f)

    f.skill.sp = float(f.skill.sp_cost)
    w.tick()

    buff = next((b for b in f.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S2_ATK_RATIO


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    w = _world()
    f = make_fartth(slot="S2")
    f.deployed = True; f.position = (0.0, 1.0); f.atk_cd = 999.0
    w.add_unit(f)

    f.skill.sp = float(f.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in f.buffs)


def test_s3_regression():
    f = make_fartth(slot="S3")
    assert f.skill is not None and f.skill.slot == "S3"
    assert f.skill.name == "Predator"

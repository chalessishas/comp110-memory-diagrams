"""Mlynar S2 Blood of Iron — ATK+30%, ASPD+40, block restored for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.mlynar import (
    make_mlynar, _S2_TAG, _S2_ATK_RATIO, _S2_ASPD_FLAT,
    _S2_BUFF_TAG, _S2_DURATION, _INACTIVE_ATK_CD,
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


def test_mlynar_s2_config():
    m = make_mlynar(slot="S2")
    sk = m.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Blood of Iron"
    assert sk.sp_cost == 35
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+30% (on top of ramp) when activated."""
    from core.types import BuffAxis, BuffStack
    w = _world()
    m = make_mlynar(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    atk_buff = next(
        (b for b in m.buffs if b.source_tag == _S2_BUFF_TAG and b.axis == BuffAxis.ATK),
        None,
    )
    assert atk_buff is not None, "S2 ATK buff must be applied"
    assert atk_buff.stack == BuffStack.RATIO
    assert atk_buff.value == _S2_ATK_RATIO


def test_s2_aspd_buff():
    """S2 applies ASPD+40 buff."""
    from core.types import BuffAxis
    w = _world()
    m = make_mlynar(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    aspd_buff = next(
        (b for b in m.buffs if b.source_tag == _S2_BUFF_TAG and b.axis == BuffAxis.ASPD),
        None,
    )
    assert aspd_buff is not None, "S2 ASPD buff must be applied"
    assert aspd_buff.value == _S2_ASPD_FLAT


def test_s2_block_restored():
    """block=3 during S2 (trait restores it on skill fire)."""
    w = _world()
    m = make_mlynar(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    assert m.block == 0  # inactive by default
    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.block == 3, "S2 must restore block to 3"


def test_s2_buffs_removed_on_end():
    """ATK and ASPD buffs cleared, block reset when S2 expires."""
    w = _world()
    m = make_mlynar(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0)
    m.skill.sp = float(m.skill.sp_cost)
    w.add_unit(m)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in m.buffs)
    assert m.block == 0


def test_s3_regression():
    m = make_mlynar(slot="S3")
    assert m.skill is not None and m.skill.slot == "S3"
    assert m.skill.name == "Father's Teachings"

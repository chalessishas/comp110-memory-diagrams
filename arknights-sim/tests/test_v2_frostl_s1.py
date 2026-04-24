"""Frostleaf S2 'Ice Tomahawk' — 25s MANUAL, ASPD+35."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, BuffStack
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.frostl import (
    make_frostl, _S1_TAG, _S1_DURATION, _S2_TAG,
    _S2_ASPD_FLAT, _S2_BUFF_TAG, _S2_DURATION,
)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_frostl_s1_config():
    op = make_frostl(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Frost Tomahawk"
    assert sk.sp_cost == 4 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG


def test_s2_config():
    op = make_frostl(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Ice Tomahawk"
    assert sk.sp_cost == 54 and sk.initial_sp == 0
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG


def test_s2_aspd_buff_applied():
    w = _world()
    op = make_frostl(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    aspd_buffs = [b for b in op.buffs if b.axis == BuffAxis.ASPD and b.stack == BuffStack.FLAT]
    assert len(aspd_buffs) == 1
    assert aspd_buffs[0].value == _S2_ASPD_FLAT


def test_s2_aspd_buff_cleared_on_end():
    w = _world()
    op = make_frostl(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)

"""Bubble S2 "Surfing Time" — DEF+300 for 20s, AUTO trigger.

Tests: config, def buff applied, def amount, buff cleared, s3 regression.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.bubble import (
    make_bubble, _S2_BUFF_TAG, _S2_DEF_BUFF, _S2_DURATION, _S2_TAG,
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


def test_bubble_s2_config():
    op = make_bubble(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Surfing Time"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 15
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_def_buff_applied():
    w = _world()
    op = make_bubble(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    assert op.effective_def > base_def
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_def_amount():
    w = _world()
    op = make_bubble(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    assert op.effective_def == base_def + _S2_DEF_BUFF


def test_s2_buff_cleared_on_end():
    w = _world()
    op = make_bubble(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()
    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_def == base_def


def test_s3_regression():
    op = make_bubble(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Grand Surf"

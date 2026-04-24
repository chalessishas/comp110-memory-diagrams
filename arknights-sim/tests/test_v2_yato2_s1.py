"""Kirin R Yato S1 "Demon Form" — 20s ON_DEPLOY AUTO, ASPD+100.

Tests cover:
  - S1 config (sp_cost=0, initial_sp=0, duration=20s, ON_DEPLOY)
  - S1 ASPD buff applied on first tick (auto-fires from sp=0)
  - S1 ASPD buff cleared after skill ends
  - S2 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.yato2 import (
    make_yato2,
    _S1_TAG, _S1_ASPD_VALUE, _S1_ASPD_BUFF_TAG, _S1_DURATION,
    _S2_TAG,
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


def test_yato2_s1_config():
    op = make_yato2(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Demon Form"
    assert sk.sp_cost == 0 and sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_s1_aspd_buff_applied():
    w = _world()
    op = make_yato2(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    w.tick()

    assert any(b.source_tag == _S1_ASPD_BUFF_TAG and b.value == _S1_ASPD_VALUE
               for b in op.buffs if b.axis == BuffAxis.ASPD)


def test_s1_aspd_buff_cleared_on_end():
    w = _world()
    op = make_yato2(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    w.tick()
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_ASPD_BUFF_TAG for b in op.buffs)


def test_s2_slot_config():
    op = make_yato2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.behavior_tag == _S2_TAG

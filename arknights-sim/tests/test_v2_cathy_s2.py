"""Cathy (Catherine) S2 "Tempered by War" — 30s MANUAL, DEF+30%.

Tests cover:
  - S2 config (name, sp_cost=30, initial_sp=15, duration=30s, MANUAL)
  - DEF buff applied on trigger
  - DEF buff cleared after skill ends
  - S1 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.cathy import (
    make_cathy, _S2_TAG, _S2_DEF_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def test_cathy_s2_config():
    op = make_cathy(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Tempered by War"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_def_buff_applied():
    w = _world()
    op = make_cathy(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S2_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_def_buff_cleared_on_end():
    w = _world()
    op = make_cathy(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_def == base_def


def test_s1_slot_config():
    op = make_cathy(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Wrought by Age"

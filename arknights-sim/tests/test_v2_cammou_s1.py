"""Cammou S1 "ATK Up β" — 25s MANUAL, ATK+80%.

Tests cover:
  - S1 config (name, sp_cost=35, initial_sp=10, duration=25s, MANUAL)
  - ATK buff applied on trigger
  - ATK buff cleared after skill ends
  - S2 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.cammou import (
    make_cammou, _S1_TAG, _S1_ATK_RATIO, _S1_BUFF_TAG, _S1_DURATION,
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


def test_cammou_s1_config():
    op = make_cammou(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "ATK Up β"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 10
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_atk_buff_applied():
    w = _world()
    op = make_cammou(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_atk * (1 + _S1_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)


def test_s1_atk_buff_cleared_on_end():
    w = _world()
    op = make_cammou(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


def test_s2_regression():
    op = make_cammou(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"
    assert op.skill.name == "Desert Quicksand"

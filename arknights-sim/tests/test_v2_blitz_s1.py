"""Blitz S1 stub / S2 "Shield Bash" — 6s MANUAL, ASPD+200.

Tests cover:
  - S1 config (name, sp_cost=18, initial_sp=10, duration=3.5s)
  - S2 config (name, sp_cost=40, initial_sp=15)
  - S2 ASPD buff applied on trigger
  - S2 ASPD buff cleared after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.blitz import (
    make_blitz, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_ASPD_BONUS, _S2_BUFF_TAG, _S2_DURATION,
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


def test_blitz_s1_config():
    op = make_blitz(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Flash Shield"
    assert sk.sp_cost == 18
    assert sk.initial_sp == 10
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_blitz_s2_config():
    op = make_blitz(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Shield Bash"
    assert sk.sp_cost == 40 and sk.initial_sp == 15
    assert sk.behavior_tag == _S2_TAG


def test_s2_aspd_buff_applied():
    w = _world()
    op = make_blitz(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    aspd_buffs = [b for b in op.buffs if b.axis == BuffAxis.ASPD]
    assert any(b.source_tag == _S2_BUFF_TAG and b.value == _S2_ASPD_BONUS for b in aspd_buffs)


def test_s2_aspd_buff_cleared_on_end():
    w = _world()
    op = make_blitz(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)

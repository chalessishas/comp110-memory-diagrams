"""Lava S1 "Tactical Chant α" — 20s MANUAL, ASPD+50.

Tests cover:
  - S1 config (name, sp_cost=40, initial_sp=0, duration=20s, MANUAL)
  - ASPD buff applied on trigger (reduces current_atk_interval)
  - ASPD buff cleared after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.lava import make_lava, _S1_TAG, _S1_ASPD_BONUS, _S1_ASPD_BUFF_TAG, _S1_DURATION


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_lava_s1_config():
    op = make_lava(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Tactical Chant α"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_aspd_buff_applied():
    w = _world()
    op = make_lava(slot="S1")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.current_atk_interval < base_interval
    assert any(b.source_tag == _S1_ASPD_BUFF_TAG for b in op.buffs)


def test_s1_aspd_buff_cleared_on_end():
    w = _world()
    op = make_lava(slot="S1")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_ASPD_BUFF_TAG for b in op.buffs)
    assert abs(op.current_atk_interval - base_interval) < 1e-6

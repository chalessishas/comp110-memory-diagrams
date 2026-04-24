"""Dagda S1 stub / S2 "Search and Destroy" — 15s MANUAL, ATK+28%.

Tests cover:
  - S1 config (name, sp_cost=4, initial_sp=0, AUTO_DEFENSIVE)
  - S2 config (name, sp_cost=34, initial_sp=15)
  - S2 ATK buff applied on trigger
  - S2 ATK buff cleared after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.dagda import (
    make_dagda, _S1_TAG, _S1_DURATION, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def test_dagda_s1_config():
    op = make_dagda(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Counter Technique"
    assert sk.sp_cost == 4
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.sp_gain_mode == SPGainMode.AUTO_DEFENSIVE
    assert sk.behavior_tag == _S1_TAG


def test_dagda_s2_config():
    op = make_dagda(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Search and Destroy"
    assert sk.sp_cost == 34 and sk.initial_sp == 15
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_dagda(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.effective_atk == int(base_atk * (1 + _S2_ATK_RATIO))
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_atk_buff_cleared_on_end():
    w = _world()
    op = make_dagda(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk

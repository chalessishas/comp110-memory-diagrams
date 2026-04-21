"""Asbest S2 "Fire-Electric Mode" — 50s MANUAL, ATK+90% DEF+60% interval+0.4s.

Tests cover:
  - S2 config (name, sp_cost=50, initial_sp=30, duration=50s, MANUAL)
  - ATK buff applied on trigger
  - DEF buff applied on trigger
  - ATK interval increases (slower attacks) on trigger
  - All buffs cleared after skill ends
  - S1 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.asbest import (
    make_asbest, _S2_TAG, _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_INTERVAL_DELTA,
    _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_INTERVAL_BUFF_TAG, _S2_DURATION,
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


def test_asbest_s2_config():
    op = make_asbest(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Fire-Electric Mode"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 30
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_asbest(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)


def test_s2_def_buff_applied():
    w = _world()
    op = make_asbest(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S2_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S2_DEF_BUFF_TAG for b in op.buffs)


def test_s2_interval_increases():
    w = _world()
    op = make_asbest(slot="S2")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.current_atk_interval > base_interval, "Interval should increase (slower attacks)"
    assert any(b.source_tag == _S2_INTERVAL_BUFF_TAG for b in op.buffs)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_asbest(slot="S2")
    base_atk = op.effective_atk
    base_def = op.effective_def
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_INTERVAL_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
    assert op.effective_def == base_def
    assert abs(op.current_atk_interval - base_interval) < 1e-6


def test_s1_regression():
    op = make_asbest(slot="S1")
    assert op.skill is not None and op.skill.slot == "S1"
    assert op.skill.name == "Fortress Mode"

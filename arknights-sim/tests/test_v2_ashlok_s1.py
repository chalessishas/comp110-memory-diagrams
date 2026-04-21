"""Ashlok S1 "ATK Up γ" — 30s MANUAL, ATK+100%.
Ashlok S2 "Focused Bombardment" — 10s MANUAL, ATK+55% + interval-0.65s.

Tests cover:
  - S1 config (name, sp_cost=30, initial_sp=15, duration=30s, MANUAL)
  - S1 ATK buff applied on trigger
  - S1 ATK buff cleared after skill ends
  - S2 ATK buff applied on trigger
  - S2 interval buff reduces current_atk_interval
  - S2 buffs cleared after skill ends
  - Cross-slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.ashlok import (
    make_ashlok,
    _S1_TAG, _S1_ATK_RATIO, _S1_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_ATK_RATIO, _S2_ATK_BUFF_TAG, _S2_INTERVAL_BUFF_TAG, _S2_DURATION,
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


def test_ashlok_s1_config():
    op = make_ashlok(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "ATK Up γ"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_atk_buff_applied():
    w = _world()
    op = make_ashlok(slot="S1")
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
    op = make_ashlok(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


def test_ashlok_s2_config():
    op = make_ashlok(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Focused Bombardment"
    assert sk.sp_cost == 18
    assert sk.initial_sp == 10
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_ashlok(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)


def test_s2_interval_buff_applied():
    w = _world()
    op = make_ashlok(slot="S2")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.current_atk_interval < base_interval
    assert any(b.source_tag == _S2_INTERVAL_BUFF_TAG for b in op.buffs)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_ashlok(slot="S2")
    base_atk = op.effective_atk
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_INTERVAL_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
    assert abs(op.current_atk_interval - base_interval) < 1e-6


def test_s1_s2_regression():
    op_s1 = make_ashlok(slot="S1")
    assert op_s1.skill is not None and op_s1.skill.slot == "S1"
    op_s2 = make_ashlok(slot="S2")
    assert op_s2.skill is not None and op_s2.skill.slot == "S2"

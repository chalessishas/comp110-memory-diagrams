"""Platinum S2 "Pegasus Vision" — instant AUTO, ATK+100% ASPD−20 (permanent).

Tests cover:
  - S2 config (name, sp_cost=50, initial_sp=0, duration=0, AUTO)
  - ATK buff permanently applied after skill fires
  - ASPD penalty permanently applied after skill fires
  - Buffs persist after SP resets (no on_end called for instant skill)
  - S1 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.platnm import (
    make_platnm, _S2_TAG, _S2_ATK_RATIO, _S2_ASPD_DELTA,
    _S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG,
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


def test_platnm_s2_config():
    op = make_platnm(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Pegasus Vision"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 0
    assert sk.duration == 0.0
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_permanent():
    w = _world()
    op = make_platnm(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()  # AUTO fires when SP full

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)


def test_s2_aspd_penalty_permanent():
    w = _world()
    op = make_platnm(slot="S2")
    base_aspd = op.effective_aspd
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.effective_aspd == base_aspd + _S2_ASPD_DELTA  # negative delta = penalty
    assert any(b.source_tag == _S2_ASPD_BUFF_TAG for b in op.buffs)


def test_s2_buffs_persist_after_sp_reset():
    w = _world()
    op = make_platnm(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    # Tick for several more seconds — skill already consumed SP, buffs should remain
    for _ in range(int(TICK_RATE * 5.0)):
        w.tick()

    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)
    assert any(b.source_tag == _S2_ASPD_BUFF_TAG for b in op.buffs)


def test_s1_regression():
    op = make_platnm(slot="S1")
    assert op.skill is not None and op.skill.slot == "S1"
    assert op.skill.name == "ATK Up γ"
